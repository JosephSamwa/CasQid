#from django_countries.fields import CountryField
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import CustomUser
import requests
from urllib.parse import quote 



class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)
    flag_url = models.CharField(max_length=255, blank=True)
    currency_code = models.CharField(max_length=10, blank=True)
    country_code = models.CharField(max_length=3, blank=True)  # Store ISO 3166-1 alpha-3 code

    def save(self, *args, **kwargs):
        # Fetch all data in a single API call if needed
        if not self.country_code or not self.flag_url or not self.currency_code:
            self._fetch_country_data()
        super().save(*args, **kwargs)

    def _fetch_country_data(self):
        """Fetch all country data in a single API call"""
        try:
            encoded_name = quote(self.name)
            response = requests.get(f"https://restcountries.com/v3.1/name/{encoded_name}?fullText=true")
            
            if response.status_code != 200:
                print(f"Error fetching data for {self.name}: HTTP {response.status_code}")
                return
                
            data = response.json()
            if not data or not isinstance(data, list) or len(data) == 0:
                print(f"No data returned for {self.name}")
                return
                
            country_data = data[0]
            
            # Set country code if not already set
            if not self.country_code:
                self.country_code = country_data.get("cca3", "")
            
            # Set flag URL if not already set
            if not self.flag_url and "flags" in country_data:
                self.flag_url = country_data["flags"].get("png", "")
            
            # Set currency code if not already set
            if not self.currency_code and "currencies" in country_data:
                currencies = country_data["currencies"]
                if currencies:
                    self.currency_code = list(currencies.keys())[0]
                    
        except Exception as e:
            print(f"Error fetching data for {self.name}: {e}")
    
    def __str__(self):
        return self.name
        
class Job(models.Model):
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    commission_fee = models.DecimalField(max_digits=10, decimal_places=2, default=100000)
    job_type = models.CharField(max_length=50, choices=[
        ('Full-Time', 'Full-Time'), 
        ('Part-Time', 'Part-Time'), 
        ('Freelance', 'Freelance')
    ])
    industry = models.CharField(max_length=100)
    description = models.TextField()
    posted_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    experience_level = models.CharField(max_length=50, choices=[
        ('Entry', 'Entry Level'),
        ('Mid', 'Mid Level'),
        ('Senior', 'Senior Level'),
        ('Executive', 'Executive Level')
    ])
    required_skills = models.ManyToManyField('Skill', blank=True)
    remote_friendly = models.BooleanField(default=False)
    
    accommodation_available = models.BooleanField(default=True)
    transport = models.BooleanField(default=True)
    jobs_for_couples = models.BooleanField(default=True)
    
    vacancy_number = models.IntegerField(default=30)
    working_hours = models.CharField(max_length=50, blank=True, default="40 hours per week")
    processing_time = models.CharField(max_length=50, default="3 weeks")
    min_salary = models.IntegerField(null=True, blank=True)
    application_deadline = models.DateField(null=True, blank=True)
    company_rating = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.title} at {self.company}"

    def get_country_name(self):
        """Return the country name"""
        return self.country.name

class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=50, choices=[
        ('Technical', 'Technical'),
        ('Soft', 'Soft Skills'),
        ('Language', 'Language')
    ])
    def __str__(self):
        return self.name

class JobApplication(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    applicant = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    application_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=[
        ('Applied', 'Applied'),
        ('Screening', 'Screening'),
        ('Interview', 'Interview'),
        ('Offer', 'Offer'),
        ('Rejected', 'Rejected')
    ])
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)
    cover_letter = models.TextField(blank=True)

    def __str__(self):
        # Fix: Return a string instead of the user object
        return f"{self.applicant.username} - {self.job.title} ({self.status})"

