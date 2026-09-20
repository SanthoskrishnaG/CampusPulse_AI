from django.db import models
from django.conf import settings
from apps.departments.models import Department

class Student(models.Model):
    """
    Unified Student Entity. Supports both linked authenticated user accounts
    and imported anonymized institutional datasets.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='student_profile'
    )
    student_id = models.CharField(max_length=50, unique=True, help_text="Anonymized ID e.g. STU2026-0042")
    first_name = models.CharField(max_length=100, default="Student")
    last_name = models.CharField(max_length=100, blank=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='students'
    )
    program = models.CharField(max_length=50, default='B.Tech')
    semester = models.PositiveIntegerField(default=5)
    section = models.CharField(max_length=10, default='A')
    admission_year = models.PositiveIntegerField(default=2023)
    academic_year = models.CharField(max_length=20, default='2025-2026')
    cgpa = models.FloatField(default=7.50)
    attendance_percentage = models.FloatField(default=82.0)
    skills = models.TextField(blank=True, help_text="Comma-separated skills (e.g. Python, Machine Learning, React, SQL)")
    interests = models.TextField(blank=True, help_text="Comma-separated interests (e.g. Robotics, NLP, Cyber Security)")
    career_interests = models.TextField(blank=True, help_text="Target role (e.g. Data Scientist, Cloud Architect)")
    backlog_count = models.PositiveIntegerField(default=0)

    # Campus Accommodation & Hostel Living
    class AccommodationType(models.TextChoices):
        HOSTEL = 'hostel', 'Hostel Student'
        DAY_SCHOLAR = 'day_scholar', 'Day Scholar'

    class HostelCategory(models.TextChoices):
        BOYS = 'boys', 'Boys Hostel'
        GIRLS = 'girls', 'Girls Hostel'

    accommodation_type = models.CharField(
        max_length=20,
        choices=AccommodationType.choices,
        default=AccommodationType.DAY_SCHOLAR,
        help_text="Hostel Student or Day Scholar"
    )
    hostel_category = models.CharField(
        max_length=10,
        choices=HostelCategory.choices,
        null=True,
        blank=True,
        help_text="boys or girls"
    )
    assigned_hostel = models.ForeignKey(
        'hostel.Hostel',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resident_students'
    )
    room_number = models.CharField(max_length=20, blank=True, help_text="e.g. B-204")
    is_accommodation_configured = models.BooleanField(
        default=False,
        help_text="Whether student completed accommodation onboarding"
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        super().clean()
        from django.core.exceptions import ValidationError
        if self.accommodation_type == self.AccommodationType.DAY_SCHOLAR:
            self.hostel_category = None
            self.assigned_hostel = None
            self.room_number = ''
        elif self.accommodation_type == self.AccommodationType.HOSTEL:
            if not self.hostel_category or self.hostel_category not in [self.HostelCategory.BOYS, self.HostelCategory.GIRLS]:
                raise ValidationError({'hostel_category': "Hostel students must select either Boys Hostel or Girls Hostel category."})
            if self.assigned_hostel:
                expected_cat = 'boys' if self.hostel_category == self.HostelCategory.BOYS else 'girls'
                if self.assigned_hostel.category != expected_cat:
                    raise ValidationError({'assigned_hostel': f"Selected hostel '{self.assigned_hostel.name}' does not match your category ({self.get_hostel_category_display()})."})

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['student_id']

    def __str__(self):
        name = self.get_display_name()
        return f"{self.student_id} - {name} ({self.department.code})"

    def get_display_name(self):
        if self.user:
            return self.user.get_full_name() or self.user.username
        return f"{self.first_name} {self.last_name}".strip()

    def get_skill_list(self):
        if not self.skills:
            return []
        return [s.strip() for s in self.skills.split(',') if s.strip()]

    def get_interest_list(self):
        if not self.interests:
            return []
        return [i.strip() for i in self.interests.split(',') if i.strip()]
