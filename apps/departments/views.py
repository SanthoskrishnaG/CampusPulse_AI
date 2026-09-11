from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Department, DepartmentAnnouncement, DepartmentResource
from apps.accounts.decorators import role_required

@login_required
def department_dashboard(request):
    """
    Department Command Center showing student risk distribution,
    faculty count, department events, and complaints.
    """
    departments = Department.objects.filter(is_active=True)
    selected_code = request.GET.get('dept', 'CSE')
    current_dept = departments.filter(code=selected_code).first() or departments.first()

    # Metrics for selected department
    from apps.students.models import Student
    from apps.faculty.models import Faculty
    from apps.complaints.models import Complaint
    from apps.academics.models import AcademicRiskAssessment

    student_count = Student.objects.filter(department=current_dept).count() if current_dept else 0
    faculty_count = Faculty.objects.filter(department=current_dept).count() if current_dept else 0
    complaints_count = Complaint.objects.filter(department=current_dept.name).count() if current_dept else 0

    high_risk_count = 0
    medium_risk_count = 0
    low_risk_count = 0
    if current_dept:
        high_risk_count = AcademicRiskAssessment.objects.filter(student__department=current_dept, risk_level='HIGH').count()
        medium_risk_count = AcademicRiskAssessment.objects.filter(student__department=current_dept, risk_level='MEDIUM').count()
        low_risk_count = AcademicRiskAssessment.objects.filter(student__department=current_dept, risk_level='LOW').count()

    announcements = DepartmentAnnouncement.objects.filter(department=current_dept)[:5] if current_dept else []
    resources = DepartmentResource.objects.filter(department=current_dept)[:5] if current_dept else []

    context = {
        'departments': departments,
        'current_dept': current_dept,
        'student_count': student_count,
        'faculty_count': faculty_count,
        'complaints_count': complaints_count,
        'high_risk_count': high_risk_count,
        'medium_risk_count': medium_risk_count,
        'low_risk_count': low_risk_count,
        'announcements': announcements,
        'resources': resources,
    }
    return render(request, 'departments/dashboard.html', context)

def department_list(request):
    departments = Department.objects.filter(is_active=True)
    return render(request, 'departments/list.html', {'departments': departments})

def department_detail(request, code):
    dept = get_object_or_404(Department, code=code)
    announcements = dept.announcements.all()
    resources = dept.resources.all()
    return render(request, 'departments/detail.html', {
        'department': dept,
        'announcements': announcements,
        'resources': resources
    })
