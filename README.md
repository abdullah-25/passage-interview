# Consultant Calendar API

## Overview
A Django REST API system that manages consultant availabilities and bookings. The system enables consultants to set their availability slots (both one-time and recurring) and allows users to book appointments.

## Table of Contents
- [Models](#models)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Development Setup](#development-setup)
- [Production Considerations](#production-considerations)

## Models

### Core Models

#### User
- Basic user model for customers who can book consultations
```python
class User(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
```

#### Consultant
- Represents service providers
```python
class Consultant(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
```

#### Availability
- Single time slots for consultants
```python
class Availability(models.Model):
    consultant = models.ForeignKey(Consultant, on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()
    date = models.DateField()
    is_booked = models.BooleanField(default=False)
```

#### RecurringAvailability
- Weekly patterns for consultant availability
```python
class RecurringAvailability(models.Model):
    DAYS_OF_WEEK = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday')
    ]
    consultant = models.ForeignKey(Consultant, on_delete=models.CASCADE)
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)
```

#### Booking
- Links users with availabilities
```python
class Booking(models.Model):
    availability = models.OneToOneField(Availability, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
```

### Design Decisions

1. **Separate User and Consultant Models**
   - Clear separation of roles
   - Independent model evolution
   - Distinct attributes and behaviors

2. **Dual Availability Models**
   - Availability: Single slots for flexibility
   - RecurringAvailability: Patterns for convenience
   - Optimized querying for each use case

3. **Independent Booking Model**
   - Better than simple flag on Availability
   - Supports booking metadata
   - Easier historical tracking
   - Extensible for future features

## API Endpoints

### Consultant Management
```
POST /consultant/ 
GET /consultant/<id>/
```

### Availability Management
```
POST /consultants/<id>/availabilities/    # Create slot
GET /consultant/<id>/availability/        # Get slots
GET /consultants/availabilities/<date>/   # Daily view
DELETE /consultant/<id>/availability/     # Remove slot
```

### Recurring Availability
```
POST /consultant/<id>/recurring/          # Set pattern
GET /consultant/<id>/recurring/           # View patterns
```

### Booking
```
POST /consultant/<id>/reserve/            # Book slot
```

### Calendar Views
```
GET /availabilities/monthly/              # Monthly view
GET /availabilities/timerange/            # Date range view
```

## Testing

### Current Test Coverage
```python
class ConsultantAvailabilityTests(APITestCase):
    def setUp(self):
        # Setup test data
        self.consultant = Consultant.objects.create(
            first_name="Test",
            last_name="Consultant"
        )
        
    def test_create_availability(self):
        # Test availability creation
        pass

    def test_get_availability(self):
        # Test availability retrieval
        pass
```

### Test with CURL

#### 1. Create Entities
```bash
# Create consultant
curl -X POST http://localhost:8000/consultant/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe"
  }'

# Create user
curl -X POST http://localhost:8000/user/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Jane",
    "last_name": "Smith"
  }'
```

#### 2. Manage Availability
```bash
# Create availability
curl -X POST http://localhost:8000/consultants/1/availabilities/ \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2024-12-25",
    "start_time": "09:00:00",
    "end_time": "10:00:00"
  }'

# Get consultant's availability
curl -X GET http://localhost:8000/consultant/1/availability/
```


## Production Considerations

### Database Optimization

#### Indexing
```python
# Add to models.py
class Availability(models.Model):
    class Meta:
        indexes = [
            models.Index(fields=['consultant', 'date', 'is_booked']),
            models.Index(fields=['date', 'is_booked']),
        ]
```

#### Query Optimization
- Use `select_related()` for foreign keys
- Implement pagination
- Cache frequent queries
- Use database connection pooling


## Development Setup

### Prerequisites
- Python 3.8+
- Django 4.0+


### Installation
```bash
# Clone repository
git clone [repository-url]

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start development server
python manage.py runserver
```
