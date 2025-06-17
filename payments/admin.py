from django.contrib import admin
from django.db import models
from django.db.models import Sum, Count
from django.utils.html import format_html
from django.urls import reverse
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    # List display configuration
    list_display = (
        'transaction_id',
        'user_link', 
        'job_link', 
        'amount', 
        'payment_method', 
        'transaction_status', 
        'transaction_date'
    )
    
    # Filtering and search options
    list_filter = (
        'payment_method', 
        'status', 
        'transaction_date'
    )
    
    search_fields = (
        'user__username', 
        'user__email', 
        'job__title', 
        'transaction_id'
    )
    
    # Grouping fields in the edit form
    fieldsets = (
        ('Payment Details', {
            'fields': (
                'user', 
                'job', 
                'amount', 
                'payment_method', 
                'phone_number'
            )
        }),
        ('Transaction Information', {
            'fields': (
                'transaction_id', 
                'transaction_date', 
                'status', 
                'is_used'
            )
        })
    )
    
    # Read-only fields
    readonly_fields = (
        'transaction_date', 
    )
    
    # Custom methods for displaying links
    def user_link(self, obj):
        if not obj.user:
            return format_html('<span style="color: red;">No User</span>')
    
        try:
            url = reverse(f'admin:{obj.user._meta.app_label}_{obj.user._meta.model_name}_change', args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user.username)
        except Exception:
            return obj.user.username  # Fallback if reverse fails

    user_link.short_description = 'User'


    
    def job_link(self, obj):
        if not obj.job:
            return format_html('<span style="color: red;">No Job</span>')
        url = reverse('admin:jobs_job_change', args=[obj.job.id])
        return format_html('<a href="{}">{}</a>', url, obj.job.title)
    job_link.short_description = 'Job'
    
    def transaction_status(self, obj):
        status_colors = {
            'pending': 'orange',
            'completed': 'green',
            'failed': 'red',
            'refunded': 'blue'
        }
        color = status_colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>', 
            color, 
            obj.status.capitalize()
        )
    transaction_status.short_description = 'Status'
    
    # Custom actions
    actions = ['mark_as_completed', 'mark_as_refunded']
    
    def mark_as_completed(self, request, queryset):
        queryset.update(status='completed')
    mark_as_completed.short_description = 'Mark selected payments as completed'
    
    def mark_as_refunded(self, request, queryset):
        queryset.update(status='refunded')
    mark_as_refunded.short_description = 'Mark selected payments as refunded'
    
    # Optional: Custom list view queryset method
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user', 'job')
    
    # Optional: Custom summary methods
    def changelist_view(self, request, extra_context=None):
        # Aggregate payments data for dashboard
        extra_context = extra_context or {}
        extra_context['total_payments'] = Payment.objects.aggregate(
            total_amount=Sum('amount'),
            total_count=Count('id'),
            completed_amount=Sum('amount', filter=models.Q(status='completed')),
            completed_count=Count('id', filter=models.Q(status='completed'))
        )
        return super().changelist_view(request, extra_context)