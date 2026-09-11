from django.contrib import admin
from .models import Project, Team, TeamMember

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'department', 'creator', 'mentor', 'status', 'created_at')
    list_filter = ('department', 'status')
    search_fields = ('title', 'required_skills', 'description')

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'created_at')

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('team', 'student', 'role_in_team', 'joined_at')
