from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Q
from .models import Job, Skill, JobApplication
from .models import Country

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("name", "display_flag", "currency_code", "country_code")
    search_fields = ("name", "currency_code", "country_code")
    list_filter = ("currency_code",)
    ordering = ("name",)
    readonly_fields = ("flag_url", "display_flag")

    def display_flag(self, obj):
        if obj.flag_url:
            return format_html('<img src="{}" width="40" height="25" style="border:1px solid #ccc;" />', obj.flag_url)
        return "No Flag"

    display_flag.short_description = "Flag"


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    """Admin configuration for Job model"""
    
    # List display columns
    list_display = (
        'title','working_hours', 'country', 'commission_fee', 
    'min_salary', 'application_count','created_at'
    )
    
    # Filtering options
    list_filter = (
        'title', 'country', 'commission_fee',
        ('created_at', admin.DateFieldListFilter),
       
    )
    
    # Search fields
    search_fields = (
        'title', 'company', 'country__name', 'commission_fee',
        'description', 'posted_by__username'
    )
    
    # Grouping fields in edit form
    fieldsets = (
        ('Job Basics', {
            'fields': (
                'title', 'company', 'country', 'commission_fee', 
                'job_type', 'description'
            )
        }),
        ('Job Details', {
            'fields': (
                'experience_level', 'remote_friendly', 
                 'min_salary','working_hours','processing_time',
                'application_deadline'
            )
        }),
        ('Additional Information', {
            'fields': ('vacancy_number','jobs_for_couples','transport','accommodation_available',
                 'company_rating', 'created_at'
            )
        }),
       
    )
    
    # Read-only fields
    readonly_fields = ('created_at', 'posted_by',)

   
    
    # Custom method to count job applications
    def application_count(self, obj):
        return obj.jobapplication_set.count()
    application_count.short_description = 'Applications'
    
    # Custom actions
    actions = ['mark_remote_friendly', 'remove_remote_option']
    
    def mark_remote_friendly(self, request, queryset):
        """Mark selected jobs as remote-friendly"""
        queryset.update(remote_friendly=True)
    mark_remote_friendly.short_description = 'Mark as Remote Friendly'
    
    def remove_remote_option(self, request, queryset):
        """Remove remote option for selected jobs"""
        queryset.update(remote_friendly=False)
    remove_remote_option.short_description = 'Remove Remote Option'
    
    # ✅ Automatically set the logged-in admin as `posted_by`
    def save_model(self, request, obj, form, change):
        """Set the currently logged-in admin as the job poster"""
        if not obj.pk:  # Only set when creating a new job
            obj.posted_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    """Admin configuration for Skill model"""
    list_display = ('name', 'category', 'job_count')
    list_filter = ('category',)
    search_fields = ('name',)
    
    def job_count(self, obj):
        """Count jobs requiring this skill"""
        return obj.job_set.count()
    job_count.short_description = 'Used in Jobs'

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    """Admin configuration for JobApplication model"""
    list_display = (
        'job', 'applicant', 'application_date', 
        'status', 'resume_link'
    )
    
    list_filter = (
        'status', 
        ('application_date', admin.DateFieldListFilter)
    )
    
    search_fields = (
        'job__title', 'applicant__username', 
        'job__company'
    )
    
    # Grouping fields in edit form
    fieldsets = (
        ('Application Details', {
            'fields': (
                'job', 'applicant', 'application_date', 
                'status'
            )
        }),
        ('Application Documents', {
            'fields': ('resume', 'cover_letter')
        })
    )
    
    readonly_fields = ('application_date',)
    
    # Custom method to display resume link
    def resume_link(self, obj):
        if obj.resume:
            return format_html(
                '<a href="{}" target="_blank">View Resume</a>', 
                obj.resume.url
            )
        return 'No Resume'
    resume_link.short_description = 'Resume'
    
    # Custom actions for job applications
    actions = ['move_to_interview', 'reject_applications']
    
    def move_to_interview(self, request, queryset):
        """Move selected applications to interview stage"""
        queryset.update(status='Interview')
    move_to_interview.short_description = 'Move to Interview Stage'
    
    def reject_applications(self, request, queryset):
        """Reject selected job applications"""
        queryset.update(status='Rejected')
    reject_applications.short_description = 'Reject Selected Applications'