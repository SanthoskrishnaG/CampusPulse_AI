import uuid
from django.db import models
from django.utils import timezone
from apps.departments.models import Department
from apps.clubs.models import Club
from apps.students.models import Student
from apps.common.models import CampusLocation

class Event(models.Model):
    class EventType(models.TextChoices):
        DEPARTMENT_EVENT = 'DEPARTMENT_EVENT', 'Department Event'
        COLLEGE_EVENT = 'COLLEGE_EVENT', 'College-Wide Event'
        CLUB_EVENT = 'CLUB_EVENT', 'Club Activity'
        WORKSHOP = 'WORKSHOP', 'Hands-on Workshop'
        SEMINAR = 'SEMINAR', 'Technical Seminar / Guest Lecture'
        HACKATHON = 'HACKATHON', 'Hackathon / Code Sprint'
        COMPETITION = 'COMPETITION', 'Inter-College Competition'
        CULTURAL = 'CULTURAL', 'Cultural Fest'
        TECHNICAL = 'TECHNICAL', 'Technical Symposium'
        SPORTS = 'SPORTS', 'Sports Tournament'
        PLACEMENT = 'PLACEMENT', 'Placement / Industry Drive'

    class Status(models.TextChoices):
        UPCOMING = 'UPCOMING', 'Upcoming'
        ONGOING = 'ONGOING', 'Happening Now'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'

    title = models.CharField(max_length=200)
    description = models.TextField()
    event_type = models.CharField(max_length=40, choices=EventType.choices, default=EventType.WORKSHOP)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='events')
    club = models.ForeignKey(Club, on_delete=models.SET_NULL, null=True, blank=True, related_name='events')
    location = models.ForeignKey(CampusLocation, on_delete=models.SET_NULL, null=True, blank=True, related_name='events')
    location_name = models.CharField(max_length=150, default="Campus Auditorium")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    capacity = models.PositiveIntegerField(default=100)
    speaker = models.CharField(max_length=150, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.UPCOMING)
    
    # ML attendance forecasting fields
    predicted_attendance = models.PositiveIntegerField(default=75)
    predicted_no_show_rate = models.FloatField(default=15.0, help_text="Percentage")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['start_time']

    def __str__(self):
        return f"{self.title} ({self.get_event_type_display()})"

    def registration_count(self):
        return self.registrations.count()

    def attendance_count(self):
        return self.registrations.filter(attended=True).count()

    def is_registration_open(self):
        return self.status == self.Status.UPCOMING and self.start_time > timezone.now()

class EventRegistration(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='event_registrations')
    registered_at = models.DateTimeField(auto_now_add=True)
    attended = models.BooleanField(default=False)
    attended_at = models.DateTimeField(null=True, blank=True)
    qr_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    class Meta:
        unique_together = ('event', 'student')
        ordering = ['-registered_at']

    def __str__(self):
        return f"{self.student.student_id} -> {self.event.title}"

class EventFeedback(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='feedbacks')
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(default=5, help_text="1 to 5 Stars")
    comments = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'student')

    def __str__(self):
        return f"Feedback for {self.event.title} by {self.student.student_id} ({self.rating}/5)"

class Certificate(models.Model):
    certificate_id = models.CharField(max_length=60, unique=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='certificates')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='certificates')
    issued_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cert {self.certificate_id} - {self.student.student_id} ({self.event.title})"
