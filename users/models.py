from django.db import models
from django.conf import settings
from django.utils import timezone
import logging
import random
import string
from django.contrib.auth.models import AbstractUser
from django.db.models import Sum, Count
from datetime import timedelta
logger = logging.getLogger(__name__)


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True,
                             help_text="Enter your email address" 
                              )
    email_confirmed = models.BooleanField(default=False)
    first_name = models.CharField(max_length=30, 
                                  help_text="Enter your first name")
    last_name = models.CharField(max_length=30, help_text="Enter your last name")
    phone_number = models.CharField(max_length=20, help_text="Phone number must be entered in the format: '254.....'")

    REQUIRED_FIELDS = ['first_name', 'last_name', 'email']


    def __str__(self):
        return self.username


class UserProfile(models.Model):
    EMPLOYMENT_CHOICES = [
        ('employed', 'Employed'),
        ('self_employed', 'Self-Employed'),
        ('unemployed', 'Unemployed'),
        ('student', 'Student'),
    ]
    is_job_seeker = models.BooleanField(default=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone_number = models.CharField(max_length=20, help_text="Phone number must be entered in the format: '254.....'")
    email = models.EmailField(unique=True)
    id_number = models.IntegerField(null=True, blank=True, unique=True) 
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    town = models.CharField(max_length=100, blank=True)
    county = models.CharField(max_length=100, blank=True)
    passport_number = models.CharField(max_length=10, null=True, blank=True, unique=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email}'s Profile"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or "N/A"

    def get_phone_number(self):
        return self.user.phone_number or "N/A"
    def get_email(self):
        return self.user.email or "N/A"

    def calculate_profile_completion(self):
        """Calculate the percentage of profile completion"""
        total_fields = 9
        completed_fields = sum(1 for field in [
            self.first_name, self.last_name, self.phone_number,
            self.id_number, self.date_of_birth, self.address,
            self.town, self.county, self.profile_picture,
        ] if field)
        return round((completed_fields / total_fields) * 100)

    def is_profile_complete(self):
        """Check if all required fields are filled"""
        required_fields = [
            self.first_name, self.last_name, self.phone_number,
            self.date_of_birth, self.address, self.town,
            self.county
        ]
        return all(required_fields)

    def get_payment_stats(self):
        """Get payment statistics for the user"""
        now = timezone.now()
        thirty_days_ago = now - timedelta(days=30)
        
        payments = self.user.payment_set.all()
        total_payments = payments.count()
        completed_payments = payments.filter(status='completed').count()
        pending_payments = payments.filter(status='pending').count()
        failed_payments = payments.filter(status='failed').count()
        recent_payments = payments.filter(transaction_date__gte=thirty_days_ago).count()
        
        return {
            'total': total_payments,
            'completed': completed_payments,
            'pending': pending_payments,
            'failed': failed_payments,
            'recent': recent_payments,
        }

    def get_total_paid(self):
        """Get total amount paid by the user"""
        result = self.user.payment_set.filter(status='completed').aggregate(total=Sum('amount'))
        return result['total'] or 0
        
    def get_payment_methods(self):
        """Get payment method distribution for the user"""
        return self.user.payment_set.values('payment_method').annotate(count=Count('payment_method'))

    def get_payment_methods(self):
        """Get user's payment methods statistics"""
        from django.db.models import Count
        return self.user.payment_set.values('payment_method').annotate(count=Count('payment_method'))

    def get_total_paid(self):
        """Get total amount paid by user"""
        from django.db.models import Sum
        return self.user.payment_set.aggregate(Sum('amount'))['amount__sum'] or 0
    

class PasswordResetCode(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def generate_code(cls):
        return ''.join(random.choices(string.digits, k=6))
    
    def __str__(self):
        # Fix: Return a string instead of the user object
        return f"Reset code for {self.user.username}"
