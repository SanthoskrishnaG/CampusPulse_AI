from django.db import models
from django.conf import settings

class Notification(models.Model):
    class Category(models.TextChoices):
        ACADEMIC_ALERT = 'ACADEMIC_ALERT', 'Academic Risk / Intervention'
        EVENT_REMINDER = 'EVENT_REMINDER', 'Event Registration & Pass'
        COMPLAINT_UPDATE = 'COMPLAINT_UPDATE', 'Complaint Status Triage'
        TRANSPORT_ALERT = 'TRANSPORT_ALERT', 'Bus Fleet & Transport Alert'
        ENERGY_ANOMALY = 'ENERGY_ANOMALY', 'Energy Spike / Anomaly'
        HOSTEL_ALERT = 'HOSTEL_ALERT', 'Hostel Resident Notice'
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

    @classmethod
    def notify_hostel_residents(cls, hostel, title, message, link_url='/hostel/'):
        """
        Dispatches private hostel notifications strictly to authorized resident students of that hostel.
        Never dispatches to Day Scholars or Faculty.
        """
        from apps.students.models import Student
        notifications_to_create = []
        residents = Student.objects.filter(
            assigned_hostel=hostel,
            accommodation_type=Student.AccommodationType.HOSTEL,
            user__isnull=False
        ).select_related('user')

        for student in residents:
            notifications_to_create.append(cls(
                user=student.user,
                title=title,
                message=message,
                category=cls.Category.HOSTEL_ALERT,
                link_url=link_url
            ))

        if notifications_to_create:
            cls.objects.bulk_create(notifications_to_create)
        return len(notifications_to_create)
