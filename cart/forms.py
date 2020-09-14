from django.contrib.auth import get_user_model
from django.template.defaultfilters import default
from django.utils import timezone
from django import forms
from django.db.models import Q
from .models import (
    OrderItem, Product,
    Address, SizeVariations, Coupon
)
from core.models import Customer
User = get_user_model()


class AddToCartForm(forms.ModelForm):
    size = forms.ModelChoiceField(
        queryset=SizeVariations.objects.none(), empty_label='-')
    # quantity = forms.IntegerField(min_value=1)

    class Meta:
        model = OrderItem
        fields = ['quantity', 'size']

    def __init__(self, *args, **kwargs):
        self.product_id = kwargs.pop('product_id')
        product = Product.objects.get(id=self.product_id)
        super().__init__(*args, **kwargs)
        # self.fields['size'].queryset = SizeVariations.objects.filter(product=product).order_by('size__size_order').values_list('size__name', flat=True)
        self.fields['size'].queryset = SizeVariations.objects.filter(
            product=product)
        # self.fields['size'].to_field_name = 'size__name'

    def clean(self):
        # product_id = self.product_id
        product = Product.objects.get(id=self.product_id)
        quantity = self.cleaned_data['quantity']
        # quantity = 1
        if product.stock < quantity:
            raise forms.ValidationError(
                f"The maximum stock available is {product.stock}")


class CouponForm(forms.Form):
    coupon_code = forms.CharField(
        max_length=15, required=True)

    def clean(self):
        cleaned_data = self.cleaned_data
        selected_coupon_code = cleaned_data.get('coupon_code', None)
        now = timezone.localtime()
        try:
            coupon = Coupon.objects.get(
                code=selected_coupon_code, valid_from__lte=now, valid_to__gte=now, active=True)
        except Coupon.DoesNotExist:
            self.add_error("coupon_code", "Nie ma takiego kodu")


class AddressForm(forms.Form):
    FIRST_NAME_LABEL = 'Imię'
    LAST_NAME_LABEL = 'Nazwisko'
    PHONE_NUMBER_LABEL = 'Telefon kontaktowy'
    EMAIL_LABEL = 'Email'

    ADDRESS_LINE_1_LABEL = 'Adres Linia 1'
    ADDRESS_LINE_2_LABEL = 'Adres Linia 2'
    ZIP_CODE_LABEL = 'Kod Pocztowy'
    CITY_LABEL = 'Miasto'
    SELECTED_ADDRESS = 'Wybrany Zapisany Adres'

    first_name_shipping = forms.CharField(max_length=150, label=FIRST_NAME_LABEL, widget=forms.TextInput(
        attrs={'placeholder': FIRST_NAME_LABEL}))
    last_name_shipping = forms.CharField(
        max_length=150, label=LAST_NAME_LABEL, widget=forms.TextInput(attrs={'placeholder': LAST_NAME_LABEL}))
    email_shipping = forms.EmailField(label=EMAIL_LABEL, widget=forms.TextInput(
        attrs={'placeholder': EMAIL_LABEL}))
    phone_number_shipping = forms.CharField(label=PHONE_NUMBER_LABEL, required=False, widget=forms.TextInput(
        attrs={'placeholder': PHONE_NUMBER_LABEL}))

    shipping_address_line_1 = forms.CharField(required=False, label=ADDRESS_LINE_1_LABEL, widget=forms.TextInput(
        attrs={'placeholder': ADDRESS_LINE_1_LABEL}))
    shipping_address_line_2 = forms.CharField(required=False, label=ADDRESS_LINE_2_LABEL, widget=forms.TextInput(
        attrs={'placeholder': ADDRESS_LINE_2_LABEL}))
    shipping_zip_code = forms.CharField(required=False, label=ZIP_CODE_LABEL, widget=forms.TextInput(
        attrs={'placeholder': ZIP_CODE_LABEL}))
    shipping_city = forms.CharField(required=False, label=CITY_LABEL, widget=forms.TextInput(
        attrs={'placeholder': CITY_LABEL}))
    selected_shipping_address = forms.ModelChoiceField(
        Address.objects.none(), required=False, label=SELECTED_ADDRESS, widget=forms.Select(attrs={'placeholder': SELECTED_ADDRESS})
    )

    first_name_billing = forms.CharField(required=False, max_length=150, label=FIRST_NAME_LABEL, widget=forms.TextInput(
        attrs={'placeholder': FIRST_NAME_LABEL}))
    last_name_billing = forms.CharField(required=False,
                                        max_length=150, label=LAST_NAME_LABEL, widget=forms.TextInput(attrs={'placeholder': LAST_NAME_LABEL}))
    email_billing = forms.EmailField(required=False, label=EMAIL_LABEL, widget=forms.TextInput(
        attrs={'placeholder': EMAIL_LABEL}))
    phone_number_billing = forms.CharField(label=PHONE_NUMBER_LABEL, required=False, widget=forms.TextInput(
        attrs={'placeholder': PHONE_NUMBER_LABEL}))

    billing_address_line_1 = forms.CharField(required=False, label=ADDRESS_LINE_1_LABEL, widget=forms.TextInput(
        attrs={'placeholder': ADDRESS_LINE_1_LABEL}))
    billing_address_line_2 = forms.CharField(required=False, label=ADDRESS_LINE_2_LABEL, widget=forms.TextInput(
        attrs={'placeholder': ADDRESS_LINE_2_LABEL}))
    billing_zip_code = forms.CharField(required=False, label=ZIP_CODE_LABEL, widget=forms.TextInput(
        attrs={'placeholder': ZIP_CODE_LABEL}))
    billing_city = forms.CharField(required=False, label=CITY_LABEL, widget=forms.TextInput(
        attrs={'placeholder': CITY_LABEL}))

    selected_billing_address = forms.ModelChoiceField(
        Address.objects.none(), required=False, label=SELECTED_ADDRESS, widget=forms.Select(attrs={'placeholder': SELECTED_ADDRESS})
    )

    is_addresses_same = forms.BooleanField(
        initial=True, required=False, label='Mój Adres Płatności taki sam jak Wysyłki')

    def __init__(self, *args, **kwargs):
        user_id = kwargs.pop('user_id')
        super().__init__(*args, **kwargs)

        # user = User.objects.filter(id=user_id).first()
        customer = Customer.objects.filter(user__id=user_id).first()

        shipping_address_qs = Address.objects.filter(
            customer=customer,
            address_type='S'
        )
        billing_address_qs = Address.objects.filter(
            customer=customer,
            address_type='B'
        )

        self.fields['selected_shipping_address'].queryset = shipping_address_qs
        self.fields['selected_billing_address'].queryset = billing_address_qs

    def clean(self):
        data = self.cleaned_data

        selected_shipping_address = data.get('selected_shipping_address', None)
        if selected_shipping_address is None:
            if not data.get('shipping_address_line_1', None):
                self.add_error("shipping_address_line_1",
                               "Please fill in this field")
            if not data.get('shipping_zip_code', None):
                self.add_error("shipping_zip_code",
                               "Please fill in this field")
            if not data.get('shipping_city', None):
                self.add_error("shipping_city", "Please fill in this field")

        if not data.get('is_addresses_same'):
            selected_billing_address = data.get(
                'selected_billing_address', None)
            if selected_billing_address is None:
                if not data.get('billing_address_line_1', None):
                    self.add_error("billing_address_line_1",
                                   "Please fill in this field")
                if not data.get('billing_zip_code', None):
                    self.add_error("billing_zip_code",
                                   "Please fill in this field")
                if not data.get('billing_city', None):
                    self.add_error("billing_city", "Please fill in this field")
