from django.db import models
from django.conf import settings
from apps.departments.models import Department

class Faculty(models.Model):
    class Designation(models.TextChoices):
        PROFESSOR = 'PROFESSOR', 'Professor'
        ASSOCIATE_PROF = 'ASSOCIATE_PROF', 'Associate Professor'
        ASSISTANT_PROF = 'ASSISTANT_PROF', 'Assistant Professor'
        LECTURER = 'LECTURER', 'Lecturer / Adjunct'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='faculty_profile'
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='faculty_members'
    )
    employee_id = models.CharField(max_length=50, unique=True)
    designation = models.CharField(max_length=50, choices=Designation.choices, default=Designation.ASSISTANT_PROF)
    specialization = models.CharField(max_length=200, blank=True)
    cabin_location = models.CharField(max_length=100, blank=True)
    office_hours = models.CharField(max_length=100, default="Mon-Fri 2:00 PM - 4:00 PM")
    is_mentor = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Faculty'
        ordering = ['user__first_name', 'user__last_name']

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.get_designation_display()} - {self.department.code})"
