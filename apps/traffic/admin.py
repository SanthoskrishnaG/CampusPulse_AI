from django.contrib import admin
from .models import TrafficObservation

@admin.register(TrafficObservation)
class TrafficObservationAdmin(admin.ModelAdmin):
    list_display = ('location_name', 'total_vehicles', 'car_count', 'motorcycle_count', 'bus_count', 'congestion_level', 'timestamp')
    list_filter = ('congestion_level',)
