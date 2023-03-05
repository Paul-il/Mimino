from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .tables import Table
from .product import Product


class Order(models.Model):
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_completed = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=50, null=True, blank=True)
    is_completed = models.BooleanField(default=False)

    class Status(models.TextChoices):
        ACTIVE = 'active', _('Active')
        COMPLETED = 'completed', _('Completed')
        CANCELED = 'canceled', _('Canceled')

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )

    class PaymentMethod(models.TextChoices):
        CASH = 'cash', _('Cash')
        CARD = 'card', _('Card')

    payment_method = models.CharField(
        max_length=10,
        choices=PaymentMethod.choices,
        null=True,
        blank=True,
    )
    
    def __str__(self):
        return f"Order {self.pk} ({self.table})"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField(_('quantity'), default=1)
    phone_number = models.CharField(max_length=10)

    class Meta:
        unique_together = ('order', 'product')

    @classmethod
    def remove_zero_quantity_products(cls):
        products = OrderItem.objects.filter(quantity=0)
        for product in products:
            product.delete()
