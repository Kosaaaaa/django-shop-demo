from .models import Order
from core.models import Customer


def get_or_set_order_session(request):
    order_id = request.session.get('order_id', None)

    if order_id is None:
        order = Order()
        order.save()
        request.session['order_id'] = order.id

    else:
        try:
            order = Order.objects.get(id=order_id, ordered=False)
        except Order.DoesNotExist:
            order = Order()
            order.save()
            request.session['order_id'] = order.id

    if request.user.is_authenticated and order.customer is None:
        order.customer = Customer.objects.get(user=request.user)
        order.save()
    # elif not request.user.is_authenticated and order.customer is None:
    #     print('anon')
    return order
