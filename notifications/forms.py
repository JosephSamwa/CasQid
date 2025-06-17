# notifications/forms.py

from django import forms
from .models import Notification

class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ['user', 'message', 'notification_type', 'notification']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].widget.attrs.update({'class': 'form-control'})
        self.fields['message'].widget.attrs.update({'class': 'form-control'})
        self.fields['notification_type'].widget.attrs.update({'class': 'form-control'})
        self.fields['notification'].widget.attrs.update({'class': 'form-control'})

class NotificationFilterForm(forms.Form):
    notification_type = forms.ChoiceField(
        choices=[('', 'All')] + list(Notification.NotificationType.choices),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    is_read = forms.ChoiceField(
        choices=[('', 'All'), ('True', 'Read'), ('False', 'Unread')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )