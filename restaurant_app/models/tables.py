from django.db import models
from django.contrib.auth.models import User
from django import forms


class Table(models.Model):
    table_id = models.IntegerField()
    description = models.TextField(null=True, blank=True)
    is_booked = models.BooleanField(default=False)
    is_ordered = models.BooleanField(default=False)
    reserved_date = models.DateField(null=True, blank=True)
    reserved_time = models.TimeField(null=True, blank=True)
    num_of_people = models.IntegerField(null=True, blank=True)
    order_time = models.DateTimeField(null=True, blank=True)
    are_guests_here = models.BooleanField(default=False)
    capacity = models.IntegerField()
    active_order = models.BooleanField(default=False)

    def __str__(self):
        return f'Table {self.table_id}'

    def orders(self):
        from .orders import Order
        return Order.objects.filter(table=self)

    class Meta:
        ordering = ['table_id']


class Booking(models.Model):
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name='bookings')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    reserved_date = models.DateField()
    reserved_time = models.TimeField()
    num_of_people = models.IntegerField()
    are_guests_here = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Бронирование {self.id} - стол {self.table.table_id} ({self.reserved_date} {self.reserved_time} {self.user})"
        
class GuestsHereForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['are_guests_here']
        widgets = {'are_guests_here': forms.HiddenInput()}
