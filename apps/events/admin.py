from django.contrib import admin
from .models import Event, EventRegistration, EventFeedback, Certificate

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_type', 'department', 'club', 'start_time', 'capacity', 'predicted_attendance', 'status')
    list_filter = ('event_type', 'status', 'department')
    search_fields = ('title', 'description', 'speaker')

@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ('event', 'student', 'registered_at', 'attended', 'attended_at')
    list_filter = ('attended', 'registered_at')
    search_fields = ('student__student_id', 'event__title')

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('certificate_id', 'student', 'event', 'issued_at')
