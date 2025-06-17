from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash, get_user_model
from django.contrib.auth.forms import PasswordChangeForm
from django.core.mail import EmailMessage, send_mail
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.db import IntegrityError
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import CustomUser, UserProfile, PasswordResetCode
from applications.models import Application
from applications.forms import ApplicationFilterForm
from jobs.models import Job
from .forms import (
    CustomUserCreationForm, 
    UserProfileForm, 
    PasswordResetRequestForm,
    PasswordResetConfirmForm
)

User = get_user_model()

class UserDashboardView(LoginRequiredMixin, View):
    template_name = 'users/dashboard.html'
    paginate_by = 10

    def get(self, request, *args, **kwargs):
        user = request.user
        profile = user.profile
        
        # Application data (from applications.views.user_dashboard)
        total_applications = Application.objects.filter(user=user).count()
        status_breakdown = Application.objects.filter(user=user).values('status').annotate(count=Count('status'))
        recent_applications = Application.objects.filter(user=user).order_by('-applied_at')[:5]
        
        # Application filter form
        filter_form = ApplicationFilterForm(request.GET or None)
        
        # Filtered applications list
        applications_queryset = Application.objects.filter(user=user).order_by('-applied_at')
        
        if filter_form.is_valid():
            status = filter_form.cleaned_data.get('status')
            job = filter_form.cleaned_data.get('job')
            start_date = filter_form.cleaned_data.get('start_date')
            end_date = filter_form.cleaned_data.get('end_date')
            
            if status:
                applications_queryset = applications_queryset.filter(status=status)
            
            if job:
                applications_queryset = applications_queryset.filter(job=job)
            
            if start_date:
                applications_queryset = applications_queryset.filter(applied_at__date__gte=start_date)
            
            if end_date:
                applications_queryset = applications_queryset.filter(applied_at__date__lte=end_date)
        
        # Paginate applications
        app_paginator = Paginator(applications_queryset, self.paginate_by)
        app_page = request.GET.get('page')
        try:
            page_obj = app_paginator.page(app_page)
        except PageNotAnInteger:
            page_obj = app_paginator.page(1)
        except EmptyPage:
            page_obj = app_paginator.page(app_paginator.num_pages)
            
        # Suggested jobs based on user's past applications
        suggested_jobs = None
        if total_applications > 0:
            # Get unique job categories from past applications
            past_job_categories = Application.objects.filter(user=user).values_list(
                'job__industry', flat=True
            ).distinct()
            
            # Recommend jobs in similar categories that user hasn't applied to
            applied_job_ids = Application.objects.filter(user=user).values_list('job_id', flat=True)
            suggested_jobs = Job.objects.filter(
                industry__in=past_job_categories
            ).exclude(
                id__in=applied_job_ids
            ).order_by('-created_at')[:5]
        
        # Payment data
        payment_stats = profile.get_payment_stats()
        total_paid = profile.get_total_paid()
        payment_methods = profile.get_payment_methods()
        payments = self.paginate_queryset(user.payment_set.order_by('-transaction_date'))
        
        context = {
            'user': user,
            'profile': profile,
            'profile_form': UserProfileForm(instance=profile),
            'password_form': PasswordChangeForm(user),
            'is_profile_complete': profile.is_profile_complete(),
            'profile_completion_percentage': profile.calculate_profile_completion(),
            
            # Payment data
            'payment_stats': payment_stats,
            'total_paid': total_paid,
            'payment_methods': payment_methods,
            'payments': payments,
            
            # Application data
            'total_applications': total_applications,
            'status_breakdown': status_breakdown,
            'recent_applications': recent_applications,
            'page_obj': page_obj,
            'filter_form': filter_form,
            'suggested_jobs': suggested_jobs,
            
            # Recent jobs from payments
            'recent_jobs': Job.objects.filter(payment__user=user).distinct().order_by('-payment__transaction_date')[:5]
        }
        
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        if 'update_profile' in request.POST:
            return self.handle_profile_update(request)
        elif 'change_password' in request.POST:
            return self.handle_password_change(request)
        return redirect('dashboard')

    def handle_profile_update(self, request):
        form = UserProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('user_dashboard')
        else:
            # Add error messages for each field with errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
            # Return to form with errors displayed
            context = {
                'profile': request.user.profile,
                'profile_form': form,  # Use the form with errors
                'password_form': PasswordChangeForm(request.user),
                'is_profile_complete': request.user.profile.is_profile_complete(),
                'profile_completion_percentage': request.user.profile.calculate_profile_completion(),
                'payment_stats': request.user.profile.get_payment_stats(),
                'total_paid': request.user.profile.get_total_paid(),
                'payment_methods': request.user.profile.get_payment_methods(),
                'payments': self.paginate_queryset(request.user.profile.user.payment_set.order_by('-transaction_date')),
            }
            return render(request, self.template_name, context)

    def handle_password_change(self, request):
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password updated successfully!')
            return redirect('user_dashboard')
        return self.get(request)

    def paginate_queryset(self, queryset):
        paginator = Paginator(queryset, self.paginate_by)
        page = self.request.GET.get('payments_page', 1)  # Use different parameter name
        try:
            return paginator.page(page)
        except PageNotAnInteger:
            return paginator.page(1)
        except EmptyPage:
            return paginator.page(paginator.num_pages)



def register_user(request):
    """Handle user registration with email verification and profile creation."""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                # Save user but keep inactive until verification
                user = form.save(commit=False)
                user.is_active = False
                user.save()

                # Store email in session for later verification
                request.session['registration_email'] = user.email

                # Create user profile with necessary fields
                UserProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'first_name': form.cleaned_data['first_name'],
                        'last_name': form.cleaned_data['last_name'],
                        'phone_number': form.cleaned_data['phone_number'],
                        'email': form.cleaned_data['email']
                    }
                )

                # Send verification email
                current_site = get_current_site(request)
                mail_subject = 'Verify Your Email'
                message = render_to_string('users/activation_email.html', {
                    'user': user,
                    'domain': "casqidtravels.com",
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': default_token_generator.make_token(user),
                })

                email = EmailMessage(mail_subject, message, to=[user.email])
                email.content_subtype = "html"
                email.send()

                messages.success(request, 'Please check your email to complete registration.')
                return redirect('activation_sent')

            except IntegrityError as e:
                messages.error(request, "Registration failed: This email or phone number is already in use.")
                return redirect('register')

            except Exception as e:
                user.delete()  # Delete user only if they were saved
                messages.error(request, f'Registration failed: {str(e)}')
                return redirect('register')

        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')

    else:
        form = CustomUserCreationForm()

    return render(request, 'users/register.html', {'form': form})


def activate(request, uidb64, token):
    """Activate user account"""
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.email_confirmed = True
        user.save()
        login(request, user)
        messages.success(request, 'Account activated successfully!')
        return redirect('dashboard')
    
    messages.error(request, 'Invalid activation link!')
    return render(request, 'users/activation_invalid.html')


from django.contrib.auth import authenticate, login


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')  # Use get() to avoid key errors
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Login successful. Welcome back, {user.username}!")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password!")
            return render(request, 'users/login.html', {'username': username})  # Preserve username

    return render(request, 'users/login.html')


@login_required
def create_profile(request):
    """Handle initial profile creation"""
    try:
        profile = request.user.profile
        return redirect('update_profile')
    except UserProfile.DoesNotExist:
        if request.method == 'POST':
            form = UserProfileForm(request.POST, request.FILES)
            if form.is_valid():
                profile = form.save(commit=False)
                profile.user = request.user
                profile.save()
                messages.success(request, 'Profile created successfully!')
                return redirect('dashboard')
        else:
            form = UserProfileForm(initial={
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email,
                'phone_number': request.user.phone_number
            })
        return render(request, 'users/create_profile.html', {'form': form})

@login_required
def update_profile(request):
    """Handle profile updates, creating profile if it doesn't exist"""
    # Use get_or_create to either get existing profile or create a new one
    profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'phone_number': request.user.phone_number,
            'email': request.user.email
        }
    )
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            
            pending_app_id = request.session.get('pending_app_id')
            if pending_app_id:
                del request.session['pending_app_id']
                return redirect('apply', job_id=pending_app_id)
            return redirect('job_list')
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'users/update_profile.html', {
        'form': form,
        'profile': profile
    })

@login_required
def profile_settings(request):
    """Handle profile settings and preferences"""
    profile = get_object_or_404(UserProfile, user=request.user)
    
    if request.method == 'POST':
        # Handle settings update
        pass
    
    return render(request, 'users/profile_settings.html', {'profile': profile})

# Simple views
def user_logout(request):
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('home')

def activation_sent(request):
    return render(request, 'users/activation_sent.html')

def activation_invalid(request):
    return render(request, 'users/activation_invalid.html')

def resend_activation(request):
    """Handle resending of activation email"""
    if request.method == 'POST':
        try:
            email = request.session.get('registration_email')
            if email:
                user = CustomUser.objects.get(email=email, is_active=False)
                
                # Generate new activation email
                current_site = get_current_site(request)
                mail_subject = 'Verify Your Email'
                message = render_to_string('users/activation_email.html', {
                    'user': user,
                    'domain': "casqidtravels.com",
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': default_token_generator.make_token(user),
                })

                email = EmailMessage(mail_subject, message, to=[user.email])
                email.content_subtype = "html"
                email.send()
                
                messages.success(request, 'Activation email has been resent. Please check your inbox.')
                return redirect('activation_sent')
            else:
                messages.error(request, 'Registration session expired. Please register again.')
                return redirect('register')
                
        except CustomUser.DoesNotExist:
            messages.error(request, 'Invalid user or already activated.')
            return redirect('login')
    
    return redirect('activation_sent')

# Password reset views
def password_reset_request(request):
    """View to handle password reset request"""
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = CustomUser.objects.get(email=email)
                
                # Generate and save reset code
                reset_code = PasswordResetCode.generate_code()
                PasswordResetCode.objects.create(user=user, code=reset_code)
                
                # Send email
                send_mail(
                    'Password Reset Request',
                    f'Your password reset code is: {reset_code}',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                
                # Redirect to reset confirmation
                return redirect('password_reset_confirm')
            
            except CustomUser.DoesNotExist:
                messages.error(request, 'No user found with this email address.')
    else:
        form = PasswordResetRequestForm()
    
    return render(request, 'users/password_reset_request.html', {'form': form})

def password_reset_confirm(request):
    """View to handle password reset confirmation"""
    if request.method == 'POST':
        form = PasswordResetConfirmForm(request.POST)
        if form.is_valid():
            reset_code = form.cleaned_data['reset_code']
            new_password = form.cleaned_data['new_password1']
            
            try:
                # Check reset code
                reset_code_obj = PasswordResetCode.objects.get(code=reset_code)
                
                # Get user and set new password
                user = reset_code_obj.user
                user.set_password(new_password)
                user.save()
                
                # Delete used reset code
                reset_code_obj.delete()
                
                messages.success(request, 'Password reset successful!')
                return redirect('login')
            
            except PasswordResetCode.DoesNotExist:
                messages.error(request, 'Invalid reset code.')
    else:
        form = PasswordResetConfirmForm()
    
    return render(request, 'users/password_reset_confirm.html', {'form': form})

