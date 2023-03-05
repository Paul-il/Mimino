from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Sum, F
from django.http import JsonResponse
from .models import DeliveryCustomer, DeliveryOrder, Cart, CartItem, Product
from .forms import ProductQuantityForm

def delivery_cart_view(request, delivery_phone_number):
    delivery_customer = get_object_or_404(DeliveryCustomer, delivery_phone_number=delivery_phone_number)
    delivery_order = DeliveryOrder.objects.filter(customer=delivery_customer, is_completed=False).first()
    customer_name = delivery_customer.name 
    
    if not delivery_order:
        return redirect('delivery_app:delivery_menu', delivery_phone_number=delivery_phone_number, category='Salads')

    cart, created = Cart.objects.get_or_create(delivery_order=delivery_order)
    cart_items = cart.delivery_cart_items.all()

    context = {
        'delivery_phone_number': delivery_phone_number,
        'delivery_order': delivery_order,
        'customer_name': customer_name,
        'cart_items': cart_items,
        'cart': cart,
    }

    return render(request, 'delivery_cart.html', context)

def delivery_add_to_cart_view(request, delivery_phone_number):
    print("delivery_add_to_cart_view")
    delivery_customer = get_object_or_404(DeliveryCustomer, delivery_phone_number=delivery_phone_number)
    delivery_order = DeliveryOrder.objects.filter(customer=delivery_customer, is_completed=False).first()

    product_id = request.POST.get('product_id')
    quantity = request.POST.get('quantity')

    if not product_id or not quantity:
        return JsonResponse({'error': 'Bad request'}, status=400)

    product = get_object_or_404(Product, id=product_id)
    cart = delivery_order.delivery_carts.first()

    if cart:
        cart_item = cart.delivery_cart_items.filter(product=product).first()
        if cart_item:
            cart_item.quantity += int(quantity)
            cart_item.save()
        else:
            cart_item = CartItem.objects.create(product=product, quantity=quantity, cart=cart)
    else:
        cart = Cart.objects.create(customer=delivery_customer, delivery_order=delivery_order)
        cart_item = CartItem.objects.create(product=product, quantity=quantity, cart=cart)

    messages.success(request, f"{quantity} {product.product_name_rus} добавлено в корзину!")
    return redirect('delivery_app:delivery_menu', delivery_phone_number=delivery_phone_number, category="Salads")

def delivery_increase_product_view(request, delivery_phone_number, product_id):
    delivery_order = get_object_or_404(DeliveryOrder, customer__delivery_phone_number=delivery_phone_number)
    cart = Cart.objects.get(delivery_order=delivery_order)
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    form = ProductQuantityForm(instance=cart_item.product)
    return render(request, 'delivery_cart_item.html', {'cart_item': cart_item, 'form': form})

def delivery_decrease_product_view(request, delivery_phone_number, product_id):
    delivery_order = get_object_or_404(DeliveryOrder, customer__delivery_phone_number=delivery_phone_number)
    product = get_object_or_404(Product, id=product_id)
    cart = Cart.objects.get(delivery_order=delivery_order)
    cart_item = cart.delivery_cart_items.get(product=product)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return JsonResponse('quantity')

def delivery_remove_product_view(request, delivery_phone_number, product_id):
    delivery_customer = get_object_or_404(DeliveryCustomer, delivery_phone_number=delivery_phone_number)
    delivery_order = DeliveryOrder.objects.filter(customer=delivery_customer, is_completed=False).first()
    cart_item = get_object_or_404(CartItem, cart=delivery_order.delivery_carts.first(), product_id=product_id)
    cart_item.delete()
    messages.success(request, f"{cart_item.product.product_name_rus} удалено из корзины")
    return redirect('delivery_app:delivery_cart', delivery_phone_number=delivery_phone_number)
