from django.contrib import admin
from .models import Feedback

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['get_feedback_name', 'rating', 'consent_to_testimonial', 'approved', 'created_at']
    list_filter = ['rating', 'consent_to_testimonial', 'approved']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'name', 'email', 'content']
    actions = ['approve_testimonials', 'unapprove_testimonials']
    fieldsets = (
        (None, {
            'fields': ('user',)
        }),
        ('Feedback Information', {
            'fields': ('name', 'email', 'role', 'content', 'rating')
        }),
        ('Publishing Options', {
            'fields': ('consent_to_testimonial', 'approved')
        }),
    )
    
    def get_feedback_name(self, obj):
        if obj.user:
            return f"{obj.user.get_full_name() or obj.user.username} (User)"
        return f"{obj.name} (Anonymous)"
    
    get_feedback_name.short_description = 'Name'
    
    def approve_testimonials(self, request, queryset):
        queryset.update(approved=True)
    approve_testimonials.short_description = "Approve selected feedback as testimonials"

    def unapprove_testimonials(self, request, queryset):
        queryset.update(approved=False)
    unapprove_testimonials.short_description = "Unapprove selected testimonials"
