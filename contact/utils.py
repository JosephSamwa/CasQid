from django.core.mail import EmailMultiAlternatives
from django.conf import settings

def send_contact_message_email(contact_message):
    """Send an email notification to the admin when a new contact message is submitted."""
    subject = f"📩 New Contact Message: {contact_message.subject}"
    recipient_email = settings.ADMIN_EMAIL  # Email where admin should receive messages

    text_content = f"""
    You have received a new contact message.

    Name: {contact_message.name}
    Email: {contact_message.email}
    Subject: {contact_message.subject}
    Message:
    {contact_message.message}

    Please review and respond as soon as possible.
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
        <h2 style="color: #333;">New Contact Message 📩</h2>
        <p><strong>Name:</strong> {contact_message.name}</p>
        <p><strong>Email:</strong> <a href="mailto:{contact_message.email}" style="color: #007bff;">{contact_message.email}</a></p>
        <p><strong>Subject:</strong> {contact_message.subject}</p>
        <p style="border-left: 4px solid #007bff; padding-left: 10px;"><strong>Message:</strong><br>{contact_message.message}</p>
        
        <hr style="border: 0; height: 1px; background-color: #ddd;">
        
        <p style="text-align: center;">
            <a href="mailto:{contact_message.email}" style="background-color: #007bff; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none;">Reply to {contact_message.name}</a>
        </p>
        
        <p style="text-align: center; font-size: 12px; color: #666;">
            This is an automated notification from <strong>CasQid Travels</strong>. Please respond as soon as possible.
        </p>
    </div>
    """

    email = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [recipient_email])
    email.attach_alternative(html_content, "text/html")
    email.send()
