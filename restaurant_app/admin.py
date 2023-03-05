from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.db.models import Count
from django.urls import reverse
from django.utils.html import format_html
from django.db import models

from .models.tables import Table, Booking
from .models.orders import Order, OrderItem
from .models.product import Product


class ActiveOrderFilter(admin.SimpleListFilter):
    title = _('active order')
    parameter_name = 'has_active_order'

    def lookups(self, request, model_admin):
        return (
            ('yes', _('Yes')),
            ('no', _('No')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.annotate(num_active_orders=Count('orders', filter=models.Q(orders__is_completed=False))).filter(num_active_orders__gt=0)
        if self.value() == 'no':
            return queryset.annotate(num_active_orders=Count('orders')).filter(num_active_orders=0)

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ['table_id', 'capacity', 'is_booked', 'are_guests_here', 'num_of_people', 'order_time', 'active_order_link']
    list_filter = [ActiveOrderFilter]  # <--- add the ActiveOrderFilter here

    def active_order_link(self, obj):
        active_order = obj.orders.filter(is_completed=False).first()
        if active_order:
            url = reverse("admin:restaurant_app_order_change", args=[active_order.id])
            return format_html('<a href="{}">{}</a>', url, active_order)
        else:
            return "-"

    active_order_link.short_description = "Active Order"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "active_order":
            kwargs["queryset"] = Order.objects.filter(table=request.obj, is_completed=False)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'table', 'user', 'reserved_date', 'reserved_time', 'num_of_people', 'are_guests_here', 'created_at', 'is_deleted']
    list_filter = ['is_deleted']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'product_name_rus', 'product_name_heb', 'product_price', 'category', 'quantity', 'created_at']
    list_filter = ['category']
    
    def get_product_names(self, obj):
        return f"{obj.product_name} ({obj.product_name_in_hebrew})"
    get_product_names.short_description = 'Product Names'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'product', 'quantity']

    
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'table', 'created_at', 'updated_at', 'is_completed')
    
  

