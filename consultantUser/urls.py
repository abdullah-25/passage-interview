from django.contrib import admin
from django.urls import path
from .views import *
urlpatterns = [
    path('consultants/<int:pk>/availabilities/', ConsultantAvailableTimeCreateView.as_view(), name='consultant-create-availability'),
     path('consultant/', ConsultantCreateView.as_view(), name='consultant-create'),
      path('consultant/<int:pk>/availability/', ConsultantGetAvailability.as_view(), name='consultant-availability'),
      path('consultants/availabilities/<str:date>/', DailyAvailabilityView.as_view()),
       path('consultant/<int:pk>/reserve/', ReserveConsultantTimeView.as_view(), name='consultant-booking-'),
       path('user/', UserCreateView.as_view(), name='user-create'),
       path('consultant/<int:pk>/availability/delete', ConsultantDeleteAvailability.as_view(), name='consultant-availability-delete'),
       path('availabilities/monthly/', MonthlyAvailabilityView.as_view(), name='monthly-availabilities'),
       path('availabilities/timerange/', TimeRangeAvailabilityView.as_view(), name='date-range-availabilities'),
        path('consultant/<int:pk>/recurring/', RecurringAvailabilityView.as_view(), name='consultant-recurring'),
]
