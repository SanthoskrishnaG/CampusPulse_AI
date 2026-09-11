from django.db import models

class EnergyMeter(models.Model):
    name = models.CharField(max_length=150, help_text="e.g. Block C Computer Science")
    meter_id = models.CharField(max_length=50, unique=True, help_text="e.g. MTR-BLK-C-01")
    building_name = models.CharField(max_length=100)
    baseline_kwh = models.FloatField(default=45.0, help_text="Expected daytime base load (kWh)")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.meter_id})"

class EnergyReading(models.Model):
    meter = models.ForeignKey(EnergyMeter, on_delete=models.CASCADE, related_name='readings')
    kwh_consumed = models.FloatField(help_text="kWh")
    timestamp = models.DateTimeField(auto_now_add=True)
    temperature = models.FloatField(default=28.0)
    occupancy_estimate = models.PositiveIntegerField(default=120)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.meter.meter_id}: {self.kwh_consumed} kWh at {self.timestamp}"

class EnergyAnomaly(models.Model):
    class Severity(models.TextChoices):
        MILD = 'MILD', 'Mild Anomaly'
        MODERATE = 'MODERATE', 'Moderate Anomaly'
        CRITICAL = 'CRITICAL', 'Critical Waste / Power Surge'

    class AnomalyType(models.TextChoices):
        NIGHT_LEAK = 'NIGHT_LEAK', 'Night-time Idle Waste (Equipment Left ON)'
        POWER_SURGE = 'POWER_SURGE', 'Sudden Electrical Power Surge'
        HVAC_OVERLOAD = 'HVAC_OVERLOAD', 'HVAC / Cooling Overload'
        EQUIPMENT_FAULT = 'EQUIPMENT_FAULT', 'Suspected Machinery / UPS Fault'

    meter = models.ForeignKey(EnergyMeter, on_delete=models.CASCADE, related_name='anomalies')
    reading = models.ForeignKey(EnergyReading, on_delete=models.CASCADE, null=True, blank=True)
    anomaly_score = models.FloatField(help_text="Isolation score (-1 to 0 or 0 to 100)")
    kwh_observed = models.FloatField()
    kwh_expected = models.FloatField()
    severity = models.CharField(max_length=20, choices=Severity.choices, default=Severity.MODERATE)
    anomaly_type = models.CharField(max_length=30, choices=AnomalyType.choices, default=AnomalyType.NIGHT_LEAK)
    explanation = models.TextField()
    detected_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)

    class Meta:
        ordering = ['-detected_at']

    def __str__(self):
        return f"ANOMALY [{self.severity}]: {self.meter.building_name} ({self.kwh_observed} kWh vs exp {self.kwh_expected} kWh)"
