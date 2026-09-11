from django.db import models
from django.conf import settings

class AuditLog(models.Model):
    """
    Centralized security and operational audit logging for all campus events.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    action = models.CharField(max_length=100, db_index=True)
    details = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        username = self.user.username if self.user else 'Anonymous/System'
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {username} -> {self.action}"

    @classmethod
    def log_action(cls, user, action, details="", ip_address=None):
        try:
            return cls.objects.create(
                user=user if user and user.is_authenticated else None,
                action=action,
                details=str(details),
                ip_address=ip_address
            )
        except Exception:
            # Audit logging failure must never crash core application
            return None

class CampusLocation(models.Model):
    """
    Canonical campus geographic landmarks, academic blocks, labs, canteens, bus stops, and parking lots.
    Stored directly in MySQL to eliminate dependence on third-party high-volume geocoding APIs.
    """
    class Category(models.TextChoices):
        ACADEMIC_BLOCK = 'ACADEMIC_BLOCK', 'Academic Block'
        DEPARTMENT = 'DEPARTMENT', 'Department Facility'
        LABORATORY = 'LABORATORY', 'Research / Computer Lab'
        CANTEEN = 'CANTEEN', 'Canteen / Dining Hall'
        PARKING = 'PARKING', 'Smart Parking Zone'
        BUS_STOP = 'BUS_STOP', 'Campus Bus Stop'
        AUDITORIUM = 'AUDITORIUM', 'Auditorium / Seminar Hall'
        SPORTS = 'SPORTS', 'Sports Complex / Ground'
        HOSTEL = 'HOSTEL', 'Student Hostel'
        ADMIN_BLOCK = 'ADMIN_BLOCK', 'Administrative Building'

    name = models.CharField(max_length=150)
    code = models.CharField(max_length=30, unique=True, help_text="e.g., BLK-A, LAB-CS1, PKG-EAST")
    category = models.CharField(max_length=40, choices=Category.choices, default=Category.ACADEMIC_BLOCK)
    latitude = models.FloatField()
    longitude = models.FloatField()
    floor_count = models.PositiveIntegerField(default=1)
    capacity = models.PositiveIntegerField(default=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"

class WeatherCache(models.Model):
    """
    Locally cached weather observations from free Open-Meteo API.
    """
    temperature = models.FloatField(help_text="Degrees Celsius")
    humidity = models.FloatField(default=60.0)
    precipitation = models.FloatField(default=0.0, help_text="mm")
    weather_code = models.IntegerField(default=0)
    weather_description = models.CharField(max_length=100, default="Clear Sky")
    wind_speed = models.FloatField(default=10.0, help_text="km/h")
    fetched_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.temperature}°C - {self.weather_description} at {self.fetched_at}"
