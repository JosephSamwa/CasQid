from django.core.mail import EmailMultiAlternatives
from django.conf import settings

def send_feedback_email(feedback):
    """Send an email to the admin when a new feedback is submitted."""
    subject = "🌟 New Feedback Submitted"
    admin_email = settings.ADMIN_EMAIL

    text_content = f"""
    A new feedback has been submitted.

    Name: {feedback.name}
    Email: {feedback.email}
    Role: {feedback.role if feedback.role else 'N/A'}
    Rating: {feedback.rating} ⭐
    
    Message:
    {feedback.content}

    Consent to Use as Testimonial: {'Yes' if feedback.consent_to_testimonial else 'No'}

    Please review and take necessary action.
    """

    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; border: 1px solid #ddd; padding: 20px; border-radius: 8px; background-color: #f9f9f9;">
        <div style="text-align: center; margin-bottom: 20px;">
            <img src="https://casqidtravels.com/static/images/logo.jpg" 
                alt="CasQid Travels" 
                style="
                    width: 120px; 
                    height: 120px; 
                    border-radius: 50%; 
                    object-fit: cover; 
                    box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2);
                    border: 3px solid #007bff;">
        </div>

        <h2 style="color: #333;">🌟 New Feedback Submitted</h2>
        <p><strong>Name:</strong> {feedback.name}</p>
        <p><strong>Email:</strong> <a href="mailto:{feedback.email}" style="color: #007bff;">{feedback.email}</a></p>
        <p><strong>Role:</strong> {feedback.role if feedback.role else 'N/A'}</p>
        <p><strong>Rating:</strong> {"⭐" * feedback.rating} ({feedback.rating}/5)</p>

        <p style="border-left: 4px solid #007bff; padding-left: 10px;"><strong>Message:</strong><br>{feedback.content}</p>
        <hr style="border: 0; height: 1px; background-color: #ddd;">

        <p style="text-align: center;">
            <a href="mailto:{feedback.email}" style="background-color: #007bff; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none;">Reply to {feedback.name}</a>
        </p>

        <p style="text-align: center; font-size: 12px; color: #666;">
            This is an automated notification from <strong>CasQid Travels</strong>. Please review and respond as needed.
        </p>
    </div>
    """

    email = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [admin_email])
    email.attach_alternative(html_content, "text/html")
    email.send()
