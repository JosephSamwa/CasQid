from rest_framework import serializers
from .models import Booking, Payment

class BookingSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Booking
        fields = ['id', 'user', 'trip', 'date_booked', 'status', 'status_display', 'total_price', 'special_requests', 'number_of_travelers']
        read_only_fields = ['user', 'date_booked']

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'booking', 'amount', 'payment_date', 'payment_method', 'transaction_id']
        read_only_fields = ['payment_date']