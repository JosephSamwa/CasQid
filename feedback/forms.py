from django import forms
from .models import Feedback

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['name', 'email', 'role', 'content', 'rating', 'consent_to_testimonial']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Share your experience...'}),
            'rating': forms.RadioSelect(),
            'consent_to_testimonial': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'role': forms.TextInput(attrs={'placeholder': 'e.g. Software Developer, Teacher, etc.'}),
        }
        labels = {
            'consent_to_testimonial': 'I allow CasQid Travels to use my feedback as a testimonial',
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make fields required only for anonymous users
        self.fields['name'].required = True
        self.fields['email'].required = True
        self.fields['role'].required = False
