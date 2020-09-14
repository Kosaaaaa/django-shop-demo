from django import forms
from pipenv.vendor import attr
from .models import Customer
from allauth.account.forms import SignupForm
import re


class ContactForm(forms.Form):
    NAME_LABEL = "Imię"
    EMAIL_LABEL = "Email"
    MESSAGE_LABEL = "Wiadomość"

    name = forms.CharField(max_length=100, label=NAME_LABEL, widget=forms.TextInput(attrs={
        'placeholder': NAME_LABEL
    }))
    email = forms.EmailField(label=EMAIL_LABEL, widget=forms.TextInput(attrs={
        'placeholder': EMAIL_LABEL
    }))
    message = forms.CharField(label=MESSAGE_LABEL, widget=forms.Textarea(attrs={
        'placeholder': MESSAGE_LABEL
    }))


class CustomerSignupForm(SignupForm):
    FIRST_NAME_LABEL = 'Imię'
    LAST_NAME_LABEL = 'Nazwisko'
    PHONE_NUMBER_LABEL = 'Telefon kontaktowy'
    first_name = forms.CharField(max_length=150, label=FIRST_NAME_LABEL, widget=forms.TextInput(
        attrs={'placeholder': FIRST_NAME_LABEL}))
    last_name = forms.CharField(
        max_length=150, label=LAST_NAME_LABEL, widget=forms.TextInput(attrs={'placeholder': LAST_NAME_LABEL}))

    phone_number = forms.CharField(label=PHONE_NUMBER_LABEL, required=False, max_length=16, widget=forms.TextInput(
        attrs={'placeholder': PHONE_NUMBER_LABEL}))

    class Meta:
        model = Customer

    def save(self, request):
        user = super(CustomerSignupForm, self).save(request)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        return user

    def clean(self):
        super().clean()
        data = self.cleaned_data

        if data.get('phone_number', None):
            phone_number = data.get('phone_number')
            if not re.search('((\+{1}\d{2})|(\+{0}))\d{9}', phone_number):
                self.add_error(
                    'phone_number', 'Błędny format numeru telefonu. Poprawny np. +48123456789 lub 123456789')
