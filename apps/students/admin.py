from django.contrib import admin
from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'get_display_name', 'department', 'program', 'semester', 'cgpa', 'attendance_percentage', 'backlog_count')
    list_filter = ('department', 'program', 'semester', 'backlog_count')
    search_fields = ('student_id', 'first_name', 'last_name', 'skills', 'interests')
