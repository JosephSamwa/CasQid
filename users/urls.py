from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import  UserDashboardView

urlpatterns = [
    # Authentication URLs
    path('accounts/register/', views.register_user, name='register'),
    path('accounts/login/', views.user_login, name='login'),
    path('accounts/logout/', views.user_logout, name='logout'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('activation_sent/', views.activation_sent, name='activation_sent'),
    path('invalid/', views.activation_invalid, name='activation_invalid'),
    path('resend-activation/', views.resend_activation, name='resend_activation'),

    path('profile/update/', views.update_profile, name='update_profile'),
    path('profile/settings/', views.profile_settings, name='profile_settings'),
    path('dashboard/', UserDashboardView.as_view(), name='dashboard'),
    # Password Reset URLs
    path('password-reset/', views.password_reset_request, name='password_reset_request'),
    path('password-reset-confirm/', views.password_reset_confirm, name='password_reset_confirm'),
    
    # Django's built-in password reset views (optional, for additional flexibility)
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='accounts/password_reset_complete.html'
         ), 
         name='password_reset_complete'),
]