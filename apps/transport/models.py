from django.db import models

class BusRoute(models.Model):
    name = models.CharField(max_length=150, unique=True, help_text="e.g. Route 1 - Metro Central Express")
    code = models.CharField(max_length=20, unique=True, help_text="e.g. R-01")
    start_point = models.CharField(max_length=100)
    end_point = models.CharField(max_length=100, default="Campus Main Terminal")
    distance_km = models.FloatField(default=12.5)
    estimated_duration_mins = models.PositiveIntegerField(default=35)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['code']

    def __str__(self):
        return f"{self.code}: {self.name}"

class Bus(models.Model):
    bus_number = models.CharField(max_length=30, unique=True, help_text="e.g. KA-01-CP-1001")
    route = models.ForeignKey(BusRoute, on_delete=models.SET_NULL, null=True, blank=True, related_name='buses')
    driver_name = models.CharField(max_length=100)
    driver_phone = models.CharField(max_length=20, blank=True)
    capacity = models.PositiveIntegerField(default=52)
    current_passengers = models.PositiveIntegerField(default=28)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        route_name = self.route.code if self.route else "No Route"
        return f"{self.bus_number} ({route_name})"

    def occupancy_percentage(self):
        if self.capacity == 0:
            return 0.0
        return round((self.current_passengers / self.capacity) * 100.0, 1)

class BusStop(models.Model):
    route = models.ForeignKey(BusRoute, on_delete=models.CASCADE, related_name='stops')
    name = models.CharField(max_length=150)
    sequence = models.PositiveIntegerField(default=1)
    latitude = models.FloatField()
    longitude = models.FloatField()
    estimated_offset_mins = models.PositiveIntegerField(default=5)

    class Meta:
        ordering = ['route', 'sequence']

    def __str__(self):
        return f"{self.route.code} Stop #{self.sequence}: {self.name}"

class GPSRecord(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='gps_records')
    latitude = models.FloatField()
    longitude = models.FloatField()
    speed_kmh = models.FloatField(default=32.0)
    passenger_count = models.PositiveIntegerField(default=30)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.bus.bus_number} at ({self.latitude:.4f}, {self.longitude:.4f})"
