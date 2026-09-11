from django.contrib import admin
from .models import Course, CourseOffering, Enrollment, WeeklyPerformanceRecord, AcademicRiskAssessment, AcademicIntervention

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'department', 'credits', 'semester')
    list_filter = ('department', 'semester')
    search_fields = ('code', 'name')

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course_offering', 'attendance_percentage', 'internal_marks', 'grade')
    list_filter = ('grade',)
    search_fields = ('student__student_id', 'course_offering__course__code')

@admin.register(WeeklyPerformanceRecord)
class WeeklyPerformanceRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'week_number', 'attendance_rate', 'quiz_score', 'assignment_score', 'lms_activity_hours')
    list_filter = ('week_number',)

@admin.register(AcademicRiskAssessment)
class AcademicRiskAssessmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'risk_level', 'risk_score', 'confidence', 'model_name', 'assessed_at')
    list_filter = ('risk_level', 'model_name')
    search_fields = ('student__student_id',)

@admin.register(AcademicIntervention)
class AcademicInterventionAdmin(admin.ModelAdmin):
    list_display = ('student', 'intervention_type', 'faculty', 'status', 'created_at')
    list_filter = ('intervention_type', 'status')
