from restaurant_app.models.product import Product
from .forms import ProductQuantityForm
from .models import PickupOrder, Cart, CartItem
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

@login_required
def pickup_menu_view(request, phone_number, category):
    products = Product.objects.filter(category=category)
    pickup_order = get_object_or_404(PickupOrder, phone=phone_number)
    product_quantity_form = ProductQuantityForm()
    context = {
        'phone_number': phone_number,
        'products': products,
        'category': category,
        'pickup_order': pickup_order,
        'product_quantity_form': product_quantity_form,
    }
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity'))
        product = get_object_or_404(Product, id=product_id)

        cart, created = Cart.objects.get_or_create(pickup_order=pickup_order)

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        else:
            cart_item.quantity = quantity
            cart_item.save()

        return redirect('pickup_app:pickup_cart', phone_number=phone_number)

    return render(request, 'pickup_menu.html', context)
