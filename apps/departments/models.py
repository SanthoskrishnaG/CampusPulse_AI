from django.db import models

class Department(models.Model):
    name = models.CharField(max_length=150, unique=True)
    code = models.CharField(max_length=20, unique=True, help_text="e.g. CSE, IT, ECE, EEE, MECH, CIVIL, AIDS")
    hod_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    building = models.CharField(max_length=100, blank=True)
    established_year = models.PositiveIntegerField(default=2000)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['code']

    def __str__(self):
        return f"{self.name} ({self.code})"

class DepartmentAnnouncement(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='announcements')
    title = models.CharField(max_length=200)
    content = models.TextField()
    is_pinned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_pinned', '-created_at']

    def __str__(self):
        return f"[{self.department.code}] {self.title}"

class DepartmentResource(models.Model):
    class ResourceType(models.TextChoices):
        SYLLABUS = 'SYLLABUS', 'Syllabus'
        LAB_MANUAL = 'LAB_MANUAL', 'Laboratory Manual'
        TIMETABLE = 'TIMETABLE', 'Timetable'
        LECTURE_NOTES = 'LECTURE_NOTES', 'Lecture Notes'

    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='resources')
    title = models.CharField(max_length=200)
    resource_type = models.CharField(max_length=30, choices=ResourceType.choices, default=ResourceType.SYLLABUS)
    link = models.URLField(blank=True, help_text="Resource document URL or link")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.get_resource_type_display()})"
