from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Feedback
from .utils import send_feedback_email

@receiver(post_save, sender=Feedback)
def notify_admin_on_feedback(sender, instance, created, **kwargs):
    """Send an email notification when a new feedback is submitted."""
    if created:
        send_feedback_email(instance)
