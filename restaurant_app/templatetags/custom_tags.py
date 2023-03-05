from django import template
from django.db.models import Sum
from restaurant_app.models.product import Product


register = template.Library()

@register.filter
def get_product_name_heb(product_id):
    return Product.objects.get(id=product_id).product_name_heb

@register.filter
def total_price(order):
    return sum(item.product.product_price * item.quantity for item in order.order_items.all())

@register.filter
def pickup_total_price(cart):
    return sum(item.quantity * item.product.product_price for item in cart.cart_items.all())


@register.filter
def delivery_total_price(cart):
    return sum(item.quantity * item.product.product_price for item in cart.delivery_cart_items.all())
