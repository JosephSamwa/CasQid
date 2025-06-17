
from jobs.models import Job

from django import forms
from .models import Payment
from django.core.exceptions import ValidationError
import re

class PaymentForm(forms.ModelForm):

    phone_number = forms.CharField(
        max_length=15,  # ✅ Corrected: CharField allows max_length
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter phone number (2547XX or 2541XX)',
        }),
        label="Phone Number"
    )

    mpesa_message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Paste the exact M-Pesa message received',
            'rows': 4
        }),
        label="M-Pesa Message"
    )

    class Meta:
        model = Payment
        fields = ['phone_number', 'mpesa_message']


    



class MpesaPaymentForm(forms.Form):
    amount = forms.DecimalField(
        max_digits=10, 
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    phone_number = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'})
    )
    job = forms.ModelChoiceField(
        queryset=Job.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(MpesaPaymentForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['job'].queryset = Job.objects.filter(user=user)

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero.")
        return amount

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not phone_number.startswith('+'):
            phone_number = '+' + phone_number
        return phone_number

class PaymentFilterForm(forms.Form):
    STATUS_CHOICES = [('', 'All')] + list(Payment._meta.get_field('status').choices)
    PAYMENT_METHOD_CHOICES = [('', 'All')] + list(Payment._meta.get_field('payment_method').choices)

    status = forms.ChoiceField(
        choices=STATUS_CHOICES, 
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    payment_method = forms.ChoiceField(
        choices=PAYMENT_METHOD_CHOICES, 
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    min_amount = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    max_amount = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        min_amount = cleaned_data.get('min_amount')
        max_amount = cleaned_data.get('max_amount')

        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("End date should be after start date.")

        if min_amount and max_amount and min_amount > max_amount:
            raise forms.ValidationError("Maximum amount should be greater than minimum amount.")

        return cleaned_data