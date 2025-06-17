from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

class Feedback(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    name = models.CharField(max_length=100)
    email = models.EmailField()
    content = models.TextField()
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    consent_to_testimonial = models.BooleanField(default=False)
    approved = models.BooleanField(default=False)
    role = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        if self.user:
            user_identifier = self.user.get_full_name() or self.user.email or self.user.username
            return f"Feedback from {user_identifier}"
        return f"Feedback from {self.name} ({self.email})"

    def clean(self):
        # Make sure either user is provided or name/email for anonymous feedback
        if not self.user and (not self.name or not self.email):
            raise ValidationError("For anonymous feedback, both name and email are required")
        
        # When a user is provided, sync the name and email if they're empty
        if self.user and not self.name:
            self.name = self.user.get_full_name() or self.user.username
        if self.user and not self.email:
            self.email = self.user.email
            
        super().clean()

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    @property
    def user_image(self):
        """Return user's profile picture or default avatar"""
        if self.user and hasattr(self.user, 'profile') and self.user.profile.profile_picture:
            return self.user.profile.profile_picture
        # Generate avatar for non-user or users without profile pictures
        return f"https://ui-avatars.com/api/?name={self.name.replace(' ', '+')}&background=random"
