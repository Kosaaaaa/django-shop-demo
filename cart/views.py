from django.http import HttpResponse
import datetime
import json
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.http import request
from django.shortcuts import get_object_or_404, reverse, redirect
from django.utils import timezone
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from .forms import (AddToCartForm, AddressForm, CouponForm,)
from .models import (Coupon, Product, OrderItem,
                     Address, Payment, Order, Category)
from core.models import Customer
from .utils import get_or_set_order_session


class ProductListView(generic.ListView):
    template_name = 'cart/product_list.html'

    def get_queryset(self):
        qs = Product.objects.filter(active=True)
        category = self.request.GET.get('category', None)
        if category:
            qs = qs.filter(Q(primary_category__name=category) | Q(
                secondary_categories__name=category)).distinct()
        return qs

    def get_context_data(self, **kwargs):
        context = super(ProductListView, self).get_context_data(**kwargs)
        context.update({
            "categories": Category.objects.values("name")
        })
        return context


class ProductDetailView(generic.FormView):
    template_name = 'cart/product_detail.html'
    form_class = AddToCartForm

    def get_object(self):
        return get_object_or_404(Product, slug=self.kwargs["slug"])

    def get_success_url(self):
        return reverse("cart:summary")

    def get_form_kwargs(self):
        kwargs = super(ProductDetailView, self).get_form_kwargs()
        kwargs["product_id"] = self.get_object().id
        return kwargs

    def form_valid(self, form):
        order = get_or_set_order_session(self.request)
        product = self.get_object()

        item_filter = order.items.filter(
            product=product,
            size=form.cleaned_data['size'],
        )

        if item_filter.exists():
            item = item_filter.first()
            item.quantity += int(form.cleaned_data['quantity'])
            item.save()

        else:
            new_item = form.save(commit=False)
            new_item.product = product
            new_item.order = order
            new_item.save()

        return super(ProductDetailView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(ProductDetailView, self).get_context_data(**kwargs)
        context['product'] = self.get_object()
        return context


class CartView(generic.FormView):
    template_name = "cart/cart.html"
    form_class = CouponForm

    def get_success_url(self):
        return reverse("cart:summary")

    def get_context_data(self, **kwargs):
        context = super(CartView, self).get_context_data(**kwargs)
        context["order"] = get_or_set_order_session(self.request)
        # context["form"] = self.form_class

        return context

    def form_valid(self, form):
        order = get_or_set_order_session(self.request)
        code = form.cleaned_data.get('coupon_code')
        order.coupon = Coupon.objects.get(code=code)
        order.save()
        messages.info(self.request, "Kod został dodany poprawnie")
        return super(CartView, self).form_valid(form)


class IncreaseQuantityView(generic.View):
    def get(self, request, *args, **kwargs):
        order_item = get_object_or_404(OrderItem, id=kwargs['pk'])
        order_item.quantity += 1
        order_item.save()
        return redirect("cart:summary")


class DecreaseQuantityView(generic.View):
    def get(self, request, *args, **kwargs):
        order_item = get_object_or_404(OrderItem, id=kwargs['pk'])
        if order_item.quantity <= 1:
            order_item.delete()
        else:
            order_item.quantity -= 1
            order_item.save()
        return redirect("cart:summary")


class RemoveFromCartView(generic.View):
    def get(self, request, *args, **kwargs):
        order_item = get_object_or_404(OrderItem, id=kwargs['pk'])
        order_item.delete()
        return redirect("cart:summary")


class CheckoutView(generic.FormView):
    template_name = 'cart/checkout.html'
    form_class = AddressForm

    def get_success_url(self):
        return reverse("cart:payment")

    def form_valid(self, form):
        order = get_or_set_order_session(self.request)
        try:
            customer = Customer.objects.get(user=self.request.user)
        except Customer.DoesNotExist:
            customer = None
            # try:
            #     customer = Customer.objects.get(email=form.cleaned_data['email_shipping'])
            # except Customer.DoesNotExist:
            #     customer = Customer.objects.create(
            #         email=form.cleaned_data['email_shipping'],
            #         first_name=form.cleaned_data['first_name_shipping'],
            #         last_name=form.cleaned_data['last_name_shipping'],
            #         phone_number=form.cleaned_data['phone_number_shipping']
            #     )
        selected_shipping_address = form.cleaned_data.get(
            'selected_shipping_address')
        selected_billing_address = form.cleaned_data.get(
            'selected_billing_address')
        is_addresses_same = form.cleaned_data.get(
            'is_addresses_same')

        if selected_shipping_address:
            order.shipping_address = selected_shipping_address
        else:
            address = Address.objects.create(
                address_type='S',
                customer=customer,
                address_line_1=form.cleaned_data['shipping_address_line_1'],
                address_line_2=form.cleaned_data['shipping_address_line_2'],
                zip_code=form.cleaned_data['shipping_zip_code'],
                city=form.cleaned_data['shipping_city'],
            )
            order.shipping_address = address

        if is_addresses_same:
            address = order.shipping_address
            order.billing_address = address

        else:
            if selected_billing_address:
                order.billing_address = selected_billing_address
            else:

                address = Address.objects.create(
                    address_type='B',
                    customer=customer,
                    address_line_1=form.cleaned_data['billing_address_line_1'],
                    address_line_2=form.cleaned_data['billing_address_line_2'],
                    zip_code=form.cleaned_data['billing_zip_code'],
                    city=form.cleaned_data['billing_city'],
                )
                order.billing_address = address

        order.save()
        messages.info(
            self.request, "You have successfully added your addresses")
        return super(CheckoutView, self).form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(CheckoutView, self).get_form_kwargs()
        kwargs["user_id"] = self.request.user.id
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(CheckoutView, self).get_context_data(**kwargs)
        context["order"] = get_or_set_order_session(self.request)
        return context


class CheckoutAnonView(generic.FormView):
    template_name = 'cart/checkout_anon.html'


class PaymentView(generic.TemplateView):
    template_name = 'cart/payment.html'

    def get_context_data(self, **kwargs):
        context = super(PaymentView, self).get_context_data(**kwargs)
        context["PAYPAL_CLIENT_ID"] = settings.PAYPAL_CLIENT_ID
        context['order'] = get_or_set_order_session(self.request)
        context['CALLBACK_URL'] = self.request.build_absolute_uri(
            reverse("cart:thank-you"))
        return context


class ConfirmOrderView(generic.View):
    def post(self, request, *args, **kwargs):
        order = get_or_set_order_session(request)
        body = json.loads(request.body)
        payment = Payment.objects.create(
            order=order,
            successful=True,
            raw_response=json.dumps(body),
            amount=float(body["purchase_units"][0]["amount"]["value"]),
            payment_method='PayPal'
        )
        order.ordered = True
        order.ordered_date = datetime.date.today()
        order.save()
        return JsonResponse({"data": "Success"})


class ThankYouView(generic.TemplateView):
    template_name = 'cart/thanks.html'


class OrderDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = 'order.html'
    queryset = Order.objects.all()
    context_object_name = 'order'
