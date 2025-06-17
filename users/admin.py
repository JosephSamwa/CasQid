from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, UserProfile, PasswordResetCode

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Custom admin configuration for CustomUser model
    """
    model = CustomUser
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active', 'email_confirmed')
    list_filter = ('is_staff', 'is_active', 'email_confirmed')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    
    # Customize the fieldsets for user creation and editing
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'username')}),
        (_('Permissions'), {
            'fields': (
                'is_active', 
                'is_staff', 
                'is_superuser', 
                'groups', 
                'user_permissions',
                'email_confirmed'
            ),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    
    # Customize the add_fieldsets for user creation
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 
                'username',
                'first_name', 
                'last_name', 
                'password1', 
                'password2',
                'is_staff',
                'is_active'
            ),
        }),
    )

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Admin configuration for UserProfile model
    """
    list_display = (
        'get_email', 
        'first_name', 
        'last_name', 
        'phone_number', 
        'is_job_seeker',
        'created_at'
    )
    list_filter = (
        'is_job_seeker', 
        'created_at'
    )
    search_fields = (
        'user__email', 
        'first_name', 
        'last_name', 
        'phone_number'
    )
    readonly_fields = ('created_at', 'updated_at')
    
    def get_email(self, obj):
        """
        Get the user's email for display in admin list view
        """
        return obj.user.email
    get_email.short_description = 'Email'
    get_email.admin_order_field = 'user__email'

@admin.register(PasswordResetCode)
class PasswordResetCodeAdmin(admin.ModelAdmin):
    """
    Admin configuration for PasswordResetCode model
    """
    list_display = ('user', 'code', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'code')
    readonly_fields = ('created_at',)
    
    def has_add_permission(self, request):
        """
        Disable manual creation of password reset codes
        """
        return False

admin.site.site_header = "Maalim Admin Panel"
admin.site.site_title = "Maalim Admin Panel"
admin.site.index_title = "Maalim Admin Panel"