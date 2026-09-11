from django.db import models
from django.conf import settings

class Notification(models.Model):
    class Category(models.TextChoices):
        ACADEMIC_ALERT = 'ACADEMIC_ALERT', 'Academic Risk / Intervention'
        EVENT_REMINDER = 'EVENT_REMINDER', 'Event Registration & Pass'
        COMPLAINT_UPDATE = 'COMPLAINT_UPDATE', 'Complaint Status Triage'
        TRANSPORT_ALERT = 'TRANSPORT_ALERT', 'Bus Fleet & Transport Alert'
        ENERGY_ANOMALY = 'ENERGY_ANOMALY', 'Energy Spike / Anomaly'
        SYSTEM = 'SYSTEM', 'Campus Broadcast'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    category = models.CharField(max_length=40, choices=Category.choices, default=Category.SYSTEM)
    link_url = models.CharField(max_length=255, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.category}] {self.title} -> {self.user.username}"
