from .models import Appointment

def pending_appointments(request):
    """
    Adds pending appointment information to the context for all templates
    """
    context = {
        'has_pending_appointment': False
    }
    
    if request.user.is_authenticated and request.user.email:
        # Check for incomplete appointments (adjust the statuses as needed)
        pending_count = Appointment.objects.filter(
            client_email=request.user.email,
            status__in=['pending', 'approved']
        ).count()
        
        context['has_pending_appointment'] = pending_count > 0
    
    return context