from django.db import models
from django.core.validators import FileExtensionValidator
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import pre_save
from django.dispatch import receiver
from users.models import CustomUser
from jobs.models import Job
from payments.models import Payment
from .utils import send_application_email, send_status_update_email


class Application(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    payment = models.ForeignKey(
        Payment, on_delete=models.CASCADE, default=None, blank=True, null=True
    )
    job = models.ForeignKey(Job, on_delete=models.CASCADE)

    CV = models.FileField(
        upload_to="applications/resumes/",
        validators=[FileExtensionValidator(allowed_extensions=["pdf", "doc", "docx"])],
        help_text="(Optional) Upload your CV in PDF, DOC, or DOCX format (max 5MB).",
        blank=False,
    )
    good_conduct = models.FileField(
        upload_to="applications/documents/",
        validators=[FileExtensionValidator(allowed_extensions=["pdf"])],
        help_text="Upload your Certificate of Good Conduct in PDF format (max 5MB).",
        blank=False,
    )
    passport = models.FileField(
        upload_to="applications/documents/",
        validators=[FileExtensionValidator(allowed_extensions=["pdf", "jpg", "jpeg", "png"])],
        help_text="Upload a scanned copy of your passport in PDF, JPG, or PNG format (max 5MB).",
        blank=False,
    )
    academic_certificate = models.FileField(
        upload_to="applications/documents/",
        validators=[FileExtensionValidator(allowed_extensions=["pdf"])],
        help_text="Upload your highest academic certificate or transcript in PDF format (max 5MB).",
        blank=False,
    )
    passport_photo = models.ImageField(
        upload_to="applications/photos/",
        validators=[FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png"])],
        help_text="Upload a recent passport-sized photo in JPG or PNG format (max 5MB).",
        blank=False,
    )

    applied_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=50,
        choices=[
            ("Pending", "Pending"),
            ("Reviewed", "Reviewed"),
            ("Accepted", "Accepted"),
            ("Rejected", "Rejected"),
            ("Shortlisted", "Shortlisted"),
        ],
        default="Pending",
    )
    admin_message = models.TextField(
        blank=True,
        help_text=_("Optional message to include in the email to the applicant"),
    )

    def save(self, *args, **kwargs):
        """Ensure application email is sent when an application is created."""
        is_new = self._state.adding  # Check if this is a new application
        super().save(*args, **kwargs)  # Save the instance first

        if is_new:
            send_application_email(self)  # Send email notification for new application


@receiver(pre_save, sender=Application)
def application_status_change(sender, instance, **kwargs):
    """Send an email when an application status is updated."""
    if instance.pk:  # Ensure it's an existing application
        old_status = Application.objects.filter(pk=instance.pk).values_list("status", flat=True).first()
        if old_status and old_status != instance.status:
            send_status_update_email(instance)

class ApplicationStatusEmailTemplate(models.Model):
    """Model for storing email templates for application status updates"""
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Interview', 'Interv   iew'),
        ('Reviewed', 'Reviewed'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
        ('Shortlisted', 'Shortlisted'),
    ]
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, unique=True)
    subject = models.CharField(max_length=255)
    body = models.TextField(help_text=_(
        "You can use the following placeholders: {applicant_name}, {job_title}, "
        "{company}, {status}, {application_date}, {admin_message}"
    ))
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Application Status Email Template"
        verbose_name_plural = "Application Status Email Templates"

    def __str__(self):
        return f"Email Template for {self.status} Status"