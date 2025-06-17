from django.shortcuts import render
from jobs.models import Job, JobApplication
from contact.models import ContactMessage
from feedback.views import get_testimonials
from django.db.models import Count
from .models import Partner, Service, Stat

def home(request):
    """
    View function for the home page of the site.
    """
    # Get all active stats from database
    db_stats = Stat.objects.filter(is_active=True).order_by('order')
    
    # Create a dictionary of stats for backwards compatibility
    stats = {}
    for stat in db_stats:
        stats[stat.name.lower().replace(' ', '_')] = stat.value
    
    # Ensure we have the required stats with defaults as fallback
    if 'clients_count' not in stats:
        stats['clients_count'] = 200
    if 'jobs_count' not in stats:
        stats['jobs_count'] = Job.objects.count()
    if 'countries_count' not in stats:
        stats['countries_count'] = Job.objects.values('country').distinct().count()
    
    context = {
        # Get latest jobs and job of the week
        'jobs': Job.objects.all().order_by('-created_at')[:8],
        'job_offer': Job.objects.order_by('-commission_fee').first(),
        
        # Get all active stats for the dynamic section
        'all_stats': db_stats,
        # Keep stats dict for backwards compatibility
        'stats': stats,
        
        # Get testimonials
        'testimonials': get_testimonials(request),
        
        # Get services from database
        'services': Service.objects.filter(is_active=True).order_by('order'),
        
        # Get partners from database
        'partners': Partner.objects.filter(is_active=True).order_by('order'),
    }
    return render(request, 'home.html', context)