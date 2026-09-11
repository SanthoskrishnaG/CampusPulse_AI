from django.contrib import admin
from .models import Complaint, ComplaintStatusHistory

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'priority', 'target_department', 'status', 'created_at')
    list_filter = ('category', 'priority', 'status')
    search_fields = ('title', 'description', 'location_extracted')

@admin.register(ComplaintStatusHistory)
class ComplaintStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('complaint', 'status', 'updated_by', 'timestamp')
