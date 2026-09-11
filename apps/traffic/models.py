from django.db import models
from apps.common.models import CampusLocation

class TrafficObservation(models.Model):
    class Congestion(models.TextChoices):
        CLEAR = 'CLEAR', 'Free Flow (Clear)'
        MODERATE = 'MODERATE', 'Moderate Traffic'
        HEAVY = 'HEAVY', 'Heavy Traffic'
        CONGESTED = 'CONGESTED', 'Campus Gate Bottleneck / Congested'

    location_name = models.CharField(max_length=150, default="Campus Main Gate North")
    image = models.ImageField(upload_to='traffic_uploads/', null=True, blank=True)
    total_vehicles = models.PositiveIntegerField(default=0)
    car_count = models.PositiveIntegerField(default=0)
    motorcycle_count = models.PositiveIntegerField(default=0)
    bus_count = models.PositiveIntegerField(default=0)
    truck_count = models.PositiveIntegerField(default=0)
    congestion_level = models.CharField(max_length=30, choices=Congestion.choices, default=Congestion.CLEAR)
    confidence = models.FloatField(default=0.88)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.location_name} - {self.total_vehicles} vehicles [{self.congestion_level}]"
