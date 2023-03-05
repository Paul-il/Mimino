from .forms import PickupForm
from .models import PickupOrder
from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required

@login_required
@login_required
def pickup_create_view(request):
    if request.method == 'POST':
        form = PickupForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data['phone']
            name = form.cleaned_data.get('name', None) # получаем имя из формы
            # проверяем, есть ли номер в базе данных
            pickup_order = PickupOrder.objects.filter(phone=phone_number).first()
            if pickup_order:
                return redirect('pickup_app:pickup_menu', phone_number=phone_number, category='Salads')
            else:
                # создаем объект заказа
                pickup_order = PickupOrder(phone=phone_number, name=name) # сохраняем имя в базу, если есть
                pickup_order.save()
                return redirect('pickup_app:pickup_menu', phone_number=phone_number, category='Salads')
    else:
        form = PickupForm()
    context = {
        'form': form,

    }
    return render(request, 'pickup_create.html', context)
