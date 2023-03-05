from django.contrib import admin

from .models import PickupOrder, Cart, CartItem

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1

class CartInline(admin.TabularInline):
    model = Cart
    extra = 0
    inlines = [CartItemInline]

class PickupOrderAdmin(admin.ModelAdmin):
    inlines = [CartItemInline]
    list_display = ('phone', 'name')
    readonly_fields = ('get_order_items_display', 'get_cart_items_display', 'get_cart_total')

    def get_order_items_display(self, obj):
        items = obj.get_order_items()
        return "\n".join([f"{item.product} ({item.quantity})" for item in items])
    get_order_items_display.short_description = 'Order Items'

    def get_cart_items_display(self, obj):
        items = []
        carts = obj.carts.all()
        for cart in carts:
            items.extend([f"{cart_item.product} ({cart_item.quantity})" for cart_item in cart.cart_items.all()])
        return "\n".join(items)
    get_cart_items_display.short_description = 'Cart Items'
    
    def get_cart_total(self, obj):
        total = 0
        carts = obj.carts.all()
        for cart in carts:
            total += cart.total_price
        return total

    get_cart_total.short_description = 'Total'

    


admin.site.register(PickupOrder, PickupOrderAdmin)

