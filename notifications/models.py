from django.db import models
from django.utils.translation import gettext_lazy as _
from users.models import CustomUser

class Notification(models.Model):
    class NotificationType(models.TextChoices):
        SYSTEM = 'SY', _('System')
        BOOKING = 'BK', _('Booking')
        TRIP = 'TR', _('Trip')
        USER = 'US', _('User')

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    date_sent = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    notification_type = models.CharField(
        max_length=2,
        choices=NotificationType.choices,
        default=NotificationType.SYSTEM,
    )
    notification = models.CharField(max_length=50, choices=[
        ('price_drop', 'Price Drop'),
        ('travel_deal', 'Travel Deal'),
        ('travel_advisory', 'Travel Advisory'),
    ])


    class Meta:
        ordering = ['-date_sent']

    def __str__(self):
        return f'{self.user.username} - {self.get_notification_type_display()} - {self.date_sent}'

    def mark_as_read(self):
        self.is_read = True
        self.save()