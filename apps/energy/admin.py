from django.contrib import admin
from .models import EnergyMeter, EnergyReading, EnergyAnomaly

@admin.register(EnergyMeter)
class EnergyMeterAdmin(admin.ModelAdmin):
    list_display = ('meter_id', 'building_name', 'baseline_kwh', 'is_active')

@admin.register(EnergyReading)
class EnergyReadingAdmin(admin.ModelAdmin):
    list_display = ('meter', 'kwh_consumed', 'timestamp', 'temperature')

@admin.register(EnergyAnomaly)
class EnergyAnomalyAdmin(admin.ModelAdmin):
    list_display = ('meter', 'severity', 'anomaly_type', 'kwh_observed', 'kwh_expected', 'detected_at', 'resolved')
    list_filter = ('severity', 'anomaly_type', 'resolved')
