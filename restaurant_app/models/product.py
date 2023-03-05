from django.db import models
from django import forms


class Product(models.Model):
    CATEGORY_CHOICES = [
        ('first_dishes', 'first_dishes'),
        ('meat_dishes', 'meat_dishes'),
        ('bakery', 'bakery'),
        ('khinkali', 'khinkali'),
        ('khachapuri', 'khachapuri'),
        ('garnish', 'garnish'),
        ('grill_meat', 'grill_meat'),
        ('dessert', 'dessert'),
        ('soups', 'soups'),
        ('salads', 'salads'),
        ('drinks', 'drinks'),
        ('sales', 'sales'),
        ('delivery', 'delivery')
    ]

    id = models.AutoField(primary_key=True)
    product_name_rus = models.CharField(max_length=100, verbose_name='Название блюда (рус.)')
    product_name_heb = models.CharField(max_length=100, verbose_name='שם מנה (עברית)')
    product_price = models.DecimalField(max_digits=6, decimal_places=2)
    product_img = models.ImageField(upload_to='product_images/')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product_name_rus} ({self.product_price}₪)"

    
class ProductQuantityForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['quantity']


