from django.core.management.base import BaseCommand
from applications.models import ApplicationStatusEmailTemplate

class Command(BaseCommand):
    help = 'Creates default email templates for application status updates'

    def handle(self, *args, **options):
        default_templates = {
            'Pending': {
                'subject': "Your application for {job_title} is pending review",
                'body': """
                Dear {applicant_name},
                
                Your application for the position of {job_title} at {company} has been received and is currently pending review.
                
                We will notify you once we have reviewed your application.
                
                {% if admin_message %}
                Additional information:
                {admin_message}
                {% endif %}
                
                Best regards,
                CasQid Travels
                """
            },
            'Reviewed': {
                'subject': "Your application for {job_title} has been reviewed",
                'body': """
                Dear {applicant_name},
                
                Your application for the position of {job_title} at {company} has been reviewed.
                
                The current status of your application is: {status}.
                
                {% if admin_message %}
                Additional information:
                {admin_message}
                {% endif %}
                
                We will be in touch with next steps soon.
                
                Best regards,
                CasQid Travels
                """
            },
            'Shortlisted': {
                'subject': "You've been shortlisted for {job_title}",
                'body': """
                Dear {applicant_name},
                
                Congratulations! Your application for the position of {job_title} at {company} has been shortlisted.
                
                {% if admin_message %}
                Additional information:
                {admin_message}
                {% endif %}
                
                We will contact you soon with next steps in the process.
                
                Best regards,
                CasQid Travels
                """
            },
            'Accepted': {
                'subject': "Congratulations! Your application for {job_title} has been accepted",
                'body': """
                Dear {applicant_name},
                
                We are pleased to inform you that your application for the position of {job_title} at {company} has been accepted!
                
                {% if admin_message %}
                Additional information:
                {admin_message}
                {% endif %}
                
                We will be in touch shortly with more details about next steps.
                
                Congratulations once again!
                
                Best regards,
                CasQid Travels
                """
            },
            'Rejected': {
                'subject': "Update on your application for {job_title}",
                'body': """
                Dear {applicant_name},
                
                Thank you for your interest in the position of {job_title} at {company}.
                
                We regret to inform you that after careful consideration, we have decided to proceed with other candidates whose qualifications better match our current needs.
                
                {% if admin_message %}
                {admin_message}
                {% endif %}
                
                We appreciate your interest in our company and wish you success in your job search.
                
                Best regards,
                CasQid Travels
                """
            },
            'Interview': {
                'subject': "Interview invitation for {job_title} position",
                'body': """
                Dear {applicant_name},
                
                We are pleased to invite you for an interview for the position of {job_title} at {company}.
                
                {% if admin_message %}
                Interview details:
                {admin_message}
                {% endif %}
                
                Please confirm your attendance by replying to this email.
                
                Best regards,
                CasQid Travels
                """
            }
        }
        
        created_count = 0
        updated_count = 0
        
        for status, content in default_templates.items():
            template, created = ApplicationStatusEmailTemplate.objects.get_or_create(
                status=status,
                defaults={
                    'subject': content['subject'],
                    'body': content['body'],
                    'is_active': True
                }
            )
            
            if created:
                created_count += 1
            else:
                updated_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_count} and updated {updated_count} email templates'
            )
        )
