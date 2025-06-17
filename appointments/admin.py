from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html
from .models import Appointment, Service
from .forms import AppointmentApprovalForm, AppointmentRejectionForm
from django.shortcuts import render

class StatusFilter(SimpleListFilter):
    title = 'status'
    parameter_name = 'status'
    
    def lookups(self, request, model_admin):
        return Appointment.STATUS_CHOICES
    
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status=self.value())
        return queryset

class ServiceFilter(SimpleListFilter):
    title = 'service'
    parameter_name = 'service'
    
    def lookups(self, request, model_admin):
        services = Service.objects.all()
        return [(s.id, s.name) for s in services]
    
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(service_id=self.value())
        return queryset

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'duration', 'active')
    list_editable = ('active',)
    search_fields = ('name',)

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        'client_name', 
        'service', 
        'status', 
        'requested_date', 
        'requested_time',
        'approved_date',
        'approved_time',
        'booking_code',
        'whatsapp_link',
        'created_at',
    )
    list_filter = (StatusFilter, ServiceFilter)
    search_fields = ('client_name', 'client_email', 'client_phone', 'booking_code')
    readonly_fields = ('created_at', 'updated_at')
    actions = ['bulk_approve', 'bulk_reject', 'bulk_cancel']
    fieldsets = (
        (None, {
            'fields': ('service', 'client_name', 'client_email', 'client_phone')
        }),
        ('Appointment Details', {
            'fields': ('requested_date', 'requested_time', 'notes')
        }),
        ('Admin Details', {
            'fields': (
                'status', 
                'approved_date', 
                'approved_time', 
                'booking_code',
                'rejection_reason',
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def whatsapp_link(self, obj):
        if obj.client_phone:
            phone = obj.client_phone.lstrip('+').replace(' ', '')
            return format_html(
                '<a href="https://wa.me/{}" target="_blank">WhatsApp</a>',
                phone
            )
        return "-"
    whatsapp_link.short_description = "Contact"
    
    def bulk_approve(self, request, queryset):
        if 'apply' in request.POST:
            form = AppointmentApprovalForm(request.POST)
            if form.is_valid():
                approved_date = form.cleaned_data['approved_date']
                approved_time = form.cleaned_data['approved_time']
                
                updated = queryset.update(
                    status='approved',
                    approved_date=approved_date,
                    approved_time=approved_time,
                )
                
                # Generate booking codes for all approved appointments
                for appointment in queryset:
                    if appointment.status == 'approved' and not appointment.booking_code:
                        appointment.booking_code = appointment.generate_booking_code()
                        appointment.save()
                
                self.message_user(request, f"{updated} appointments were approved.")
                return HttpResponseRedirect(request.get_full_path())
        else:
            form = AppointmentApprovalForm(initial={'_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})
        
        return render(
            request,
            'appointments/admin/bulk_approve.html',
            {
                'appointments': queryset,
                'form': form,
            }
        )
    bulk_approve.short_description = "Approve selected appointments"
    
    def bulk_reject(self, request, queryset):
        if 'apply' in request.POST:
            form = AppointmentRejectionForm(request.POST)
            if form.is_valid():
                rejection_reason = form.cleaned_data['rejection_reason']
                
                updated = queryset.update(
                    status='rejected',
                    rejection_reason=rejection_reason,
                )
                
                self.message_user(request, f"{updated} appointments were rejected.")
                return HttpResponseRedirect(request.get_full_path())
        else:
            form = AppointmentRejectionForm(initial={'_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})
        
        return render(
            request,
            'appointments/admin/bulk_reject.html',
            {
                'appointments': queryset,
                'form': form,
            }
        )
    bulk_reject.short_description = "Reject selected appointments"
    
    def bulk_cancel(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f"{updated} appointments were cancelled.")
    bulk_cancel.short_description = "Cancel selected appointments"
    
    def get_actions(self, request):
        actions = super().get_actions(request)
        if not request.user.is_superuser:
            if 'delete_selected' in actions:
                del actions['delete_selected']
        return actions