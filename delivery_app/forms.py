from django import forms
from django.core.validators import RegexValidator

from .models import DeliveryCustomer


class DeliveryForm(forms.Form):
    delivery_phone_number = forms.CharField(label='Номер телефона', validators=[RegexValidator(regex=r'^\d{10}$', message='Номер телефона должен содержать ровно 10 цифр')])


class DeliveryCustomerForm(forms.ModelForm):
    city = forms.ChoiceField(choices=[('חיפה', 'Хайфа'), ('נשר', ('Нэшер')), ('טירת כרמל', 'Тира'), ('כפר גלים', 'Кфар Галим'),('קריית חיים', 'Кирият Хаим'), ('קריית אתא', 'Кирият Ата'), ('קריית ביאליק', 'Кирият Биалик'), ('קריית ים', ('Кирият Ям'))], widget=forms.Select(attrs={'class': 'form-control', 'required': True}))

    class Meta:
        model = DeliveryCustomer
        fields = ['delivery_phone_number', 'name', 'city', 'street', 'house_number', 'floor', 'apartment_number', 'intercom_code']
        widgets = {
            'delivery_phone_number': forms.TextInput(attrs={'readonly': 'readonly'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'street': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'house_number': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'floor': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'apartment_number': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'intercom_code': forms.TextInput(attrs={'class': 'form-control'}),
        }



class ProductQuantityForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, max_value=100, initial=1, widget=forms.NumberInput(attrs={
        'class': 'form-control',
        'style': 'width: 100px; display: inline-block;'
    }))

