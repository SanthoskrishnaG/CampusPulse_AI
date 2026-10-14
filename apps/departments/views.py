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
    complaints_count = Complaint.objects.filter(target_department__icontains=current_dept.name).count() if current_dept else 0

    from apps.common.models import CampusLocation
    from apps.events.models import Event
    
    lab_count = CampusLocation.objects.filter(category='LABORATORY', department_id=current_dept.id).count() if current_dept else 0
    classroom_count = CampusLocation.objects.filter(category='ACADEMIC_BLOCK', department_id=current_dept.id).count() if current_dept else 0
    event_count = Event.objects.filter(organizing_department=current_dept).count() if current_dept else 0

    faculty_count = Faculty.objects.filter(department=current_dept).count() if current_dept else 0
    complaints_count = Complaint.objects.filter(target_department__icontains=current_dept.name).count() if current_dept else 0

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
        'lab_count': lab_count,
        'classroom_count': classroom_count,
        'event_count': event_count,
    }
    return render(request, 'departments/dashboard.html', context)

def department_list(request):
    from apps.academics.models import AcademicRiskAssessment
    from apps.common.models import CampusLocation

    departments = list(Department.objects.filter(is_active=True))
    dept_meta = {
        'CSE': {'accent': '#4F46E5', 'block': 'Block A • Level 2', 'category': 'Computing', 'labs': 8},
        'AIDS': {'accent': '#06B6D4', 'block': 'Block E • Tech Park', 'category': 'Computing', 'labs': 6},
        'IT': {'accent': '#6366F1', 'block': 'Block A • Level 3', 'category': 'Computing', 'labs': 6},
        'ECE': {'accent': '#7C3AED', 'block': 'Block B • Circuits Wing', 'category': 'Circuits', 'labs': 7},
        'EEE': {'accent': '#F59E0B', 'block': 'Block B • Power Lab Wing', 'category': 'Circuits', 'labs': 5},
        'MECH': {'accent': '#EF4444', 'block': 'Block C • Central Workshop', 'category': 'Core', 'labs': 9},
        'CIVIL': {'accent': '#10B981', 'block': 'Block C • Structures Lab', 'category': 'Core', 'labs': 6},
        'AERO': {'accent': '#3B82F6', 'block': 'Block D • Propulsion Lab', 'category': 'Core', 'labs': 5},
        'BIOTECH': {'accent': '#14B8A6', 'block': 'Block F • Genomics Complex', 'category': 'Bio', 'labs': 6},
    }

    for dept in departments:
        meta = dept_meta.get(dept.code, {'accent': '#4F46E5', 'block': 'Block A', 'category': 'Engineering', 'labs': 4})
        dept.accent_color = meta['accent']
        dept.block_label = meta['block']
        dept.category_label = meta['category']
        dept.stu_count = dept.students.count()
        dept.fac_count = dept.faculty_members.count()
        dept.lab_count = meta['labs']
        high_risk = AcademicRiskAssessment.objects.filter(student__department=dept, risk_level='HIGH').count()
        dept.risk_rate = round((high_risk / max(1, dept.stu_count)) * 100, 1)

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
