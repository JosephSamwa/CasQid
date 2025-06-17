from django.shortcuts import render, redirect, get_object_or_404
from .models import Service
from .forms import ServiceForm

def add_service(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('service_list')  # Redirect to the service list page
    else:
        form = ServiceForm()

    return render(request, 'services/add_service.html', {'form': form})


def service_list(request):
    services = Service.objects.all().order_by('-created_at')
    return render(request, 'services/services.html', {'services': services})


def service_detail(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    # Get all services to display in the sidebar
    all_services = Service.objects.all().order_by('-created_at')
    return render(request, 'services/service_detail.html', {
        'service': service,
        'services': all_services
    })
