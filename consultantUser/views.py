from django.utils import timezone
from rest_framework.response import Response

from consultantUser.models import Availability, Consultant, RecurringAvailability
from consultantUser.serializers import AvailabilitySerializer, BookingSerializer,ConsultantSerializer, RecurringAvailabilitySerializer, UserSerializer
from rest_framework.views import APIView, status

from django.utils.dateparse import parse_date, parse_time

from django.db import transaction


class UserCreateView(APIView):
    """
    Create a new user in the system.
    """
    def post(self, request):
        serializer = UserSerializer(data={
            'first_name': request.data.get('first_name'),
            'last_name': request.data.get('last_name'),
        })
        
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'message': 'User created successfully'},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class ConsultantCreateView(APIView):
    """
    Create a consultant.
    """

    def post(self, request):
        serializer = ConsultantSerializer(data={
                
                            'first_name': request.data.get('first_name'),
                             'last_name': request.data.get('last_name'),
                              
                        })
                        
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Consutlant created successfully'}, 
                                        status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ConsultantAvailableTimeCreateView(APIView):
    """
    Create an available time slot for future reservations for a specific consultant.
    """

    def post(self, request, pk):
        try:
            consultant = Consultant.objects.get(id=pk)

            # Validate date is in future
            date = request.data.get('date')
            if parse_date(date) <= timezone.now().date():
                return Response(
                    {'error': 'Only future dates are allowed'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer = AvailabilitySerializer(data={
                            'consultant': pk,
                            'start_time': request.data.get('start_time'),
                            'end_time': request.data.get('end_time'),
                            'date': request.data.get('date'),
                            'is_booked': False,  # at the time of availability creation, assume that the slot isnt booked
                        })
                        
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {'message': 'Future availability slot created successfully'}, 
                    status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Consultant.DoesNotExist:
            return Response(
                {'error': 'Consultant not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {f"error: 'Failed to create availability slot due to {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

   

class ConsultantGetAvailability(APIView):
    """
    Retrieve all available time slots for a specific consultant.
    """

    def get(self, request, pk):

        try:
            consultant = Consultant.objects.get(id=pk)

            availabilities = Availability.objects.filter(
                consultant=consultant,
                is_booked=False
            ).order_by('date', 'start_time')  # so that result is ordered

            serializer = AvailabilitySerializer(availabilities, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Consultant.DoesNotExist:
            return Response(
                {'error': 'Consultant not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'An unexpected error occurred: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
       

class DailyAvailabilityView(APIView):
    """
    Retrieve all available time slots for all consultants on a specific date.

    Example:
        GET /consultants/availabilities/2024-12-25/
    """
    def get(self, request, date):
        if not date:
            return Response(
                {'error': 'Date parameter is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            parsed_date = parse_date(date)
            if not parsed_date:
                raise ValueError("Invalid date format")

            # Check if date is in past
            if parsed_date < timezone.now().date():
                return Response(
                    {'error': 'Cannot query availability for past dates'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            available_slots = Availability.objects.filter(
                date=parsed_date,
                is_booked=False
            ).order_by('start_time')

            serializer = AvailabilitySerializer(available_slots, many=True)

            response_data = {
                'date': date,
                'total_slots': len(serializer.data),
                'availabilities': serializer.data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response(
                {'error': f'Invalid date format. Use YYYY-MM-DD. Details: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        except Exception as e:
            return Response(
                {'error': f'An unexpected error occurred: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class ReserveConsultantTimeView(APIView):
    """
    Reserve an available time slot for a consultant
    """

    def post(self, request, pk):
        try:
            consultant = Consultant.objects.get(id=pk)
        
            with transaction.atomic():
                # Find available slot
                available_slot = Availability.objects.select_for_update().get(
                    consultant_id=pk,
                    date=request.data.get('date'),
                    start_time=request.data.get('start_time'),
                    end_time=request.data.get('end_time'),
                    is_booked=False
                )
                
                # Create booking using serializer
                serializer = BookingSerializer(data={
                    'availability': available_slot.id,
                    'user': request.data.get('user'),
                    'consultant': pk,
                    'date': request.data.get('date'),
                    'start_time': request.data.get('start_time'),
                    'end_time': request.data.get('end_time')
                })
                
                if serializer.is_valid():
                    booking = serializer.save()
                    # Update availability status
                    available_slot.is_booked = True
                    available_slot.save()
                    
                    return Response(
                        {'message': 'Booking created successfully',
                        'booking': serializer.data}, 
                        status=status.HTTP_201_CREATED
                    )
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Availability.DoesNotExist:
            return Response(
                {'error': 'Time slot not available'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Booking failed: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
       
class ConsultantDeleteAvailability(APIView):
    """
    Delete an availability time slot for a consultant.
    """
    def delete(self, request, pk):
        try:
            availability = Availability.objects.get(
                consultant_id=pk,
                date=request.data.get('date'),
                start_time=request.data.get('start_time'),
                end_time=request.data.get('end_time')
            )
        
            availability.delete()
            
            return Response(
                {'message': 'Time slot deleted successfully'},
                status=status.HTTP_204_NO_CONTENT
            )
            
        except Availability.DoesNotExist:
            return Response(
                {'error': 'Time slot not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Deletion failed: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

class MonthlyAvailabilityView(APIView):
    """
    Get all available time slots for all consultants in a specific month.
    """
    def get(self, request):
        month = request.query_params.get('month')
        year = request.query_params.get('year')

        try:
            month = int(month)
            year = int(year)
            
            if not (1 <= month <= 12):
                raise ValueError("Month must be between 1 and 12")
                
            import calendar
            from datetime import date
            
            # Get start and end dates for the month
            _, last_day = calendar.monthrange(year, month)
            start_date = date(year, month, 1)
            end_date = date(year, month, last_day)
            
           
            available_slots = Availability.objects.filter(
                date__gte=start_date,
                date__lte=end_date,
                is_booked=False
            ).order_by('date', 'start_time')
            
            serializer = AvailabilitySerializer(available_slots, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid month or year format'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
class TimeRangeAvailabilityView(APIView):
    """
    Get all available slots within a specified date AND time range.
    """
    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        start_time = request.query_params.get('start_time')
        end_time = request.query_params.get('end_time')

        if not all([start_date, end_date, start_time, end_time]):
            return Response(
                {'error': 'All parameters (start_date, end_date, start_time, end_time) are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            parsed_start_date = parse_date(start_date)
            parsed_end_date = parse_date(end_date)
            parsed_start_time = parse_time(start_time)
            parsed_end_time = parse_time(end_time)

            if not all([parsed_start_date, parsed_end_date, parsed_start_time, parsed_end_time]):
                raise ValueError("Invalid date or time format")

            
            available_slots = Availability.objects.filter(
                date__gte=parsed_start_date,
                date__lte=parsed_end_date,
                start_time__gte=parsed_start_time,
                end_time__lte=parsed_end_time,
                is_booked=False
            ).order_by('date', 'start_time')

            serializer = AvailabilitySerializer(available_slots, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except ValueError:
            return Response(
                {'error': 'Invalid format. Use YYYY-MM-DD for dates and HH:MM:SS for times'},
                status=status.HTTP_400_BAD_REQUEST
            )
        

class RecurringAvailabilityView(APIView):
    """
    Manage recurring availability slots for consultants.
    
    This view handles both creation and retrieval of recurring availability patterns.
    Recurring availabilities allow consultants to set regular weekly time slots
    instead of individual dates.
    """
    def post(self, request, pk):
        """
        Create a recurring availability slot for a consultant.

        Example:
            POST /consultant/1/recurring/
            {
                "day_of_week": 1,
                "start_time": "09:00:00",
                "end_time": "10:00:00"
            }
        """
        try:
            serializer = RecurringAvailabilitySerializer(data={
                'consultant': pk,
                'day_of_week': request.data.get('day_of_week'),
                'start_time': request.data.get('start_time'),
                'end_time': request.data.get('end_time')
            })
            
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {'message': 'Recurring availability created successfully'},
                    status=status.HTTP_201_CREATED
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Consultant.DoesNotExist:
            return Response(
                {'error': 'Consultant not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    def get(self, request, pk):
        """
        Retrieve all active recurring availability slots for a consultant.

        Example:
            GET /consultant/1/recurring/
        """
        recurring_slots = RecurringAvailability.objects.filter(
            consultant_id=pk,
            is_active=True
        )
        serializer = RecurringAvailabilitySerializer(recurring_slots, many=True)
        return Response(serializer.data)