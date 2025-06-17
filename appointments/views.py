from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Appointment, Service
from .forms import AppointmentForm, AppointmentApprovalForm, AppointmentRejectionForm

def book_appointment(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.status = 'pending'
            appointment.save()
            messages.success(request, 'Your appointment request has been submitted. You will receive a confirmation email shortly.')
            return redirect('appointment_tracking')
    else:
        form = AppointmentForm()
    
    services = Service.objects.filter(active=True)
    return render(request, 'appointments/book_appointment.html', {
        'form': form,
        'services': services,
    })

def appointment_tracking(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        booking_code = request.POST.get('booking_code')
        
        if email:
            appointments = Appointment.objects.filter(client_email=email)
        elif booking_code:
            appointments = Appointment.objects.filter(booking_code=booking_code)
        else:
            appointments = None
        
        return render(request, 'appointments/tracking_results.html', {
            'appointments': appointments,
            'email': email,
            'booking_code': booking_code,
        })
    
    return render(request, 'appointments/appointment_tracking.html')

@staff_member_required
def appointment_list(request):
    appointments = Appointment.objects.all().order_by('-created_at')
    
    # Filtering
    status_filter = request.GET.get('status')
    service_filter = request.GET.get('service')
    
    if status_filter:
        appointments = appointments.filter(status=status_filter)
    if service_filter:
        appointments = appointments.filter(service_id=service_filter)
    
    # Pagination
    paginator = Paginator(appointments, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    services = Service.objects.all()
    
    return render(request, 'appointments/admin/appointment_list.html', {
        'page_obj': page_obj,
        'services': services,
        'status_filter': status_filter,
        'service_filter': service_filter,
    })

@staff_member_required
def approve_appointment(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    
    if request.method == 'POST':
        form = AppointmentApprovalForm(request.POST, instance=appointment)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.status = 'approved'
            appointment.save()
            messages.success(request, 'Appointment has been approved.')
            return redirect('admin_appointment_list')
    else:
        form = AppointmentApprovalForm(instance=appointment)
    
    return render(request, 'appointments/admin/approve_appointment.html', {
        'form': form,
        'appointment': appointment,
    })

@staff_member_required
def reject_appointment(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    
    if request.method == 'POST':
        form = AppointmentRejectionForm(request.POST, instance=appointment)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.status = 'rejected'
            appointment.save()
            messages.success(request, 'Appointment has been rejected.')
            return redirect('admin_appointment_list')
    else:
        form = AppointmentRejectionForm(instance=appointment)
    
    return render(request, 'appointments/admin/reject_appointment.html', {
        'form': form,
        'appointment': appointment,
    })

@staff_member_required
def complete_appointment(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    appointment.status = 'completed'
    appointment.save()
    messages.success(request, 'Appointment marked as completed.')
    return redirect('admin_appointment_list')

@staff_member_required
def cancel_appointment(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    appointment.status = 'cancelled'
    appointment.save()
    messages.success(request, 'Appointment marked as cancelled.')
    return redirect('admin_appointment_list')