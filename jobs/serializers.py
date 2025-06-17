from rest_framework import serializers
from .models import Destination, Attraction

class AttractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attraction
        fields = ['id', 'name', 'description', 'image']

class DestinationSerializer(serializers.ModelSerializer):
    attractions = AttractionSerializer(many=True, read_only=True)

    class Meta:
        model = Destination
        fields = ['id', 'name', 'slug', 'description', 'image', 'best_time_to_visit', 'latitude', 'longitude', 'average_rating', 'attractions']