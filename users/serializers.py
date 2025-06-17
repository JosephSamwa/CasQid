from rest_framework import serializers
from .models import CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'bio', 'profile_image', 'date_of_birth', 'location', 'preferred_language', 'travel_preferences']
        read_only_fields = ['username', 'email']

class CustomUserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'bio', 'profile_image', 'date_of_birth', 'location', 'preferred_language', 'travel_preferences']