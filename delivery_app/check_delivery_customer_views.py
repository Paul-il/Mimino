from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import DeliveryCustomer

@login_required
def check_delivery_customer_view(request, delivery_phone_number):
    customer = get_object_or_404(DeliveryCustomer, delivery_phone_number=delivery_phone_number)
    return render(request, 'check_delivery_customer.html', {'customer': customer, 'delivery_phone_number': delivery_phone_number})
