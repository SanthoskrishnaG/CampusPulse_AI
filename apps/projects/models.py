from django.db import models
from apps.students.models import Student
from apps.faculty.models import Faculty
from apps.departments.models import Department

class Project(models.Model):
    class Status(models.TextChoices):
        OPEN = 'OPEN', 'Looking for Teammates'
        IN_PROGRESS = 'IN_PROGRESS', 'Team Formed & In Progress'
        COMPLETED = 'COMPLETED', 'Completed & Evaluated'

    title = models.CharField(max_length=200)
    description = models.TextField()
    required_skills = models.CharField(max_length=255, help_text="Comma-separated skills (e.g. Python, Computer Vision, React, Django)")
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='projects')
    creator = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='created_projects')
    mentor = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True, blank=True, related_name='mentored_projects')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.department.code})"

    def get_skill_list(self):
        return [s.strip() for s in self.required_skills.split(',') if s.strip()]

class Team(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='team')
    name = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Team '{self.name}' for {self.project.title}"

class TeamMember(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='members')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='team_memberships')
    role_in_team = models.CharField(max_length=100, default="Core Developer")
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('team', 'student')

    def __str__(self):
        return f"{self.student.get_display_name()} - {self.role_in_team} ({self.team.name})"
