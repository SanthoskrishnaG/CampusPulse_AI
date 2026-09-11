from django.contrib import admin
from .models import Club, ClubMembership, ClubAnnouncement, ClubAchievement

@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'category', 'faculty_coordinator', 'student_lead', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'code', 'skills_developed')

@admin.register(ClubMembership)
class ClubMembershipAdmin(admin.ModelAdmin):
    list_display = ('student', 'club', 'role', 'joined_at', 'is_approved')
    list_filter = ('role', 'is_approved')
    search_fields = ('student__student_id', 'club__name')

@admin.register(ClubAnnouncement)
class ClubAnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'club', 'created_at')

@admin.register(ClubAchievement)
class ClubAchievementAdmin(admin.ModelAdmin):
    list_display = ('title', 'club', 'competition', 'position', 'award_date')
