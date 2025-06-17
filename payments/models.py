from django.db import models
from jobs.models import Job
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal


User = get_user_model()
class TimestampIDField(models.BigAutoField):
    def get_prep_value(self, value):
        if isinstance(value, (int, str)):
            return super().get_prep_value(value)
        if isinstance(value, timezone.datetime):
            return int(value.timestamp())
        return super().get_prep_value(value)

class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('Credit Card', 'Credit Card'),
        ('Mpesa', 'Mpesa'),
        ('PayPal', 'PayPal'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=100, unique=True,blank=True , null=True)
    transaction_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES, default='Mpesa', blank=True)
    phone_number = models.CharField(max_length=15, default='0')
    is_used = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ], default='pending')

    def __str__(self):
        return f'{self.user} - {self.amount} - {self.job}'

    def get_failure_url(self):
        return 'payment_failure_url'

    def get_success_url(self):
        return 'payment_success_url'


    def get_timestamp_as_int(self):
        return int(self.timestamp.timestamp())

    class Meta:
        app_label = 'payments'
