from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    notification_type_display = serializers.CharField(source='get_notification_type_display', read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'user', 'message', 'date_sent', 'is_read', 'notification_type', 'notification_type_display']
        read_only_fields = ['user', 'date_sent']