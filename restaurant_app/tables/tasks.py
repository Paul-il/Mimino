from datetime import datetime, timedelta
from celery import shared_task
from restaurant_app.models.models import Table


@shared_task
def check_reserved_tables():
    # Получаем все забронированные столики, у которых время брони прошло
    reserved_tables = Table.objects.filter(is_booked=True, reserved_datetime__lt=datetime.now())

    for table in reserved_tables:
        # Если время брони прошло более чем на 30 минут и гости еще не пришли, освобождаем столик
        if datetime.now() - table.reserved_datetime > timedelta(minutes=30) and not table.are_guests_here:
            table.is_booked = False
            table.save()
