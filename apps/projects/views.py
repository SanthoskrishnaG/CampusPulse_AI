from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Project, Team, TeamMember
from apps.students.models import Student
from apps.departments.models import Department
from apps.recommendations.engine import RecommendationEngine

def project_list(request):
    projects = Project.objects.select_related('department', 'creator', 'mentor').all()
    q = request.GET.get('q')
    dept = request.GET.get('dept')

    if q:
        projects = projects.filter(title__icontains=q) | projects.filter(required_skills__icontains=q)
    if dept:
        projects = projects.filter(department__code=dept)

    return render(request, 'projects/list.html', {'projects': projects, 'departments': Department.objects.all()})

def project_detail(request, pk):
    project = get_object_or_404(Project.objects.select_related('department', 'creator', 'mentor'), pk=pk)
    team = getattr(project, 'team', None)
    team_members = team.members.select_related('student', 'student__user') if team else []

    # Recommended complementary teammates
    recommended_teammates = RecommendationEngine.recommend_teammates_for_project(project, limit=5)

    return render(request, 'projects/detail.html', {
        'project': project,
        'team': team,
        'team_members': team_members,
        'recommended_teammates': recommended_teammates
    })

@login_required
def create_project(request):
    student = getattr(request.user, 'student_profile', None)
    if not student:
        messages.error(request, "Only registered students can initiate capstone/research projects.")
        return redirect('projects:list')

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        required_skills = request.POST.get('required_skills')

        proj = Project.objects.create(
            title=title,
            description=description,
            required_skills=required_skills,
            department=student.department,
            creator=student,
            status=Project.Status.OPEN
        )

        team = Team.objects.create(project=proj, name=f"Team {title[:20]}")
        TeamMember.objects.create(team=team, student=student, role_in_team="Project Lead / Architect")

        messages.success(request, f"Project '{title}' announced! AI is now recommending complementary teammates.")
        return redirect('projects:detail', pk=proj.pk)

    return render(request, 'projects/create.html')
