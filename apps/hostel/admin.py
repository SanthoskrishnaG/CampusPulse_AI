from django.contrib import admin
from .models import (
    Hostel, HostelBlock, HostelRoom, HostelFacility,
    HostelAnnouncement, HostelComplaint, HostelMaintenanceRequest,
    HostelMessMenu, HostelEvent
)

@admin.register(Hostel)
class HostelAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'category', 'floor_count', 'capacity', 'occupied_count', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'code')

@admin.register(HostelBlock)
class HostelBlockAdmin(admin.ModelAdmin):
    list_display = ('name', 'hostel', 'floor_count')
    list_filter = ('hostel',)

@admin.register(HostelRoom)
class HostelRoomAdmin(admin.ModelAdmin):
    list_display = ('room_number', 'hostel', 'block', 'floor', 'room_type', 'capacity', 'occupied', 'is_available')
    list_filter = ('hostel', 'room_type', 'floor')
    search_fields = ('room_number',)

@admin.register(HostelFacility)
class HostelFacilityAdmin(admin.ModelAdmin):
    list_display = ('name', 'hostel', 'category', 'status')
    list_filter = ('hostel', 'category', 'status')

@admin.register(HostelAnnouncement)
class HostelAnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'hostel', 'priority', 'is_public', 'created_at')
    list_filter = ('priority', 'is_public', 'created_at')

@admin.register(HostelComplaint)
class HostelComplaintAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'hostel', 'room_number', 'category', 'priority', 'status', 'created_at')
    list_filter = ('status', 'priority', 'category', 'hostel')
    search_fields = ('title', 'room_number', 'student__student_id')

@admin.register(HostelMaintenanceRequest)
class HostelMaintenanceRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'item', 'hostel', 'room_number', 'priority', 'status', 'created_at')
    list_filter = ('status', 'priority', 'hostel')
    search_fields = ('item', 'room_number')

@admin.register(HostelMessMenu)
class HostelMessMenuAdmin(admin.ModelAdmin):
    list_display = ('day_of_week', 'hostel', 'timing_info')

@admin.register(HostelEvent)
class HostelEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'hostel', 'event_date', 'location')
    list_filter = ('hostel', 'event_date')
