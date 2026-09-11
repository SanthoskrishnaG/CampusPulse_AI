from django.contrib import admin
from .models import Faculty

@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'user', 'department', 'designation', 'specialization', 'is_mentor')
    list_filter = ('department', 'designation', 'is_mentor')
    search_fields = ('employee_id', 'user__first_name', 'user__last_name', 'specialization')
