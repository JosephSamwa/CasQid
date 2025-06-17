from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden
from .models import Application, Job
from .forms import ApplicationForm, AdminApplicationForm, ApplicationFilterForm
from payments.models import Payment
from users.models import UserProfile

@login_required
def user_dashboard(request):
    """
    Redirect to the unified dashboard in the users app
    """
    return redirect('dashboard')

@login_required
def quick_job_apply(request, job_id):
    """
    Quick apply functionality from dashboard.
    Redirects to full application submission with pre-selected job.
    """
    job = get_object_or_404(Job, id=job_id)
    
    # Check if user has already applied to this job
    existing_application = Application.objects.filter(
        user=request.user, 
        job=job
    ).exists()
    
    if existing_application:
        messages.warning(request, "You have already applied to this job.")
        return redirect('user_dashboard')
    
    # Redirect to full application submission
    return redirect('submit_application', job.id)

@login_required
def requirements(request, job_id):
     job = get_object_or_404(Job, pk=job_id)
     formatted_commission_fee = f"{job.commission_fee:,.2f}"  # Adds commas & keeps 2 decimal places
     return render(request, 'applications/requirements.html', {
        'job': job,
        'formatted_commission_fee': formatted_commission_fee,

    })
@login_required  # Add this decorator to ensure user is logged in
def submit_application(request, job_id):
    """
    Allow logged-in users to submit a job application.
    """
    request.session['pending_app_id'] =job_id
    required_profile_fields = [
        'phone_number', 
        'id_number', 
        'first_name', 
        'last_name',
        'date_of_birth', 
        'address', 
        'town', 
        'county', 
        'passport_number'
    ]

    # Check if user has a profile
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        messages.error(request, 'Please complete your profile before applying.')
        return redirect('update_profile')  # Changed from create_profile

    # Check for missing required fields
    missing_fields = [
        field for field in required_profile_fields 
        if not getattr(profile, field, None)
    ]
    
    if missing_fields:
        fields_list = ", ".join(field.replace('_', ' ').title() for field in missing_fields)
        messages.warning(
            request, 
            f'Please complete your profile before applying. Missing fields: {fields_list}'
        )
        return redirect('update_profile')

    # Get the job
    job = get_object_or_404(Job, id=job_id)
    
    # Check if user has already applied
    existing_application = Application.objects.filter(
        user=request.user, 
        job=job
    ).exists()
    
    if existing_application:
        payment = Payment.objects.filter(
            user=request.user, 
            job=job
        ).exists()
        
        if payment:
            messages.warning(request, "You have already applied to this job.")
            return redirect('job_detail', job.id)
        else:
            messages.warning(request, "You have already applied to this job. Proceed to payment.")
            return redirect('guide', job.id)

    # Handle application submission
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.job = job
            application.save()
            
            messages.success(request, "Application submitted successfully!")
            return redirect('guide', job_id=job.id)  # Updated this line
    else:
        form = ApplicationForm()
    
    return render(request, 'applications/submit_application.html', {
        'form': form,
        'job': job
    })

@login_required
def application_list(request):
    """
    List applications for the current user.
    """
    applications = Application.objects.filter(user=request.user).order_by('-applied_at')
    
    paginator = Paginator(applications, 10)  # 10 applications per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'applications/application_list.html', {
        'page_obj': page_obj
    })

def is_admin_or_staff(user):
    """
    Helper function to check if user is admin or staff.
    """
    return user.is_authenticated and (user.is_staff or user.is_superuser)

@user_passes_test(is_admin_or_staff)
def admin_application_list(request):
    """
    Admin view to list and filter all job applications.
    """
    queryset = Application.objects.all().order_by('-applied_at')
    
    filter_form = ApplicationFilterForm(request.GET or None)
    
    if filter_form.is_valid():
        status = filter_form.cleaned_data.get('status')
        job = filter_form.cleaned_data.get('job')
        start_date = filter_form.cleaned_data.get('start_date')
        end_date = filter_form.cleaned_data.get('end_date')
        
        if status:
            queryset = queryset.filter(status=status)
        
        if job:
            queryset = queryset.filter(job=job)
        
        if start_date:
            queryset = queryset.filter(applied_at__date__gte=start_date)
        
        if end_date:
            queryset = queryset.filter(applied_at__date__lte=end_date)
    
    paginator = Paginator(queryset, 20)  # 20 applications per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'applications/admin_application_list.html', {
        'page_obj': page_obj,
        'filter_form': filter_form
    })

@user_passes_test(is_admin_or_staff)
def update_application_status(request, application_id):
    """
    Allow admins to update application status.
    """
    application = get_object_or_404(Application, id=application_id)
    
    if request.method == 'POST':
        form = AdminApplicationForm(request.POST, request.FILES, instance=application)
        if form.is_valid():
            form.save()
            messages.success(request, f"Application status updated to {form.cleaned_data['status']}.")
            return redirect('admin_application_list')
    else:
        form = AdminApplicationForm(instance=application)
    
    return render(request, 'applications/update_application_status.html', {
        'form': form,
        'application': application
    })

@login_required
def application_detail(request, application_id):
    """
    View details of a specific application.
    """
    application = get_object_or_404(Application, id=application_id)
    
    # Ensure only the application owner or admin can view
    if not (request.user == application.user or is_admin_or_staff(request.user)):
        return HttpResponseForbidden("You do not have permission to view this application.")
    
    return render(request, 'applications/application_detail.html', {
        'application': application
    })