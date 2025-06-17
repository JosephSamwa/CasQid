from django.contrib import admin
from django.utils.html import format_html
from .models import ContactMessage

class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at', 'is_read_status')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    list_per_page = 20
    ordering = ('-created_at',)

    def is_read_status(self, obj):
        """Shows a visual indicator for Read/Unread messages."""
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            'green' if obj.is_read else 'red',
            'Read' if obj.is_read else 'Unread'
        )
    is_read_status.short_description = 'Status'

    def mark_read_button(self, obj):
        """Adds a quick button to mark messages as Read."""
        if not obj.is_read:
            return format_html(
                '<a href="/admin/app/contactmessage/{}/mark_read/" class="button" style="color: blue;">Mark as Read</a>',
                obj.id
            )
        return "✔"
    mark_read_button.short_description = 'Action'

    def mark_as_read(self, request, queryset):
        """Custom admin action to mark multiple messages as read."""
        queryset.update(is_read=True)
        self.message_user(request, "Selected messages marked as Read.")
    mark_as_read.short_description = "Mark selected messages as Read"

    def mark_as_unread(self, request, queryset):
        """Custom admin action to mark multiple messages as unread."""
        queryset.update(is_read=False)
        self.message_user(request, "Selected messages marked as Unread.")
    mark_as_unread.short_description = "Mark selected messages as Unread"

    actions = [mark_as_read, mark_as_unread]

admin.site.register(ContactMessage, ContactMessageAdmin)
