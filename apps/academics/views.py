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

    assessments = AcademicRiskAssessment.objects.select_related(
        'student', 'student__department', 'student__user'
    ).order_by('-assessed_at')

    if dept_code:
        assessments = assessments.filter(student__department__code=dept_code)
    if risk_filter:
        assessments = assessments.filter(risk_level=risk_filter)

    total_assessed = assessments.count()
    high_risk_count = assessments.filter(risk_level='HIGH').count()
    med_risk_count = assessments.filter(risk_level='MEDIUM').count()
    low_risk_count = assessments.filter(risk_level='LOW').count()
    active_interventions_count = AcademicIntervention.objects.filter(
        status__in=[AcademicIntervention.Status.PENDING, AcademicIntervention.Status.IN_PROGRESS]
    ).count()

    paginator = Paginator(assessments, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    departments = Department.objects.filter(is_active=True)

    context = {
        'page_obj': page_obj,
        'assessments': page_obj,  # ensure both references work in template
        'departments': departments,
        'selected_dept': dept_code,
        'selected_risk': risk_filter,
        'total_assessed': total_assessed,
        'high_risk_count': high_risk_count,
        'med_risk_count': med_risk_count,
        'low_risk_count': low_risk_count,
        'active_interventions_count': active_interventions_count,
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
    
    results = AcademicRiskPredictor.batch_assess_all_students()
    return JsonResponse({
        'status': 'success',
        'message': f"Assessed academic risk for {results.get('processed', 0)} students using Random Forest + Sequential DL model.",
        'details': results
    })

@login_required
@role_required('SUPER_ADMIN', 'COLLEGE_ADMIN', 'DEPARTMENT_ADMIN', 'FACULTY')
def api_auto_dispatch_interventions(request):
    """
    Automatically dispatches academic interventions and in-app alert notifications
    for all students flagged as HIGH risk who do not currently have an active intervention.
    """
    from apps.notifications.models import Notification
    
    # Identify HIGH risk students from their most recent assessment
    high_risk_assessments = AcademicRiskAssessment.objects.filter(
        risk_level='HIGH'
    ).select_related('student', 'student__user', 'student__department').order_by('-assessed_at')
    
    seen_students = set()
    dispatched_count = 0
    created_interventions = []

    for a in high_risk_assessments:
        student = a.student
        if student.id in seen_students:
            continue
        seen_students.add(student.id)

        # Check if student already has a pending/active intervention
        existing_active = AcademicIntervention.objects.filter(
            student=student,
            status__in=[AcademicIntervention.Status.PENDING, AcademicIntervention.Status.IN_PROGRESS]
        ).exists()

        if not existing_active:
            # Select appropriate intervention type based on factors
            factors = a.get_factors()
            factors_str = " ".join(factors).lower()
            if 'attendance' in factors_str and 'below' in factors_str:
                itype = AcademicIntervention.InterventionType.REMEDIAL_CLASS
                desc = "Automated AI Alert: Mandatory remedial attendance clinic assigned."
            elif 'gpa' in factors_str or 'internal' in factors_str:
                itype = AcademicIntervention.InterventionType.FACULTY_MENTORING
                desc = "Automated AI Alert: 1-on-1 faculty academic counseling scheduled."
            else:
                itype = AcademicIntervention.InterventionType.ASSIGNMENT_SUPPORT
                desc = "Automated AI Alert: Coursework support and lab assignment extension granted."

            intervention = AcademicIntervention.objects.create(
                assessment=a,
                student=student,
                intervention_type=itype,
                notes=f"{desc} (Risk Score: {a.risk_score:.1f}%). Factors: {'; '.join(factors[:2])}",
                status=AcademicIntervention.Status.IN_PROGRESS
            )
            dispatched_count += 1
            created_interventions.append({
                'student_id': student.student_id,
                'name': student.user.get_full_name() if student.user else f"{student.first_name} {student.last_name}",
                'type': intervention.get_intervention_type_display(),
                'risk_score': a.risk_score
            })

            # In-app student alert
            if student.user:
                Notification.objects.create(
                    user=student.user,
                    title="🚨 Academic AI Early-Warning Alert",
                    message=f"An automated intervention ({intervention.get_intervention_type_display()}) has been activated to help safeguard your semester coursework.",
                    category=Notification.Category.ACADEMIC_ALERT
                )

    return JsonResponse({
        'status': 'success',
        'dispatched_count': dispatched_count,
        'message': f"Successfully dispatched {dispatched_count} high-risk academic interventions and sent in-app notifications.",
        'interventions': created_interventions[:10]  # preview of top 10
    })

@login_required
def api_student_academic_analytics(request, student_id):
    """
    Returns full student performance metrics, 5-week sequential trajectory,
    explainable AI factor weights, and intervention history for interactive modal.
    """
    student = get_object_or_404(Student.objects.select_related('department', 'user'), student_id=student_id)
    latest_assessment = AcademicRiskAssessment.objects.filter(student=student).order_by('-assessed_at').first()
    weekly_records = WeeklyPerformanceRecord.objects.filter(student=student).order_by('week_number')
    interventions = AcademicIntervention.objects.filter(student=student).order_by('-created_at')

    assessment_data = None
    if latest_assessment:
        assessment_data = {
            'risk_level': latest_assessment.risk_level,
            'risk_score': latest_assessment.risk_score,
            'confidence': round(latest_assessment.confidence * 100, 1),
            'factors': latest_assessment.get_factors(),
            'recommended_action': latest_assessment.recommended_action,
            'assessed_at': latest_assessment.assessed_at.strftime('%b %d, %Y %H:%M')
        }

    return JsonResponse({
        'status': 'success',
        'student': {
            'student_id': student.student_id,
            'name': student.user.get_full_name() if student.user else f"{student.first_name} {student.last_name}",
            'department': student.department.name,
            'department_code': student.department.code,
            'semester': student.semester,
            'cgpa': student.cgpa,
            'attendance_percentage': student.attendance_percentage,
            'backlog_count': student.backlog_count,
        },
        'assessment': assessment_data,
        'weekly_records': [
            {
                'week': w.week_number,
                'attendance': round(w.attendance_rate, 1),
                'quiz': round(w.quiz_score, 1),
                'assignment': round(w.assignment_score, 1),
                'lms_hours': round(w.lms_activity_hours, 1)
            } for w in weekly_records
        ],
        'interventions': [
            {
                'type': i.get_intervention_type_display(),
                'status': i.status,
                'notes': i.notes,
                'date': i.created_at.strftime('%b %d, %Y')
            } for i in interventions
        ]
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
