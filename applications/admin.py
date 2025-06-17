from django.contrib import admin
from django.utils.html import format_html
from django.core.mail import send_mail
from django.template import Template, Context
from .models import Application, ApplicationStatusEmailTemplate
from django.urls import reverse
from django.http import HttpResponseRedirect
import logging

logger = logging.getLogger(__name__)

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    # List display configuration
    list_display = (
        'user', 
        'job', 
        'applied_at', 
        'status', 
        'cv_link',
        'documents_count'
    )
    
    # Filtering options
    list_filter = (
        'status', 
        'applied_at', 
        'job__company',  # Assuming Job model has a company field
    )
    
    # Search fields
    search_fields = (
        'user__username', 
        'user__email', 
        'job__title', 
        'job__company'
    )
    
    # Ordering
    ordering = ('-applied_at',)
    
    # Read-only fields
    readonly_fields = ('applied_at',)
    
    def job_title(self, obj):
        return obj.job.title if obj.job else 'No Job'
    
    # Custom methods for additional functionality
    def cv_link(self, obj):
        """
        Generate a clickable link for the CV if it exists
        """
        if obj.CV:
            return format_html(
                '<a href="{}" target="_blank">View CV</a>', 
                obj.CV.url
            )
        return 'No CV'
    cv_link.short_description = 'CV'
    
    def documents_count(self, obj):
        """
        Count the number of additional documents uploaded
        """
        doc_fields = ['good_conduct', 'passport', 'academic_certificate', 'passport_photo']
        return sum(1 for doc in doc_fields if getattr(obj, doc))
    documents_count.short_description = 'Doc Count'
    
    # Detailed view fieldsets
    fieldsets = (
        ('Applicant Information', {
            'fields': ('user', 'job')
        }),
        ('Application Documents', {
            'fields': (
                'CV', 
                'good_conduct', 
                'passport', 
                'academic_certificate', 
                'passport_photo'
            )
        }),
        ('Application Status', {
            'fields': ('status', 'applied_at', 'admin_message')
        })
    )
    
    # Actions for bulk operations
    actions = [
        'mark_as_reviewed', 
        'mark_as_accepted', 
        'mark_as_rejected',
        'send_email_to_applicant'
    ]
    
    def mark_as_reviewed(self, request, queryset):
        """
        Bulk action to mark selected applications as reviewed
        """
        queryset.update(status='Reviewed')
    mark_as_reviewed.short_description = 'Mark selected as Reviewed'
    
    def mark_as_accepted(self, request, queryset):
        """
        Bulk action to mark selected applications as accepted
        """
        queryset.update(status='Accepted')
    mark_as_accepted.short_description = 'Mark selected as Accepted'
    
    def mark_as_rejected(self, request, queryset):
        """
        Bulk action to mark selected applications as rejected
        """
        queryset.update(status='Rejected')
    mark_as_rejected.short_description = 'Mark selected as Rejected'
    
    def send_email_to_applicant(self, request, queryset):
        """
        Bulk action to send emails to selected applicants based on their current status
        """
        success_count = 0
        for application in queryset:
            try:
                self.send_status_update_email(application, application.admin_message)
                success_count += 1
            except Exception as e:
                self.message_user(
                    request, 
                    f"Error sending email to {application.user.email}: {str(e)}", 
                    level='ERROR'
                )
        
        self.message_user(
            request,
            f"Successfully sent {success_count} email(s) to applicant(s)."
        )
    send_email_to_applicant.short_description = "Send status update email to selected applicants"
    
    # Add admin_message field to the model if it doesn't exist
    def get_form(self, request, obj=None, **kwargs):
        if not hasattr(Application, 'admin_message'):
            # Dynamically add admin_message field if not present in model
            Application.admin_message = ''
        
        return super().get_form(request, obj, **kwargs)
    
    def save_model(self, request, obj, form, change):
        """Override save_model to send email when status is updated"""
        # Check if status has changed
        status_changed = False
        if change:
            old_obj = self.model.objects.get(pk=obj.pk)
            if old_obj.status != obj.status:
                status_changed = True
        else:
            # New application, treat as status change
            status_changed = True
        
        # Get admin message from form
        admin_message = form.cleaned_data.get('admin_message', '')
        
        # Save the model first
        super().save_model(request, obj, form, change)
        
        # Send email if status changed
        if status_changed:
            self.send_status_update_email(obj, admin_message)
    
    def send_status_update_email(self, application, admin_message=''):
        """Send email notification to the applicant about status update"""
        try:
            # Get email template for this status
            try:
                template = ApplicationStatusEmailTemplate.objects.get(
                    status=application.status,
                    is_active=True
                )
            except ApplicationStatusEmailTemplate.DoesNotExist:
                # Use default template if specific one doesn't exist
                template = ApplicationStatusEmailTemplate.objects.filter(
                    is_active=True
                ).first()
                
                if not template:
                    # Create a default template
                    template = ApplicationStatusEmailTemplate(
                        status=application.status,
                        subject="Update on Your Job Application",
                        body="""
                        Dear {applicant_name},
                        
                        Your application for the position of {job_title} at {company} has been updated to: {status}.
                        
                        {% if admin_message %}
                        Additional information:
                        {admin_message}
                        {% endif %}
                        
                        Thank you for your interest in our company.
                        
                        Best regards,
                        CasQid Travels
                        """,
                        is_active=True
                    )
                    template.save()
            
            # First, prepare the context for replacement
            context_dict = {
                'applicant_name': application.user.get_full_name() or application.user.username,
                'job_title': application.job.title,
                'company': application.job.company,
                'status': application.status,
                'application_date': application.applied_at.strftime('%B %d, %Y'),
                'admin_message': admin_message
            }
            
            # Manual string replacement for placeholders using format
            subject = template.subject
            body = template.body
            
            # Replace all placeholders in the subject and body
            for key, value in context_dict.items():
                placeholder = "{" + key + "}"
                subject = subject.replace(placeholder, str(value))
                body = body.replace(placeholder, str(value))
            
            # Now handle the Django template tags using the Template system
            subject_template = Template(subject)
            body_template = Template(body)
            
            context = Context({'admin_message': admin_message})
            
            subject = subject_template.render(context)
            body = body_template.render(context)
            
            # Send email
            send_mail(
                subject,
                body,
                None,  # From email (will use DEFAULT_FROM_EMAIL from settings)
                [application.user.email],
                fail_silently=False,
            )
            
            logger.info(f"Email sent successfully to {application.user.email} about application status: {application.status}")
            
        except Exception as e:
            # Log the error but don't stop the flow
            logger.error(f"Failed to send email: {str(e)}")
            raise
    
    # Add response_change to add a custom button in the change form
    def response_change(self, request, obj):
        if "_send_email" in request.POST:
            # Send the email when the custom button is clicked
            try:
                self.send_status_update_email(obj, obj.admin_message)
                self.message_user(request, f"Email sent to {obj.user.email} successfully!")
            except Exception as e:
                self.message_user(
                    request, 
                    f"Error sending email: {str(e)}", 
                    level='ERROR'
                )
            # Redirect back to the change form
            return HttpResponseRedirect(".")
        return super().response_change(request, obj)
    
    # Add this method to customize the change form
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_send_email_button'] = True
        return super().change_view(
            request, object_id, form_url, extra_context=extra_context
        )

@admin.register(ApplicationStatusEmailTemplate)
class ApplicationStatusEmailTemplateAdmin(admin.ModelAdmin):
    list_display = ('status', 'subject', 'is_active', 'updated_at')
    list_filter = ('status', 'is_active')
    search_fields = ('subject', 'body')
    
    # Add preview fields
    readonly_fields = ('preview_subject', 'preview_body')
    
    fieldsets = (
        (None, {
            'fields': ('status', 'subject', 'body', 'is_active'),
        }),
        ('Preview', {
            'fields': ('preview_subject', 'preview_body'),
            'description': 'This is how the email will look with sample data.'
        }),
    )
    
    def preview_subject(self, obj):
        """Preview the subject with sample data"""
        try:
            # Sample data for preview
            context_dict = {
                'applicant_name': 'John Doe',
                'job_title': 'Sample Job Position',
                'company': 'Sample Company',
                'status': obj.status,
                'application_date': '2023-06-15',
                'admin_message': 'This is a sample message from the admin.'
            }
            
            # Replace placeholders
            subject = obj.subject
            for key, value in context_dict.items():
                placeholder = "{" + key + "}"
                subject = subject.replace(placeholder, str(value))
            
            return subject
        except Exception as e:
            return f"Error previewing: {str(e)}"
    preview_subject.short_description = "Subject Preview"
    
    def preview_body(self, obj):
        """Preview the body with sample data"""
        try:
            # Sample data for preview
            context_dict = {
                'applicant_name': 'John Doe',
                'job_title': 'Sample Job Position',
                'company': 'Sample Company',
                'status': obj.status,
                'application_date': '2023-06-15',
                'admin_message': 'This is a sample message from the admin.'
            }
            
            # Replace placeholders
            body = obj.body
            for key, value in context_dict.items():
                placeholder = "{" + key + "}"
                body = body.replace(placeholder, str(value))
            
            # Process Django template tags
            template = Template(body)
            context = Context({'admin_message': 'This is a sample message from the admin.'})
            rendered = template.render(context)
            
            return format_html('<pre style="white-space: pre-wrap;">{}</pre>', rendered)
        except Exception as e:
            return f"Error previewing: {str(e)}"
    preview_body.short_description = "Body Preview"
