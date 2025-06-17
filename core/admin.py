from django.contrib import admin
from .models import Partner, Service, Stat

@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'order', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name']
    list_editable = ['is_active', 'order']

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'is_active', 'order', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    list_editable = ['is_active', 'order', 'icon']

@admin.register(Stat)
class StatAdmin(admin.ModelAdmin):
    list_display = ['name', 'value', 'icon', 'is_active', 'order']
    list_filter = ['is_active']
    search_fields = ['name']
    list_editable = ['value', 'icon', 'is_active', 'order']
