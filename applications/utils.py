from django.core.mail import EmailMultiAlternatives
from django.conf import settings

def send_application_email(application):
    """Send a confirmation email to the applicant and notify the admin."""
    
    # 📩 1. Email to the Applicant
    subject_applicant = "✅ Application Submitted Successfully"
    applicant_email = application.user.email

    text_content_applicant = f"""
    Dear {application.user.first_name},

    Thank you for applying for the position: {application.job.title}.

    We have received your application and will review it shortly. You will be notified once a decision has been made.

    Regards,
    CasQid Travels
    """

    html_content_applicant = f"""
    <html>
    <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4;">
        <div style="max-width: 600px; background: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 2px 2px 10px #ddd;">
            <h2 style="color: #007BFF; text-align: center;">✅ Application Submitted Successfully</h2>
            <p>Dear <strong>{application.user.first_name}</strong>,</p>
            <p>Thank you for applying for the position: <strong>{application.job.title}</strong>.</p>
            <p>We have received your application and will review it shortly. You will be notified once a decision has been made.</p>
            <hr style="border: none; border-top: 1px solid #ddd;">
            <p style="text-align: center;">
                <a href="https://casqidtravels.com/dashboard/" style="background: #007BFF; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                    View Your Application
                </a>
            </p>
            <p style="color: #555; text-align: center;">Regards,<br><strong>CasQid Travels Team</strong></p>
        </div>
    </body>
    </html>
    """

    email_applicant = EmailMultiAlternatives(subject_applicant, text_content_applicant, settings.EMAIL_HOST_USER, [applicant_email])
    email_applicant.attach_alternative(html_content_applicant, "text/html")
    email_applicant.send()

    # 📩 2. Email Notification to the Admin
    subject_admin = "🚀 New Job Application Submitted"
    admin_email = settings.ADMIN_EMAIL  # Ensure this is set in settings.py

    text_content_admin = f"""
    Hello Admin,

    A new application has been submitted.

    Applicant: {application.user.get_full_name()} ({application.user.email})
    Job Applied: {application.job.title}
    Submission Time: {application.applied_at.strftime('%Y-%m-%d %H:%M:%S')}

    Please review the application from the admin panel.

    Regards,
    CasQid System
    """

    html_content_admin = f"""
    <html>
    <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4;">
        <div style="max-width: 600px; background: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 2px 2px 10px #ddd;">
            <h2 style="color: #ff5733; text-align: center;">🚀 New Job Application Submitted</h2>
            <p><strong>Applicant:</strong> {application.user.get_full_name()} (<a href="mailto:{application.user.email}">{application.user.email}</a>)</p>
            <p><strong>Job Applied:</strong> {application.job.title}</p>
            <p><strong>Submission Time:</strong> {application.applied_at.strftime('%Y-%m-%d %H:%M:%S')}</p>
            <hr style="border: none; border-top: 1px solid #ddd;">
            <p style="text-align: center;">
                <a href="https://casqidtravels.com/admin/applications/application/{application.id}/change/" style="background: #ff5733; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                    Review Application
                </a>
            </p>
            <p style="color: #555; text-align: center;">Regards,<br><strong>CasQid System</strong></p>
        </div>
    </body>
    </html>
    """

    email_admin = EmailMultiAlternatives(subject_admin, text_content_admin, settings.EMAIL_HOST_USER, [admin_email])
    email_admin.attach_alternative(html_content_admin, "text/html")
    email_admin.send()


def send_status_update_email(application):
    """Send an email when an admin updates the application status."""
    subject = f"📢 Application Status Update: {application.status}"
    applicant_email = application.user.email

    text_content = f"""
    Dear {application.user.first_name},

    Your job application for {application.job.title} has been updated to: {application.status}.

    {f"Admin message: {application.admin_message}" if application.admin_message else ""}

    Regards,
    CasQid Travels
    """

    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f4f4;">
        <div style="max-width: 600px; background: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 2px 2px 10px #ddd;">
            <h2 style="color: #007BFF; text-align: center;">📢 Application Status Update</h2>
            <p>Dear <strong>{application.user.first_name}</strong>,</p>
            <p>Your job application for <strong>{application.job.title}</strong> has been updated to: <strong>{application.status}</strong>.</p>
            {f"<p style='color: #ff5733;'><strong>Admin message:</strong> {application.admin_message}</p>" if application.admin_message else ""}
            <hr style="border: none; border-top: 1px solid #ddd;">
            <p style="text-align: center;">
                <a href="https://casqidtravels.com/dashboard/dashboard/" style="background: #007BFF; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                    View Your Application
                </a>
            </p>
            <p style="color: #555; text-align: center;">Regards,<br><strong>CasQid Travels Team</strong></p>
        </div>
    </body>
    </html>
    """

    email = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [applicant_email])
    email.attach_alternative(html_content, "text/html")
    email.send()
