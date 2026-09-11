from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

class Complaint(models.Model):
    class Category(models.TextChoices):
        ELECTRICAL = 'ELECTRICAL', 'Electrical & Lighting'
        WATER = 'WATER', 'Water Supply & Plumbing'
        SANITATION = 'SANITATION', 'Sanitation & Hygiene'
        CLASSROOM = 'CLASSROOM', 'Classroom Infrastructure'
        LABORATORY = 'LABORATORY', 'Laboratory Equipment'
        TRANSPORT = 'TRANSPORT', 'Campus Transport & Buses'
        HOSTEL = 'HOSTEL', 'Hostel Facility'
        CANTEEN = 'CANTEEN', 'Canteen & Food Quality'
        PARKING = 'PARKING', 'Parking & Traffic'
        NETWORK = 'NETWORK', 'Wi-Fi & Campus Network'
        SECURITY = 'SECURITY', 'Campus Security'
        ACADEMIC = 'ACADEMIC', 'Academic / Timetable'
        INFRASTRUCTURE = 'INFRASTRUCTURE', 'General Campus Infrastructure'
        OTHER = 'OTHER', 'Other Issues'

    class Priority(models.TextChoices):
        LOW = 'LOW', 'Low'
        MEDIUM = 'MEDIUM', 'Medium'
        HIGH = 'HIGH', 'High'
        URGENT = 'URGENT', 'Urgent / Critical'

    class Status(models.TextChoices):
        SUBMITTED = 'SUBMITTED', 'Submitted (AI Triaged)'
        ASSIGNED = 'ASSIGNED', 'Assigned to Staff'
        IN_PROGRESS = 'IN_PROGRESS', 'Work in Progress'
        RESOLVED = 'RESOLVED', 'Resolved'
        REJECTED = 'REJECTED', 'Closed / Inapplicable'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='complaints')
    title = models.CharField(max_length=200)
    description = models.TextField(help_text="Detailed complaint in natural language")
    
    # AI Extracted / Predicted Attributes
    category = models.CharField(max_length=30, choices=Category.choices, default=Category.INFRASTRUCTURE)
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.MEDIUM)
    target_department = models.CharField(max_length=100, default="Maintenance")
    location_extracted = models.CharField(max_length=150, blank=True, help_text="AI-extracted building/room location")
    confidence = models.FloatField(default=0.85)

    # Workflow & SLA Tracking
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SUBMITTED)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_complaints'
    )
    resolution_notes = models.TextField(blank=True)
    sla_hours = models.PositiveIntegerField(default=24)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"CMP-{self.id:04d}: {self.title} [{self.category} - {self.priority}]"

    def is_overdue(self):
        if self.status in [self.Status.RESOLVED, self.Status.REJECTED]:
            return False
        deadline = self.created_at + timedelta(hours=self.sla_hours)
        return timezone.now() > deadline

    def get_deadline(self):
        return self.created_at + timedelta(hours=self.sla_hours)

class ComplaintStatusHistory(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='history')
    status = models.CharField(max_length=20)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    comments = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"CMP-{self.complaint.id} -> {self.status} at {self.timestamp}"
