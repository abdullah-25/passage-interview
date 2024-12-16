from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.utils import timezone
from datetime import timedelta
from .models import Consultant, Availability

class ConsultantAvailabilityTests(APITestCase):
    def setUp(self):
        """Setup runs before each test method"""
        # Create a test consultant
        self.consultant = Consultant.objects.create(
            first_name="Test",
            last_name="Consultant"
        )
        
        # Get tomorrow's date for valid future date testing
        self.future_date = (timezone.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        self.past_date = (timezone.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    def test_create_availability_success(self):
        """Test creating availability with valid future date"""
        url = reverse('consultant-create-availability', kwargs={'pk': self.consultant.id})
        data = {
            'date': self.future_date,
            'start_time': '09:00:00',
            'end_time': '10:00:00'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Availability.objects.count(), 1)

    def test_create_availability_past_date(self):
        """Test creating availability with past date should fail"""
        url = reverse('consultant-create-availability', kwargs={'pk': self.consultant.id})
        data = {
            'date': self.past_date,
            'start_time': '09:00:00',
            'end_time': '10:00:00'
        }
        response = self.client.post(url, data, format='json')
        
        # Assert response is 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Assert error message is correct
        self.assertEqual(response.data['error'], 'Only future dates are allowed')
        # Assert no availability was created
        self.assertEqual(Availability.objects.count(), 0)