from django.db import models


class User(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)


class Consultant(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)


class Availability(models.Model):
    consultant = models.ForeignKey(Consultant, on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()
    date = models.DateField()
    is_booked = models.BooleanField(default=False)


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


class Booking(models.Model):
    availability = models.OneToOneField(Availability, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
