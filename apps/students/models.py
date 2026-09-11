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
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
