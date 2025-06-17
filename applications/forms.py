from django import forms
from django.core.exceptions import ValidationError
from .models import Application
import os
from jobs.models import Job

class ApplicationForm(forms.ModelForm):
   
    """
    Form for job applications with comprehensive validation.
    """
    class Meta:
        model = Application
        fields = [
            'CV', 'good_conduct', 
            'academic_certificate', 'passport', 'passport_photo', 
        ]
        widgets = {
            'CV': forms.FileInput(attrs={'class': 'form-control-file'}),
            'good_conduct': forms.FileInput(attrs={'class': 'form-control-file'}),
            'academic_certificate': forms.FileInput(attrs={'class': 'form-control-file'}),
            'passport': forms.FileInput(attrs={'class': 'form-control-file'}),
            'passport_photo': forms.FileInput(attrs={'class': 'form-control-file', 'accept': 'image/*'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].help_text = self.instance._meta.get_field(field).help_text

    def clean_file(self, field_name):
        file = self.cleaned_data.get(field_name)
        if file:
            # Validate file size (max 5MB)
            if file.size > 5 * 1024 * 1024:
                raise ValidationError(f"{field_name.replace('_', ' ').title()} must be under 5MB.")
            
            # Validate file type
            ext = os.path.splitext(file.name)[1].lower()
            if field_name == 'passport_photo':
                allowed_extensions = ['.jpg', '.jpeg', '.png']
            else:
                allowed_extensions = ['.pdf', '.doc', '.docx']
            
            if ext not in allowed_extensions:
                raise ValidationError(f"Unsupported file type for {field_name.replace('_', ' ').title()}. Allowed types: {', '.join(allowed_extensions)}")
        return file

    def clean_CV(self):
        return self.clean_file('CV')

    def clean_good_conduct(self):
        return self.clean_file('good_conduct')

    def clean_academic_certificate(self):
        return self.clean_file('academic_certificate')

    def clean_passport(self):
        return self.clean_file('passport')

    def clean_passport_photo(self):
        passport_photo = self.clean_file('passport_photo')
        if passport_photo and not passport_photo.content_type.startswith('image'):
            raise ValidationError("Passport photo must be an image file.")
        return passport_photo

    def clean(self):
        cleaned_data = super().clean()
        
        # Ensure all required files are provided
        required_files = ['CV', 'good_conduct', 'academic_certificate', 'passport', 'passport_photo']
        for field in required_files:
            if not cleaned_data.get(field):
                self.add_error(field, f"{field.replace('_', ' ').title()} is required.")
        
        return cleaned_data


class AdminApplicationForm(forms.ModelForm):
    """
    Form for administrators to manage job applications.
    Includes fields for managing application status and viewing uploaded documents.
    """
    class Meta:
        model = Application
        fields = ['status', 'user', 'job', 'CV', 'good_conduct', 
                  'passport', 'academic_certificate', 'passport_photo']
        
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'user': forms.Select(attrs={'class': 'form-control'}),
            'job': forms.Select(attrs={'class': 'form-control'}),
            'CV': forms.FileInput(attrs={'class': 'form-control-file'}),
            'good_conduct': forms.FileInput(attrs={'class': 'form-control-file'}),
            'passport': forms.FileInput(attrs={'class': 'form-control-file'}),
            'academic_certificate': forms.FileInput(attrs={'class': 'form-control-file'}),
            'passport_photo': forms.ImageField(widget=forms.FileInput(attrs={'class': 'form-control-file', 'accept': 'image/*'})),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].help_text = self.instance._meta.get_field(field).help_text

    def clean(self):
        cleaned_data = super().clean()
        # Add any additional validation if needed
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance


class ApplicationFilterForm(forms.Form):
    """
    Form for filtering job applications in admin or dashboard views.
    """
    STATUS_CHOICES = [
        ('', 'All Statuses'),
        ('Pending', 'Pending'),
        ('Reviewed', 'Reviewed'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected')
    ]

    status = forms.ChoiceField(
        choices=STATUS_CHOICES, 
        required=False, 
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    job = forms.ModelChoiceField(
        queryset=Job.objects.all(), 
        required=False, 
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    start_date = forms.DateField(
        required=False, 
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    
    end_date = forms.DateField(
        required=False, 
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    def clean(self):
        """
        Validate date range.
        """
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and start_date > end_date:
            raise ValidationError("End date must be after start date.")
        
        return cleaned_data