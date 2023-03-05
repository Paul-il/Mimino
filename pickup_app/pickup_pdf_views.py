from django.template.loader import get_template
from weasyprint.fonts import FontConfiguration
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from datetime import datetime
from io import BytesIO
from weasyprint import HTML
import os
import traceback

from .models import PickupOrder


@login_required
def pickup_generate_pdf_view(request, phone_number, order_id):
    print("pickup_generate_pdf_view")
    try:
        # Get order data from database
        order = get_object_or_404(PickupOrder, phone=phone_number)
        print(order)
        # Get payment method from request data
        payment_method = request.POST.get('payment_method')
        pay_button_value = request.POST.get('pay-button')

        # Get all cart items in the order
        cart_items = []
        for cart in order.carts.all():
            for item in cart.cart_items.all():
                cart_items.append(item)

        # Calculate the total price of the order
        total_price = sum(item.quantity * item.product.product_price for item in cart_items)

        # Render the HTML template with the order data
        template = get_template('pickup_pdf_template.html')
        context = {
            'order': order,
            'cart_items': cart_items,
            'payment_method': payment_method,
            'total_price': total_price,
        }
        html = template.render(context)
        font_config = FontConfiguration()

        # Convert the HTML to a PDF using weasyprint
        pdf_file = BytesIO()
        HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(
            pdf_file,
            font_config=font_config,
        )
        pdf_file.seek(0)

        # Save the PDF to a file with a unique filename
        print(payment_method)
        today = datetime.now().strftime('%Y-%m-%d')
        directory = os.path.join('pdfs', today)
        if payment_method == 'מזומן':
            cash_directory = os.path.join(directory, 'cash')
            os.makedirs(cash_directory, exist_ok=True)
            filename = f'_Phone:({phone_number})___{today}___{payment_method}.pdf'
            filepath = os.path.join(cash_directory, filename)
        elif payment_method == 'כרטיס אשראי':
            cc_directory = os.path.join(directory, 'credit_card')
            os.makedirs(cc_directory, exist_ok=True)
            filename = f'_Phone:({phone_number})___{today}___{payment_method}.pdf'
            filepath = os.path.join(cc_directory, filename)
        else:
            none_directory = os.path.join(directory, 'none')
            os.makedirs(none_directory, exist_ok=True)
            filename = f'_Phone:({phone_number})___{today}___{payment_method}.pdf'
            filepath = os.path.join(none_directory, filename)

        with open(filepath, 'wb') as f:
            f.write(pdf_file.read())

        # Delete Order if the bill was paid
        if pay_button_value:
            order.delete()
            return JsonResponse({'thank': "You."})

        return JsonResponse({'Bill': "Printed."})

    except Exception as e:
        traceback.print_exc()
        error_message = f"An error occurred while generating the PDF: {str(e)}"
        return HttpResponse(error_message, content_type='text/plain', status=500)


