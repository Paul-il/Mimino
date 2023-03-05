from django import forms

from .models import PickupOrder
from restaurant_app.models.orders import OrderItem

class PickupForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PickupForm, self).__init__(*args, **kwargs)
        self.fields['name'].required = False

    class Meta:
        model = PickupOrder
        fields = ['phone', 'name']
        labels = {
            'phone': 'Номер телефона',
            'name': 'Имя',
        }

class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'phone_number']


class ProductQuantityForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, max_value=100, initial=1, widget=forms.NumberInput(attrs={
        'class': 'form-control',
        'style': 'width: 100px; display: inline-block;'
    }))