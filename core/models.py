from django.db import models

class Partner(models.Model):
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='partners/')
    url = models.URLField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0, help_text="Order of display")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'name']
        
    def __str__(self):
        return self.name

class Service(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    icon = models.CharField(max_length=50, help_text="Font Awesome icon class (e.g., 'fa-briefcase')")
    order = models.PositiveIntegerField(default=0, help_text="Order of display")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'name']
        
    def __str__(self):
        return self.name

class Stat(models.Model):
    name = models.CharField(max_length=255)
    value = models.PositiveIntegerField()
    icon = models.CharField(max_length=50, help_text="Font Awesome icon class (optional)", blank=True, null=True)
    order = models.PositiveIntegerField(default=0, help_text="Order of display")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'name']
        
    def __str__(self):
        return f"{self.name}: {self.value}"
