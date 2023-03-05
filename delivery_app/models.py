from django.db import models
from datetime import datetime, timezone

from restaurant_app.models.product import Product


class DeliveryCustomer(models.Model):
    CITY_CHOICES = (
        ('חיפה', 'Хайфа'), 
        ('נשר', ('Нэшер')), 
        ('טירת כרמל', 'Тира'), 
        ('כפר גלים', 'Кфар Галим'),
        ('קריית חיים', 'Кирият Хаим'), 
        ('קריית אתא', 'Кирият Ата'), 
        ('קריית ביאליק', 'Кирият Биалик'), 
        ('קריית ים', ('Кирият Ям'))
    )
    delivery_phone_number = models.CharField(max_length=10)
    name = models.CharField(max_length=10)
    city = models.CharField(max_length=20, choices=CITY_CHOICES)
    street = models.CharField(max_length=10)
    house_number = models.CharField(max_length=10)
    floor = models.CharField(max_length=10)
    apartment_number = models.CharField(max_length=10)
    intercom_code = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.delivery_phone_number}"



class DeliveryOrder(models.Model):
    customer = models.ForeignKey(DeliveryCustomer, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_completed = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Delivery Order'
        verbose_name_plural = 'Delivery Orders'

    def __str__(self):
        return f"{self.pk} - {self.customer.name} ({self.customer.delivery_phone_number})"

class DeliveryProduct(models.Model):
    delivery_order = models.ForeignKey(DeliveryOrder, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Delivery Product'
        verbose_name_plural = 'Delivery Products'

    def __str__(self):
        return f'{self.product.product_name_rus} ({self.quantity})'


class Cart(models.Model):
    delivery_order = models.ForeignKey(DeliveryOrder, on_delete=models.CASCADE, related_name='delivery_carts')
    customer = models.ForeignKey(DeliveryCustomer, on_delete=models.CASCADE) # added foreign key to DeliveryCustomer model
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    def get_total(self):
        return sum([item.quantity * item.product.product_price for item in self.delivery_cart_items.all()])

    def save(self, *args, **kwargs):
        self.total_price = self.get_total()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Cart ({self.pk}) for delivery order {self.delivery_order.delivery_phone_number}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='delivery_cart_items')
    delivery_order = models.ForeignKey(DeliveryOrder, on_delete=models.CASCADE, related_name='delivery_cart_items', null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='delivery_product')
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.product_name_rus}"


