from django.shortcuts import render, get_object_or_404, redirect

from restaurant_app.models.product import Product
from .models import DeliveryCustomer, DeliveryOrder, Cart, CartItem
from .forms import ProductQuantityForm



def delivery_menu_view(request, delivery_phone_number, category):
    delivery_customer = get_object_or_404(DeliveryCustomer, delivery_phone_number=delivery_phone_number)
    delivery_order, created = DeliveryOrder.objects.get_or_create(customer=delivery_customer, is_completed=False)
    products = Product.objects.filter(category=category)
    product_quantity_form = ProductQuantityForm()

    context = {
        'delivery_phone_number': delivery_phone_number,
        'category': category,
        'products': products,
        'product_quantity_form': product_quantity_form,
    }

    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity'))
        product = get_object_or_404(Product, id=product_id)

        cart, created = Cart.objects.get_or_create(delivery_order=delivery_order)

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        else:
            cart_item.quantity = quantity
            cart_item.save()

        return redirect('delivery_app:delivery_cart', delivery_phone_number=delivery_phone_number)


    return render(request, 'delivery_menu.html', context)

