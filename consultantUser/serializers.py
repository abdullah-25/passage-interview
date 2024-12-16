from rest_framework import serializers
from .models import  RecurringAvailability, User,Consultant,Availability,Booking

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']

class ConsultantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consultant
        fields = ['first_name', 'last_name']

class AvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Availability
        fields = ['consultant', 'start_time', 'end_time', 'date', 'is_booked' ]

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['availability', 'user']

class RecurringAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = RecurringAvailability
        fields = ['consultant', 'day_of_week', 'start_time', 'end_time', 'is_active']

