from django.contrib import admin
from .models import Service, Requirement

@admin.register(Requirement)
class RequirementAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'cost', 'duration', 'available', 'created_at')
    list_filter = ('available',)
    search_fields = ('name', 'description')
    ordering = ('-created_at',)
