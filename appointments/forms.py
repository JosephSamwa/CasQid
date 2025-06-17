from django import forms
from django.core.exceptions import ValidationError
from .models import Appointment, Service
from django.utils import timezone
import datetime
from django.core.validators import MinValueValidator

class AppointmentForm(forms.ModelForm):
    requested_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        validators=[MinValueValidator(timezone.now().date())]
    )
    requested_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'})
    )
    
    class Meta:
        model = Appointment
        fields = ['service', 'client_name', 'client_email', 'client_phone', 'requested_date', 'requested_time', 'notes']
    
    def clean_requested_date(self):
        date = self.cleaned_data['requested_date']
        if date.weekday() >= 5:  # Saturday=5, Sunday=6
            raise ValidationError("Appointments are only available on weekdays.")
        return date
    
    def clean(self):
        cleaned_data = super().clean()
        requested_date = cleaned_data.get('requested_date')
        requested_time = cleaned_data.get('requested_time')
        
        if requested_date and requested_time:
            requested_datetime = datetime.datetime.combine(requested_date, requested_time)
            if requested_datetime < timezone.now():
                raise ValidationError("You cannot book an appointment in the past.")
        
        return cleaned_data

class AppointmentApprovalForm(forms.ModelForm):
    approved_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        validators=[MinValueValidator(timezone.now().date())]
    )
    approved_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'})
    )
    
    class Meta:
        model = Appointment
        fields = ['approved_date', 'approved_time', 'status']

class AppointmentRejectionForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['rejection_reason', 'status']