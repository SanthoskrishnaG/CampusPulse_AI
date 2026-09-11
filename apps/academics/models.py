import json
from django.db import models
from apps.departments.models import Department
from apps.students.models import Student

class Course(models.Model):
    code = models.CharField(max_length=20, unique=True, help_text="e.g., CS501, AI402")
    name = models.CharField(max_length=150)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses')
    credits = models.PositiveIntegerField(default=3)
    semester = models.PositiveIntegerField(default=5)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

class CourseOffering(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='offerings')
    faculty = models.ForeignKey('faculty.Faculty', on_delete=models.CASCADE, related_name='course_offerings')
    academic_year = models.CharField(max_length=20, default='2025-2026')
    semester = models.PositiveIntegerField(default=5)

    def __str__(self):
        return f"{self.course.code} ({self.faculty.user.get_full_name() or self.faculty.employee_id})"

class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    course_offering = models.ForeignKey(CourseOffering, on_delete=models.CASCADE, related_name='enrollments')
    attendance_percentage = models.FloatField(default=85.0)
    internal_marks = models.FloatField(default=75.0, help_text="Out of 100")
    grade = models.CharField(max_length=5, default='B+')

    class Meta:
        unique_together = ('student', 'course_offering')

    def __str__(self):
        return f"{self.student.student_id} -> {self.course_offering.course.code}"

class WeeklyPerformanceRecord(models.Model):
    """
    Temporal student behavior data (Week 1 -> 5...16) used for Sequential Deep Learning (LSTM/GRU).
    Captures declining or improving engagement patterns without data leakage.
    """
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='weekly_records')
    week_number = models.PositiveIntegerField()
    attendance_rate = models.FloatField(help_text="Weekly attendance % (0-100)")
    quiz_score = models.FloatField(help_text="Weekly quiz score (0-100)")
    assignment_score = models.FloatField(help_text="Weekly assignment score (0-100)")
    lms_activity_hours = models.FloatField(default=4.0)

    class Meta:
        ordering = ['student', 'week_number']
        unique_together = ('student', 'week_number')

    def __str__(self):
        return f"{self.student.student_id} W{self.week_number} (Att: {self.attendance_rate}%, Quiz: {self.quiz_score})"

class AcademicRiskAssessment(models.Model):
    class RiskLevel(models.TextChoices):
        LOW = 'LOW', 'Low Risk (Healthy Progress)'
        MEDIUM = 'MEDIUM', 'Moderate Risk (Attention Needed)'
        HIGH = 'HIGH', 'High Academic Risk (Critical Intervention)'

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='risk_assessments')
    risk_level = models.CharField(max_length=20, choices=RiskLevel.choices, default=RiskLevel.LOW)
    risk_score = models.FloatField(default=15.0, help_text="Estimated failure/dropout risk % (0-100)")
    confidence = models.FloatField(default=0.88)
    model_name = models.CharField(max_length=100, default="RandomForest-Ensemble-v1")
    contributing_factors_json = models.TextField(default='[]', help_text="JSON list of top explainable factors")
    recommended_action = models.TextField(default="Regular coursework progression.")
    assessed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-assessed_at']

    def get_factors(self):
        try:
            return json.loads(self.contributing_factors_json)
        except Exception:
            return ["Coursework monitoring recommended"]

    def __str__(self):
        return f"{self.student.student_id} - {self.risk_level} ({self.risk_score:.1f}%)"

class AcademicIntervention(models.Model):
    class InterventionType(models.TextChoices):
        REMEDIAL_CLASS = 'REMEDIAL_CLASS', 'Remedial Session'
        FACULTY_MENTORING = 'FACULTY_MENTORING', 'Faculty 1-on-1 Mentoring'
        ASSIGNMENT_SUPPORT = 'ASSIGNMENT_SUPPORT', 'Assignment Extension / Lab Support'
        ATTENDANCE_WARNING = 'ATTENDANCE_WARNING', 'Attendance Warning Notice'
        PEER_TUTORING = 'PEER_TUTORING', 'Peer Tutor Assignment'

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending Action'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        RESOLVED = 'RESOLVED', 'Completed / Resolved'

    assessment = models.ForeignKey(AcademicRiskAssessment, on_delete=models.SET_NULL, null=True, blank=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='interventions')
    faculty = models.ForeignKey('faculty.Faculty', on_delete=models.SET_NULL, null=True, blank=True)
    intervention_type = models.CharField(max_length=40, choices=InterventionType.choices, default=InterventionType.FACULTY_MENTORING)
    notes = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Intervention for {self.student.student_id} ({self.get_intervention_type_display()}) - {self.status}"
