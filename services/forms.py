from django import forms
from .models import Service, Requirement

class ServiceForm(forms.ModelForm):
    requirements = forms.ModelMultipleChoiceField(
        queryset=Requirement.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Service
        fields = ['name', 'description', 'requirements', 'cost', 'duration', 'available', 'image']
