from django import forms
from .models import Skill, Job

class JobSearchForm(forms.Form):
    EXPERIENCE_CHOICES = [
        ('', 'Any Experience Level'),
        ('Entry', 'Entry Level'),
        ('Mid', 'Mid Level'),
        ('Senior', 'Senior Level'),
        ('Executive', 'Executive Level')
    ]

    JOB_TYPE_CHOICES = [
        ('', 'Any Job Type'),
        ('Full-Time', 'Full-Time'),
        ('Part-Time', 'Part-Time'),
        ('Freelance', 'Freelance')
    ]

    keyword = forms.CharField(
        required=False, 
        widget=forms.TextInput(attrs={'placeholder': 'Job Title, Keywords, or Company'})
    )
    country = forms.ChoiceField(
        choices=[('', 'All Locations'), ('remote', 'Remote'), ('onsite', 'On-site')],
        required=False
    )
    industry = forms.ModelChoiceField(
        queryset=Job.objects.values_list('industry', flat=True).distinct(),
        required=False,
        empty_label="All Industries"
    )
    experience_level = forms.ChoiceField(choices=EXPERIENCE_CHOICES, required=False)
    job_type = forms.ChoiceField(choices=JOB_TYPE_CHOICES, required=False)
    min_salary = forms.IntegerField(
        required=False, 
        widget=forms.NumberInput(attrs={'placeholder': 'Minimum Salary'})
    )
    remote_only = forms.BooleanField(required=False, label='Remote Only')
    skills = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['skills'].choices = [(skill.id, skill.name) for skill in Skill.objects.all()]