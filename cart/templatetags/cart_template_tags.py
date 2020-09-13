from itertools import product
from django import template
from requests.api import request
from cart.utils import get_or_set_order_session
from django.utils.html import format_html

register = template.Library()


@register.filter
def cart_item_count(request):
    order = get_or_set_order_session(request)
    count = order.items.count()
    return count


@register.simple_tag
def product_image_to_html(product, request):
    return format_html(f'<img src="{request.scheme}://{request.META.get("HTTP_HOST")}{ product.imageURL }" alt="{product.image_alt_text}" class="img-fluid" />')
