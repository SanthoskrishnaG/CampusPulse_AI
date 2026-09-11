import csv
import io
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from .models import Student
from apps.departments.models import Department
from apps.accounts.decorators import role_required

@login_required
def student_dashboard(request):
    """
    Student Intelligence Hub: Shows personal academic risk status,
    attendance telemetry, recommended clubs, events, and project teammates.
    """
    student = getattr(request.user, 'student_profile', None)
    if not student:
        # Fallback to demo student if viewing as admin/faculty
        student = Student.objects.first()

    risk_assessment = None
    enrollments = []
    recommended_clubs = []
    recommended_events = []
    recommended_teammates = []

    if student:
        from apps.academics.models import AcademicRiskAssessment, Enrollment
        risk_assessment = AcademicRiskAssessment.objects.filter(student=student).order_by('-assessed_at').first()
        enrollments = Enrollment.objects.filter(student=student).select_related('course_offering', 'course_offering__course')

        # Recommendations
        from apps.recommendations.engine import RecommendationEngine
        recommended_clubs = RecommendationEngine.recommend_clubs_for_student(student, limit=3)
        recommended_events = RecommendationEngine.recommend_events_for_student(student, limit=3)
        recommended_teammates = RecommendationEngine.recommend_teammates_for_student(student, limit=4)

    context = {
        'student': student,
        'risk_assessment': risk_assessment,
        'enrollments': enrollments,
        'recommended_clubs': recommended_clubs,
        'recommended_events': recommended_events,
        'recommended_teammates': recommended_teammates,
    }
    return render(request, 'students/dashboard.html', context)

@login_required
def student_list(request):
    """
    Searchable and filterable student directory for Faculty and Administrators.
    """
    students = Student.objects.select_related('department', 'user').all()
    q = request.GET.get('q')
    dept = request.GET.get('dept')
    sem = request.GET.get('sem')

    if q:
        students = students.filter(student_id__icontains=q) | students.filter(first_name__icontains=q) | students.filter(skills__icontains=q)
    if dept:
        students = students.filter(department__code=dept)
    if sem:
        students = students.filter(semester=sem)

    paginator = Paginator(students, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    departments = Department.objects.all()

    return render(request, 'students/list.html', {
        'page_obj': page_obj,
        'departments': departments,
        'q': q,
        'selected_dept': dept,
        'selected_sem': sem
    })

@login_required
def student_detail(request, student_id):
    student = get_object_or_404(Student.objects.select_related('department', 'user'), student_id=student_id)
    from apps.academics.models import AcademicRiskAssessment, Enrollment, WeeklyPerformanceRecord, AcademicIntervention
    
    risk_assessment = AcademicRiskAssessment.objects.filter(student=student).order_by('-assessed_at').first()
    enrollments = Enrollment.objects.filter(student=student).select_related('course_offering__course')
    weekly_records = WeeklyPerformanceRecord.objects.filter(student=student).order_by('week_number')
    interventions = AcademicIntervention.objects.filter(student=student).order_by('-created_at')

    context = {
        'student': student,
        'risk_assessment': risk_assessment,
        'enrollments': enrollments,
        'weekly_records': weekly_records,
        'interventions': interventions,
    }
    return render(request, 'students/detail.html', context)

@login_required
@role_required('SUPER_ADMIN', 'COLLEGE_ADMIN', 'DEPARTMENT_ADMIN')
def import_csv_view(request):
    """
    Secure CSV Importer for anonymized institutional student records.
    Includes format validation, preview, and safe bulk insertion.
    """
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        if not csv_file.name.endswith('.csv'):
            messages.error(request, "Invalid file type. Please upload a standard CSV file.")
            return redirect('students:import_csv')

        try:
            decoded_file = csv_file.read().decode('utf-8')
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string)
            
            # Required headers validation
            required_fields = {'student_id', 'department_code', 'cgpa', 'attendance'}
            if not required_fields.issubset(set(reader.fieldnames or [])):
                missing = required_fields - set(reader.fieldnames or [])
                messages.error(request, f"Missing required CSV columns: {', '.join(missing)}")
                return redirect('students:import_csv')

            imported_count = 0
            errors = []

            with transaction.atomic():
                for row_idx, row in enumerate(reader, start=2):
                    try:
                        sid = row['student_id'].strip()
                        dept_code = row['department_code'].strip().upper()
                        dept = Department.objects.filter(code=dept_code).first()
                        if not dept:
                            errors.append(f"Row {row_idx}: Department '{dept_code}' does not exist.")
                            continue

                        cgpa = float(row.get('cgpa', 7.0))
                        attendance = float(row.get('attendance', 80.0))
                        semester = int(row.get('semester', 5))
                        skills = row.get('skills', '')
                        interests = row.get('interests', '')

                        Student.objects.update_or_create(
                            student_id=sid,
                            defaults={
                                'department': dept,
                                'cgpa': cgpa,
                                'attendance_percentage': attendance,
                                'semester': semester,
                                'skills': skills,
                                'interests': interests,
                                'first_name': row.get('first_name', f"Student-{sid}"),
                                'last_name': row.get('last_name', ''),
                            }
                        )
                        imported_count += 1
                    except Exception as row_err:
                        errors.append(f"Row {row_idx}: {str(row_err)}")

            if imported_count > 0:
                messages.success(request, f"Successfully imported/updated {imported_count} student records.")
            if errors:
                messages.warning(request, f"Encountered {len(errors)} issues during import: {errors[:3]}")

            return redirect('students:list')
        except Exception as e:
            messages.error(request, f"Failed to process CSV file: {str(e)}")

    return render(request, 'students/import_csv.html')
