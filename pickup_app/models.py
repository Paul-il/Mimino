from django.db import models
from datetime import datetime, timezone

from restaurant_app.models.product import Product


class PickupOrder(models.Model):
    phone = models.CharField(max_length=20)
    name = models.CharField(max_length=20)
    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_updated = models.DateTimeField(auto_now=True, editable=False)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.phone} ({self.name})"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.date_created = datetime.now(timezone.utc)
        self.date_updated = datetime.now(timezone.utc)
        return super().save(*args, **kwargs)


class Cart(models.Model):
    pickup_order = models.ForeignKey(PickupOrder, on_delete=models.CASCADE, related_name='carts')
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    def get_total(self):
        return sum([item.quantity * item.product.product_price for item in self.cart_items.all()])

    def save(self, *args, **kwargs):
        self.total_price = self.get_total()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Cart ({self.pk}) for {self.pickup_order.phone}"


class OrderItem(models.Model):
    order = models.ForeignKey(PickupOrder, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cart_items")
    pickup_order = models.ForeignKey(PickupOrder, on_delete=models.CASCADE, related_name='cart_items', null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.product_name_rus}"