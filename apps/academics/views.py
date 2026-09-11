from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import Course, AcademicRiskAssessment, AcademicIntervention, WeeklyPerformanceRecord
from apps.students.models import Student
from apps.departments.models import Department
from apps.accounts.decorators import role_required

@login_required
def risk_dashboard(request):
    """
    Early Warning & Academic Risk Center.
    Visualizes risk distribution, explainability factors, and intervention queues.
    """
    dept_code = request.GET.get('dept')
    risk_filter = request.GET.get('risk')

    assessments = AcademicRiskAssessment.objects.select_related('student', 'student__department', 'student__user').all()

    if dept_code:
        assessments = assessments.filter(student__department__code=dept_code)
    if risk_filter:
        assessments = assessments.filter(risk_level=risk_filter)

    total_assessed = assessments.count()
    high_risk_count = assessments.filter(risk_level='HIGH').count()
    med_risk_count = assessments.filter(risk_level='MEDIUM').count()
    low_risk_count = assessments.filter(risk_level='LOW').count()

    paginator = Paginator(assessments, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    departments = Department.objects.filter(is_active=True)

    context = {
        'page_obj': page_obj,
        'departments': departments,
        'selected_dept': dept_code,
        'selected_risk': risk_filter,
        'total_assessed': total_assessed,
        'high_risk_count': high_risk_count,
        'med_risk_count': med_risk_count,
        'low_risk_count': low_risk_count,
    }
    return render(request, 'academics/risk_dashboard.html', context)

@login_required
@role_required('SUPER_ADMIN', 'COLLEGE_ADMIN', 'DEPARTMENT_ADMIN', 'FACULTY')
def run_risk_assessment_api(request):
    """
    Executes the trained ML model pipeline on active students, computing
    calibrated probabilities and explainable factors.
    """
    from ml.academic.predict import AcademicRiskPredictor
    
    count = AcademicRiskPredictor.batch_assess_all_students()
    return JsonResponse({
        'status': 'success',
        'message': f"Assessed academic risk for {count} students using trained Random Forest + Sequential model.",
        'students_updated': count
    })

@login_required
@role_required('SUPER_ADMIN', 'COLLEGE_ADMIN', 'DEPARTMENT_ADMIN', 'FACULTY')
def create_intervention(request, student_id):
    student = get_object_or_404(Student, student_id=student_id)
    if request.method == 'POST':
        intervention_type = request.POST.get('intervention_type', 'FACULTY_MENTORING')
        notes = request.POST.get('notes', 'Scheduled faculty mentorship regarding course progress.')

        faculty = getattr(request.user, 'faculty_profile', None)
        latest_assessment = student.risk_assessments.first()

        intervention = AcademicIntervention.objects.create(
            assessment=latest_assessment,
            student=student,
            faculty=faculty,
            intervention_type=intervention_type,
            notes=notes,
            status=AcademicIntervention.Status.IN_PROGRESS
        )

        # In-app notification for the student
        from apps.notifications.models import Notification
        if student.user:
            Notification.objects.create(
                user=student.user,
                title="Academic Mentorship Scheduled",
                message=f"A {intervention.get_intervention_type_display()} has been assigned to support your coursework.",
                category=Notification.Category.ACADEMIC_ALERT
            )

        messages.success(request, f"Intervention registered for {student.student_id}.")
        return redirect('students:detail', student_id=student.student_id)

    return redirect('students:detail', student_id=student.student_id)

def course_list(request):
    courses = Course.objects.select_related('department').all()
    return render(request, 'academics/courses.html', {'courses': courses})
