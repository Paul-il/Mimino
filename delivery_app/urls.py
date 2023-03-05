from django.urls import path

from .delivery_views import delivery_view
from .check_delivery_customer_views import check_delivery_customer_view
from .add_delivery_customer_views import add_delivery_customer_view
from .delivery_menu_views import delivery_menu_view
from .delivery_pdf_views import delivery_generate_pdf_view
from .delivery_cart_views import (
    delivery_add_to_cart_view, 
    delivery_cart_view,
    delivery_increase_product_view,
    delivery_decrease_product_view,
    delivery_remove_product_view,
     )

app_name = 'delivery_app'


urlpatterns = [
    path('check_delivery_number', delivery_view, name='check_delivery_number'),
    path('add_delivery_customer/<str:delivery_phone_number>/', add_delivery_customer_view, name='add_delivery_customer'),
    path('check_delivery_customer/<str:delivery_phone_number>/', check_delivery_customer_view, name='check_delivery_customer'),
    path('delivery_add_to_cart/<str:delivery_phone_number>/', delivery_add_to_cart_view, name='delivery_add_to_cart'),
    path('delivery_menu/<str:delivery_phone_number>/<str:category>/', delivery_menu_view, name='delivery_menu'),

    path('cart/<str:delivery_phone_number>/', delivery_cart_view, name='delivery_cart'),
    path('cart/<str:delivery_phone_number>/increase/<int:product_id>/', delivery_increase_product_view, name='delivery_increase_product'),
    path('cart/<str:delivery_phone_number>/decrease/<int:product_id>/', delivery_decrease_product_view, name='delivery_decrease_product'),
    path('cart/<str:delivery_phone_number>/remove/<int:product_id>/', delivery_remove_product_view, name='delivery_remove_product'),
    path('cart/<str:delivery_phone_number>/<int:order_id>/pdf/', delivery_generate_pdf_view, name='delivery_generate_pdf'),

]
