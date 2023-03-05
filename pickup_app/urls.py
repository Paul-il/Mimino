from django.urls import path

from pickup_app.pickup_create_views import pickup_create_view
from pickup_app.pickup_menu_views import pickup_menu_view
from pickup_app.pickup_pdf_views import pickup_generate_pdf_view
from pickup_app.pickup_cart_views import (
    pickup_cart_view, 
    pickup_add_to_cart_view, 
    pickup_remove_product_view,
    pickup_increase_product_view,
    pickup_decrease_product_view,
    pickup_total_price_view
                                          
)


app_name = 'pickup_app'

urlpatterns = [
    path('', pickup_create_view, name='pickup_create'),
    path('pickup_cart/<str:phone_number>/', pickup_cart_view, name='pickup_cart'),
    path('pickup_menu/<str:phone_number>/<str:category>/', pickup_menu_view, name='pickup_menu'),
    path('pickup_total_price/<str:phone_number>/', pickup_total_price_view, name='pickup_total_price'),
    path('pickup_add_to_cart/<str:phone_number>/<int:product_id>/', pickup_add_to_cart_view, name='pickup_add_to_cart'),
    path('pickup_generate_pdf/<str:phone_number>/<int:order_id>/', pickup_generate_pdf_view, name='pickup_generate_pdf'),
    path('pickup_remove_product/<str:phone_number>/<int:product_id>/', pickup_remove_product_view, name='pickup_remove_product'), 
    path('pickup_increase_product/<str:phone_number>/<int:product_id>/', pickup_increase_product_view, name='pickup_increase_product'),
    path('pickup_decrease_product/<str:phone_number>/<int:product_id>/', pickup_decrease_product_view, name='pickup_decrease_product'),
       
    
]