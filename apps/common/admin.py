from django.contrib import admin
from .models import AuditLog, CampusLocation, WeatherCache

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'action', 'ip_address')
    list_filter = ('action', 'timestamp')
    search_fields = ('action', 'details', 'user__username')
    readonly_fields = ('user', 'action', 'details', 'ip_address', 'timestamp')

@admin.register(CampusLocation)
class CampusLocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'category', 'latitude', 'longitude', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'code', 'description')

@admin.register(WeatherCache)
class WeatherCacheAdmin(admin.ModelAdmin):
    list_display = ('temperature', 'humidity', 'precipitation', 'weather_description', 'fetched_at')
    readonly_fields = ('fetched_at',)
