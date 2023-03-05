from django.shortcuts import render, redirect, reverse
from .forms import DeliveryCustomerForm
from .models import DeliveryCustomer

def add_delivery_customer_view(request, delivery_phone_number):
    if request.method == 'POST':
        form = DeliveryCustomerForm(request.POST)
        if form.is_valid():
            # check if a DeliveryCustomer object with the given phone number already exists
            customer_qs = DeliveryCustomer.objects.filter(delivery_phone_number=delivery_phone_number)
            if customer_qs.exists():
                # redirect to the delivery_menu view
                print("redirect to the delivery_menu view")
                return redirect(reverse('delivery_app:delivery_menu', args=[delivery_phone_number, 'Salads']))

            else:
                # create a new DeliveryCustomer object
                form.save()
                # redirect to the delivery_menu view
                print("redirect to the delivery_menu view")
                return redirect(reverse('delivery_app:delivery_menu', args=[delivery_phone_number, 'Salads']))
    else:
        print("delivery_phone_number")
        form = DeliveryCustomerForm(initial={'delivery_phone_number': delivery_phone_number})
    print("add_delivery_customer.html")
    return render(request, 'add_delivery_customer.html', {'form': form, 'delivery_phone_number': delivery_phone_number})
