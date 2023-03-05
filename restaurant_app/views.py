from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

from .models.tables import Table, Booking
from .models.orders import Order, OrderItem
from .models.product import Product

from .forms import GuestsHereForm, OrderForm, BookingForm, OrderItemForm, ProductQuantityForm
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.utils import timezone
import os

from weasyprint.fonts import FontConfiguration
from weasyprint import HTML
from datetime import datetime
from io import BytesIO
from django.http import JsonResponse
from django.db.models import Sum, F
from django.template.loader import get_template
from django.http import HttpResponse

def login_page_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('ask_where')
        else:
            return render(request, 'index.html', {'error': 'Invalid login credentials'})
    else:
        return render(request, 'index.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def ask_where_view(request):
    if request.user.is_authenticated:
        return render(request, 'ask_where.html')
    else:
        return redirect('login')

@login_required
def tables_view(request):
    tables = Table.objects.all()

    for table in tables:
        if table.orders.filter(is_completed=False).exists():
            table.active_order = True
        else:
            table.active_order = False

    context = {'tables': tables}
    return render(request, 'tables.html', context)


########################################################################################

@login_required
def book_table_view(request, table_id):
    table = get_object_or_404(Table, table_id=table_id)
    if request.method == 'POST':
        form = BookingForm(request.POST, request=request)
        if form.is_valid():
            form.save()
            return redirect('tables')
    else:
        form = BookingForm(request=request)
    return render(request, 'book_table.html', {'table': table, 'form': form})



@login_required
def bookings_view(request):
    bookings = Booking.objects.all()
    context = {'bookings': bookings}
    return render(request, 'bookings.html', context)

@login_required
def guests_here_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if request.method == 'POST':
        form = GuestsHereForm(request.POST, instance=booking)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.are_guests_here = not booking.are_guests_here
            booking.user = request.user
            if booking.are_guests_here:
                booking.table.is_booked = False
                booking.table.are_guests_here = True
                booking.table.save()
                booking.is_deleted = True
            booking.save()
            messages.success(request, 'Статус гостей обновлен.')
            return redirect('bookings')
    else:
        form = GuestsHereForm(instance=booking, initial={'are_guests_here': booking.are_guests_here})
    return render(request, 'guests_here.html', {'form': form, 'booking': booking})

@login_required
def menu_view(request, table_id, category):
    # If the table_id starts with "pickup-", extract the pickup order ID from the string

    table = get_object_or_404(Table, table_id=table_id)
    product_quantity_form = ProductQuantityForm()
    # Get the active order for the table or the pickup order

    active_order = table.orders.filter(is_completed=False).first()

    # Get the category filter from the query parameters or use the default value
    category = request.GET.get('category', 'all')

    # Get the products for the selected category

    products = Product.objects.filter(category=category)

    # Get the order ID from the query parameters
    order_id = request.GET.get('order_id')

    # Define the context for the template
    context = {
        'table': table,
        'active_order': active_order,
        'products': products,
        'category': category,
        'order_id': order_id,
        'product_quantity_form': product_quantity_form,
    }

    # If the request is a POST request, add the new order item to the cart
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = request.POST.get('quantity')
        product = get_object_or_404(Product, pk=product_id)
        
        if active_order:
            # Add the product to the existing active order
            order_item, created = OrderItem.objects.get_or_create(order=active_order, product=product)
            order_item.quantity += int(quantity)
            order_item.save()
        else:
            # Create a new active order and add the product to it
            active_order = Order.objects.create(table=table)
            order_item = OrderItem.objects.create(order=active_order, product=product, quantity=int(quantity))

        # Set the context variable for the active order after the update
        context['active_order'] = active_order

    # Create a form to update the are_guests_here field for the active booking
    booking = table.bookings.filter(are_guests_here=False, is_deleted=False).first() if table else None
    guests_here_form = None
    if booking:
        guests_here_form = GuestsHereForm(instance=booking)


    if table:
        context['order_id'] = f'{table_id}?order_id={request.GET.get("order_id")}&category={category}'

    # Add the context variable for the form to update the guests_here field
    context['guests_here_form'] = guests_here_form

    # Add the context variable for the form to add a new order item
    context['order_item_form'] = OrderItemForm()

    # Render the menu page with the selected products and other data
    return render(request, 'menu.html', context=context)


@login_required
def table_order_view(request, table_id):
    table = get_object_or_404(Table, table_id=table_id)
    active_order = table.get_active_order()

    if active_order is None:
        order = Order(table=table)
        order.save()
    else:
        order = active_order

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            product_id = form.cleaned_data['product']
            quantity = form.cleaned_data['quantity']
            order.add_to_cart(product_id, quantity)
            order.save()
            return redirect('menu', table_id=table_id)
    else:
        form = OrderForm()

    if active_order is not None:
        active_order_items = active_order.order_items.all()
        active_order_total = active_order.get_total_price()
    else:
        active_order_items = None
        active_order_total = 0

    return render(request, 'table_order.html', {
        'table': table,
        'form': form,
        'active_order': order,
        'active_order_items': active_order_items,
        'active_order_total': active_order_total,
    })

def start_order_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.order_time = timezone.now()  # Update order_time field to current time
    order.save()
    return redirect('order_detail', order_id=order_id)


def order_detail_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order_items = order.order_items.annotate(total_price=F('quantity') * F('product__product_price'))
    total_price = order_items.aggregate(Sum('total_price'))['total_price__sum']

    if request.method == 'POST':
        # Update order with payment information
        payment_method = request.POST.get('payment_method')
        order.payment_method = payment_method
        order.paid = True
        order.save()
        

        # Clear the table associated with the order
        order.table.is_available = True
        order.table.save()

        return redirect('order_confirmation', order_id=order.id)

    return render(request, 'order_detail.html', {'order': order, 'order_items': order_items, 'total_price': total_price})

def add_to_cart_view(request, table_id):
    # Get the current cart from the session, or create a new empty cart if it doesn't exist
    cart = request.session.get('cart', [])

    # Get the table and its active order
    table = get_object_or_404(Table, table_id=table_id)
    active_order = table.orders.filter(is_completed=False).first()

    if request.method == 'POST':
        # If the form has been submitted, get the product ID from the form data and add it to the cart
        product_id = request.POST.get('product_id')
        if product_id:
            # If there is an active order, check if the product is already in the order
            if active_order:
                product = get_object_or_404(Product, pk=product_id)
                order_item = active_order.order_items.filter(product=product).first()

                # If the product is already in the order, increase the quantity
                if order_item:
                    order_item.quantity += 1
                    order_item.save()
                # If the product is not in the order, add it to the order
                else:
                    OrderItem.objects.create(order=active_order, product=product)

                # Update the session to store the new cart
                cart.append(product_id)
                request.session['cart'] = cart

            # If there is no active order, create a new one and add the product to it
            else:
                new_order = Order.objects.create(table=table)
                product = get_object_or_404(Product, pk=product_id)
                OrderItem.objects.create(order=new_order, product=product)

                # Update the session to store the new cart
                cart.append(product_id)
                request.session['cart'] = cart

            # Redirect back to the menu page to prevent the form from being resubmitted
            if table_id:
                return redirect(reverse('menu', kwargs={'table_id': table_id}))
            else:
                return redirect('pickup')

    # If the request is not a POST request, redirect back to the menu page
    if table_id:
        return redirect(reverse('menu', kwargs={'table_id': table_id}))
    else:
        return redirect('pickup')

############################ ADD_DELETE ##################################

def increase_product_in_order_view(request, order_id, order_item_id):
    order_item = get_object_or_404(OrderItem, id=order_item_id)
    order_item.quantity += 1
    order_item.save()
    order_items = order_item.order.order_items.annotate(total_price=F('quantity') * F('product__product_price'))
    total_price = order_items.aggregate(Sum('total_price'))['total_price__sum']
    response_data = {
        order_item.quantity,
        total_price,
    }
    return JsonResponse(response_data)

def decrease_product_from_order_view(request, order_id, order_item_id):
    order_item = get_object_or_404(OrderItem, id=order_item_id)
    order = order_item.order
    order_item.quantity = F('quantity') - 1
    order_item.save()
    if order_item.quantity == 0:
        order_item.delete()
        removed = True
    else:
        removed = False
    order_items = order.order_items.annotate(total_price=F('quantity') * F('product__product_price'))
    total_price = order_items.aggregate(Sum('total_price'))['total_price__sum']
    response_data = {
        'quantity': order_item.quantity,
        'total_price': total_price,
        'removed': removed,
    }
    return JsonResponse(response_data)

def delete_product_from_order_view(request, order_id, order_item_id):
    order_item = get_object_or_404(OrderItem, id=order_item_id)
    order = order_item.order
    order_item.delete()
    messages.success(request, f"{order_item.product.product_name_rus} удалено из корзины")
    order_items = order.order_items.annotate(total_price=F('quantity') * F('product__product_price'))
    total_price = order_items.aggregate(Sum('total_price'))['total_price__sum']
    response_data = {total_price, order_items.count()}
    return JsonResponse(response_data)


def get_order_item_quantity_view(request, order_id, order_item_id):
    order_item = OrderItem.objects.get(order__id=order_id, id=order_item_id)
    data = {order_item.quantity}
    return JsonResponse(data, safe=False)

def remove_empty_order_items():
    empty_order_items = OrderItem.objects.filter(quantity=0)
    empty_order_items.delete()

def pay_order_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    print(order.id)
    #generate_pdf_view(request,order.id)
    order.payment_method = request.POST.get('payment_method')
    order.paid = True
    order.is_completed = True  # Mark the order as completed
    order.save()
    return redirect('tables')

############################ PDF ##################################


def generate_pdf_view(request, order_id):
    try:
        # Get order data from database
        order = Order.objects.get(id=order_id)

        # Get payment method from request data
        payment_method = request.POST.get('payment_method')
        pay_button_value = request.POST.get('pay-button')
        
        # Calculate the total price of the order
        total_price = sum(
            order_item.quantity * order_item.product.product_price
            for order_item in order.order_items.all()
        )

        # Render the HTML template with the order data
        template = get_template('pdf_template.html')
        html = template.render({'order': order, 'payment_method': payment_method, 'total_price': total_price})
        font_config = FontConfiguration()

        # Convert the HTML to a PDF using weasyprint
        pdf_file = BytesIO()
        HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(
            pdf_file,
            font_config=font_config,
        )
        pdf_file.seek(0)

        # Save the PDF to a file with a unique filename
        table_number = order.table.table_id
        today = datetime.now().strftime('%Y-%m-%d')
        directory = os.path.join('pdfs', today)
        if payment_method == 'מזומן':
            cash_directory = os.path.join(directory, 'cash')
            os.makedirs(cash_directory, exist_ok=True)
            filename = f'_TableNumber({table_number})___{today}___{payment_method}.pdf'
            filepath = os.path.join(cash_directory, filename)
        elif payment_method == 'כרטיס אשראי':
            cc_directory = os.path.join(directory, 'credit_card')
            os.makedirs(cc_directory, exist_ok=True)
            filename = f'_TableNumber({table_number})___{today}___{payment_method}.pdf'
            filepath = os.path.join(cc_directory, filename)
        else:
            none_directory = os.path.join(directory, 'none')
            os.makedirs(none_directory, exist_ok=True)
            filename = f'_TableNumber({table_number})___{today}___{payment_method}.pdf'
            filepath = os.path.join(none_directory, filename)

        with open(filepath, 'wb') as f:
            f.write(pdf_file.read())
        print(pay_button_value)
        # Delete Order if the bill was paid
        if pay_button_value:
            order.delete()

        return JsonResponse({'thank': "You."})
    
    except Exception as e:
        error_message = f"An error occurred while generating the PDF: {str(e)}"
        return HttpResponse(error_message, content_type='text/plain', status=500)





def generate_pdf_view1(request, order_id):
    print("generate_pdf_view1")
    try:
        # Get order data from database
        order = Order.objects.get(id=order_id)

        # Get payment method from request data
        payment_method = request.POST.get('payment_method')
        bill = request.POST.get('bill')
        print(bill)

        # Calculate the total price of the order
        total_price = sum(
            order_item.quantity * order_item.product.product_price
            for order_item in order.order_items.all()
        )

        # Render the HTML template with the order data
        template = get_template('pdf_template.html')
        html = template.render({'order': order, 'payment_method': payment_method, 'total_price': total_price, 'bill': bill})
        font_config = FontConfiguration()

        # Convert the HTML to a PDF using weasyprint
        pdf_file = BytesIO()
        HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(
            pdf_file,
            font_config=font_config,
        )
        pdf_file.seek(0)

        # Save the PDF to a file with a unique filename
        table_number = order.table.table_id
        today = datetime.now().strftime('%Y-%m-%d')
        directory = os.path.join('pdfs', today)
        if payment_method == 'מזומן':
            cash_directory = os.path.join(directory, 'cash')
            os.makedirs(cash_directory, exist_ok=True)
            filename = f'_TableNumber({table_number})___{today}___{payment_method}.pdf'
            filepath = os.path.join(cash_directory, filename)
        elif payment_method == 'כרטיס אשראי':
            cc_directory = os.path.join(directory, 'credit_card')
            os.makedirs(cc_directory, exist_ok=True)
            filename = f'_TableNumber({table_number})___{today}___{payment_method}.pdf'
            filepath = os.path.join(cc_directory, filename)
        else:
            none_directory = os.path.join(directory, 'none')
            os.makedirs(none_directory, exist_ok=True)
            filename = f'_TableNumber({table_number})___{today}___{payment_method}.pdf'
            filepath = os.path.join(none_directory, filename)

        with open(filepath, 'wb') as f:
            f.write(pdf_file.read())


        return JsonResponse({'thank': "You."})
    
    except Exception as e:
        error_message = f"An error occurred while generating the PDF: {str(e)}"
        return HttpResponse(error_message, content_type='text/plain', status=500)