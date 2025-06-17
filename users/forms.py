from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.validators import RegexValidator
from .models import CustomUser, UserProfile

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator
from .models import CustomUser


from django.core.exceptions import ValidationError

class CustomUserCreationForm(UserCreationForm):
    """Form for creating a new user with help texts displayed"""
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'Enter your email',
            'class': 'form-control border border-blue-600 rounded-md p-2'
        }),
        help_text=CustomUser._meta.get_field('email').help_text
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your first name',
            'class': 'form-control border border-blue-600 rounded-md p-2'
        }),
        help_text=CustomUser._meta.get_field('first_name').help_text
    )
    username = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your username',
            'class': 'form-control border border-blue-600 rounded-md p-2'
        }),
        help_text=CustomUser._meta.get_field('username').help_text
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your last name',
            'class': 'form-control border border-blue-600 rounded-md p-2'
        }),
        help_text=CustomUser._meta.get_field('last_name').help_text
    )
    phone_number = forms.CharField(
        max_length=20,
        validators=[RegexValidator(
            regex=r'^1?\d{9,15}$',
            message="Phone number must be entered in the format: '254.....'."
        )],
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your phone number',
            'class': 'form-control border border-blue-600 rounded-md p-2'
        }),
        help_text=CustomUser._meta.get_field('phone_number').help_text
    )

    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'first_name', 'last_name', 'phone_number', 'password1', 'password2')

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if CustomUser.objects.filter(phone_number=phone_number).exists():
            raise ValidationError("This phone number is already in use. Please use a different one.")
        return phone_number

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.phone_number = self.cleaned_data['phone_number']
        if commit:
            user.save()
        return user




class UserProfileForm(forms.ModelForm):
    """Form for creating or updating user profile with enhanced UI."""
    date_of_birth = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'type': 'date', 
                'placeholder': 'Select your date of birth', 
                'class': 'form-control'
            }
        ),
        required=False
    )
    profile_picture = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        required=False
    )

    class Meta:
        model = UserProfile
        fields = [
            'first_name', 
            'last_name', 
            'phone_number', 
            'id_number', 
            'date_of_birth', 
            'address', 
            'town', 
            'county', 
            'passport_number', 
            'profile_picture'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'placeholder': 'Enter your first name', 
                'class': 'form-control'
            }),
            'last_name': forms.TextInput(attrs={
                'placeholder': 'Enter your last name', 
                'class': 'form-control'
            }),
            'phone_number': forms.NumberInput(attrs={
                'placeholder': 'Enter your phone number', 
                'class': 'form-control'
            }),
            'id_number': forms.TextInput(attrs={
                'placeholder': 'Enter your ID number', 
                'class': 'form-control'
            }),
            'address': forms.TextInput(attrs={
                'placeholder': 'Enter your address', 
                'class': 'form-control'
            }),
            'town': forms.TextInput(attrs={
                'placeholder': 'Enter your town', 
                'class': 'form-control'
            }),
            'county': forms.TextInput(attrs={
                'placeholder': 'Enter your county', 
                'class': 'form-control'
            }),
            
            'passport_number': forms.TextInput(attrs={
                'placeholder': 'Enter your passport number', 
                'class': 'form-control'
            }),
        }


class PasswordResetRequestForm(forms.Form):
    """Form for requesting password reset"""
    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'})
    )

class PasswordResetConfirmForm(forms.Form):
    """Form for confirming password reset"""
    reset_code = forms.CharField(
        max_length=6,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter 6-digit reset code'})
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'New Password'}),
        label="New Password"
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm New Password'}),
        label="Confirm New Password"
    )

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("new_password1")
        password2 = cleaned_data.get("new_password2")
        
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match")
        
        return cleaned_data
