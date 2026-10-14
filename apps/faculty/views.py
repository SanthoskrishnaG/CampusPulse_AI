from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Faculty
from apps.accounts.decorators import role_required

@login_required
def faculty_dashboard(request):
    """
    Faculty Portal: displays monitored student risk assessments, courses handled,
    and assigned academic interventions.
    """
    faculty = getattr(request.user, 'faculty_profile', None)
    from apps.academics.models import CourseOffering, AcademicRiskAssessment, AcademicIntervention

    if faculty:
        courses = CourseOffering.objects.filter(faculty=faculty)
        interventions = AcademicIntervention.objects.filter(faculty=faculty).order_by('-created_at')[:10]
        # At-risk students in faculty's department
        at_risk_assessments = AcademicRiskAssessment.objects.filter(
            student__department=faculty.department
        ).select_related('student', 'student__user', 'student__department').order_by('-risk_score')[:15]
    else:
        courses = []
        interventions = AcademicIntervention.objects.all().order_by('-created_at')[:10]
        at_risk_assessments = AcademicRiskAssessment.objects.select_related('student', 'student__user', 'student__department').order_by('-risk_score')[:15]

    context = {
        'faculty': faculty,
        'courses': courses,
        'interventions': interventions,
        'at_risk_assessments': at_risk_assessments,
    }
    return render(request, 'faculty/dashboard.html', context)

def faculty_list(request):
    from apps.departments.models import Department
    departments = Department.objects.filter(is_active=True).order_by('code')
    faculty_members = Faculty.objects.select_related('user', 'department').all().order_by('user__first_name', 'user__last_name')
    dept = request.GET.get('dept')
    if dept:
        faculty_members = faculty_members.filter(department__code=dept)
    return render(request, 'faculty/list.html', {
        'faculty_members': faculty_members,
        'departments': departments,
        'selected_dept': dept or '',
        'total_faculty_count': 176,
    })

def faculty_detail(request, pk):
    faculty = get_object_or_404(Faculty.objects.select_related('user', 'department'), pk=pk)
    from apps.academics.models import CourseOffering
    courses = CourseOffering.objects.filter(faculty=faculty)
    return render(request, 'faculty/detail.html', {'faculty': faculty, 'courses': courses})
