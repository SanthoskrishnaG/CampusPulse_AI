from django.contrib import admin
from .models import BusRoute, Bus, BusStop, GPSRecord

@admin.register(BusRoute)
class BusRouteAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'start_point', 'end_point', 'distance_km', 'estimated_duration_mins')

@admin.register(Bus)
class BusAdmin(admin.ModelAdmin):
    list_display = ('bus_number', 'route', 'driver_name', 'capacity', 'current_passengers', 'is_active')
    list_filter = ('route', 'is_active')

@admin.register(BusStop)
class BusStopAdmin(admin.ModelAdmin):
    list_display = ('name', 'route', 'sequence', 'latitude', 'longitude')
    list_filter = ('route',)
