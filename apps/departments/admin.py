from django.contrib import admin
from .models import Department, DepartmentAnnouncement, DepartmentResource

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'hod_name', 'building', 'established_year', 'is_active')
    search_fields = ('name', 'code', 'hod_name')

@admin.register(DepartmentAnnouncement)
class DepartmentAnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'department', 'is_pinned', 'created_at')
    list_filter = ('department', 'is_pinned')
    search_fields = ('title', 'content')

@admin.register(DepartmentResource)
class DepartmentResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'department', 'resource_type', 'created_at')
    list_filter = ('department', 'resource_type')
