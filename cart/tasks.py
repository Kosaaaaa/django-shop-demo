from celery import task
from django.core.mail import send_mail
from .models import Order
from django.conf import settings

# TODO send mail order created
# @task
# def order_payment_success(order_id):
#     order = Order.objects.get(id=order_id)
#     subject = f'Zamówienie nr {order.reference_number} zostało złożne'
#     message = f'Cześć, {}! \n\n Złożyłeś zamówienie w naszym sklepie.\n Identyfikator zamówienia to {order.reference_number}'

#     mail_sent = send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, order.email)
# order_payment_success.delay(order_id)
