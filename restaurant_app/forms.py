from django import forms
from django.forms import CheckboxSelectMultiple
from .models.tables import Table, Booking
from .models.orders import Order, OrderItem

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ('table', 'num_of_people', 'reserved_date', 'reserved_time', 'are_guests_here', 'description', 'user')
        widgets = {
            'user': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.fields['table'].queryset = Table.objects.filter(is_booked=False)
        self.fields['description'].required = False

    def save(self, commit=True):
        booking = super().save(commit=False)
        booking.user = self.request.user
        if commit:
            booking.save()
        return booking

class GuestsHereForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['are_guests_here']
        widgets = {'are_guests_here': forms.HiddenInput()}

"""class GuestsHereForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['are_guests_here']
        labels = {'are_guests_here': 'Подтвердить, что гости пришли'}
        widgets = {
            'are_guests_here': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }"""

class OrderForm(forms.ModelForm):
    PAYMENT_CHOICES = (
        ('cash', 'Наличные'),
        ('card', 'Кредитная карта'),
    )

    payment_method = forms.MultipleChoiceField(widget=CheckboxSelectMultiple, choices=PAYMENT_CHOICES)

    class Meta:
        model = Order
        fields = ['payment_method']

    
class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']

class ProductQuantityForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, max_value=100, initial=1, widget=forms.NumberInput(attrs={
        'class': 'form-control',
        'style': 'width: 100px; display: inline-block;'
    }))