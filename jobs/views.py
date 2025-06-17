from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from django.db.models import Q
from django.views.decorators.http import require_GET
from .models import Job, Country
from .forms import JobSearchForm

class JobListView(ListView):
    model = Job
    template_name = 'jobs/job_list.html'
    context_object_name = 'jobs'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Job.objects.all()
        
        # Get filters from query parameters
        country = self.request.GET.get('country')
        job_type = self.request.GET.get('job_type')
        experience_level = self.request.GET.get('experience_level')
        remote_friendly = self.request.GET.get('remote_friendly')
        min_salary = self.request.GET.get('min_salary')
        industry = self.request.GET.get('industry')
        search_query = self.request.GET.get('search')
        sort_by = self.request.GET.get('sort', '-created_at')
        
        # Apply filters
        if country:
            queryset = queryset.filter(country__iexact=country)
        if job_type:
            queryset = queryset.filter(job_type=job_type)
        if experience_level:
            queryset = queryset.filter(experience_level=experience_level)
        if remote_friendly:
            queryset = queryset.filter(remote_friendly=True)
        if min_salary:
            try:
                queryset = queryset.filter(min_salary__gte=int(min_salary))
            except ValueError:
                pass
        if industry:
            queryset = queryset.filter(industry__icontains=industry)
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(company__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        # Apply sorting
        valid_sort_fields = [
            'created_at', '-created_at', 'title', '-title',
            'company', '-company', 'country', '-country',
            'salary_range', '-salary_range', 'experience_level',
            '-experience_level', 'company_rating', '-company_rating'
        ]
        if sort_by in valid_sort_fields:
            queryset = queryset.order_by(sort_by)
        else:
            queryset = queryset.order_by('-created_at')
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'countries': Country.objects.all(),
            'job_types': Job._meta.get_field('job_type').choices,
            'experience_levels': Job._meta.get_field('experience_level').choices,
            'current_filters': {
                'country': self.request.GET.get('country', ''),
                'job_type': self.request.GET.get('job_type', ''),
                'experience_level': self.request.GET.get('experience_level', ''),
                'remote_friendly': self.request.GET.get('remote_friendly', ''),
                'min_salary': self.request.GET.get('min_salary', ''),
                'industry': self.request.GET.get('industry', ''),
                'search': self.request.GET.get('search', ''),
                'sort': self.request.GET.get('sort', '-created_at')
            }
        })
        return context

@require_GET
def job_detail(request, pk):
    """
    Retrieve job details and related jobs
    
    Args:
        request: HTTP request object
        pk: Primary key of the job
    
    Returns:
        Rendered job detail page with context
    """
    # Fetch the specific job or return 404 if not found
    job = get_object_or_404(Job, pk=pk)
    
    # Fetch up to 5 related jobs from the same industry
    related_jobs = Job.objects.filter(
        industry=job.industry
    ).exclude(pk=job.pk)[:5]
    
    # Prepare context for template rendering
    context = {
        'job': job,
        'related_jobs': related_jobs
    }
    
    return render(request, 'jobs/job_detail.html', context)

class JobSearchView(ListView):
    model = Job
    template_name = 'jobs/job_search.html'
    context_object_name = 'jobs'
    paginate_by = 10

    def get_queryset(self):
        form = JobSearchForm(self.request.GET)
        queryset = Job.objects.all()

        if form.is_valid():
            if form.cleaned_data['keyword']:
                queryset = queryset.filter(
                    Q(title__icontains=form.cleaned_data['keyword']) | 
                    Q(description__icontains=form.cleaned_data['keyword']) |
                    Q(company__name__icontains=form.cleaned_data['keyword'])
                )

            if form.cleaned_data['country']:
                if form.cleaned_data['country'] == 'remote':
                    queryset = queryset.filter(remote_friendly=True)
                elif form.cleaned_data['country'] == 'onsite':
                    queryset = queryset.filter(remote_friendly=False)

            if form.cleaned_data['industry']:
                queryset = queryset.filter(industry=form.cleaned_data['industry'])

            if form.cleaned_data['experience_level']:
                queryset = queryset.filter(experience_level=form.cleaned_data['experience_level'])

            if form.cleaned_data['job_type']:
                queryset = queryset.filter(job_type=form.cleaned_data['job_type'])

            if form.cleaned_data['min_salary']:
                queryset = queryset.filter(min_salary__gte=form.cleaned_data['min_salary'])

            if form.cleaned_data['remote_only']:
                queryset = queryset.filter(remote_friendly=True)

            if form.cleaned_data['skills']:
                queryset = queryset.filter(required_skills__in=form.cleaned_data['skills']).distinct()

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = JobSearchForm(self.request.GET)
        return context