from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import datetime
import random
import string
from services.models import Service

from django.core.exceptions import ValidationError


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    client_name = models.CharField(max_length=100)
    client_email = models.EmailField()
    client_phone = models.CharField(max_length=20)
    requested_date = models.DateField()
    requested_time = models.TimeField()
    notes = models.TextField(blank=True)
    
    # Admin fields
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    approved_date = models.DateField(null=True, blank=True)
    approved_time = models.TimeField(null=True, blank=True)
    booking_code = models.CharField(max_length=20, blank=True)
    rejection_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.client_name} - {self.service} - {self.status}"
    
    def generate_booking_code(self):
        if not self.approved_date:
            return ""
        
        date_str = self.approved_date.strftime("%d%m%y")
        random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        return f"APPT-{date_str}-{random_str}"
    
    def send_confirmation_email(self):
        subject = f"Appointment Request Received: {self.service.name}"
        html_message = render_to_string('appointments/email_confirmation.html', {
            'appointment': self,
        })
        plain_message = strip_tags(html_message)
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [self.client_email],
            html_message=html_message,
        )
    
    def send_approval_email(self):
        subject = f"Appointment Approved: {self.service.name} - {self.booking_code}"
        html_message = render_to_string('appointments/email_approval.html', {
            'appointment': self,
        })
        plain_message = strip_tags(html_message)
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [self.client_email],
            html_message=html_message,
        )
    
    def send_rejection_email(self):
        subject = f"Appointment Rejected: {self.service.name}"
        html_message = render_to_string('appointments/email_rejection.html', {
            'appointment': self,
        })
        plain_message = strip_tags(html_message)
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [self.client_email],
            html_message=html_message,
        )
    
    def clean(self):
        # Check if client already has pending or approved appointments
        if self.status in ['pending', 'approved'] and not self.pk:
            existing_appointments = Appointment.objects.filter(
                client_email=self.client_email,
                status__in=['pending', 'approved']
            ).exclude(pk=self.pk)
            
            if existing_appointments.exists():
                raise ValidationError("You already have an existing appointment. Please wait until it's completed or cancelled.")
    
    def save(self, *args, **kwargs):
        # Generate booking code when approved
        if self.status == 'approved' and not self.booking_code:
            self.booking_code = self.generate_booking_code()
        
        # Send appropriate emails
        if not self.pk:  # New appointment
            super().save(*args, **kwargs)
            self.send_confirmation_email()
        else:
            original = Appointment.objects.get(pk=self.pk)
            if original.status != self.status:
                if self.status == 'approved':
                    self.send_approval_email()
                elif self.status == 'rejected':
                    self.send_rejection_email()
            super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-created_at']