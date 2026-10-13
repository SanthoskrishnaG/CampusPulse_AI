from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.utils import timezone
from django.db.models import Q
from apps.accounts.models import User
from apps.students.models import Student
from .models import (
    Hostel, HostelBlock, HostelRoom, HostelFacility,
    HostelAnnouncement, HostelComplaint, HostelMaintenanceRequest,
    HostelMessMenu, HostelEvent, HostelMessFeedback, HostelAttendance,
    HostelOutPass, HostelMessAttendance
)
from .decorators import hostel_access_required


def _get_student_hostel(request):
    """Helper to get student's assigned hostel or active hostel based on category."""
    user = request.user
    if user.is_superuser or user.role in [User.Role.SUPER_ADMIN, User.Role.COLLEGE_ADMIN]:
        hostel_code = request.GET.get('hostel', 'BH-1')
        return Hostel.objects.filter(code=hostel_code).first() or Hostel.objects.first()

    student_profile = getattr(user, 'student_profile', None)
    if student_profile and student_profile.assigned_hostel:
        return student_profile.assigned_hostel
    elif student_profile and student_profile.hostel_category:
        return Hostel.objects.filter(category=student_profile.hostel_category, is_active=True).first()
    return None


@login_required
@hostel_access_required
def dashboard(request):
    """
    Resident Hostel Dashboard.
    Provides personal room details, occupancy metrics, announcements,
    mess menu for today, active maintenance tickets, and emergency contacts.
    """
    hostel = _get_student_hostel(request)
    if not hostel:
        hostel = Hostel.objects.first()

    student = getattr(request.user, 'student_profile', None)

    # Announcements (hostel specific or all-hostel broadcasts)
    announcements = HostelAnnouncement.objects.filter(
        Q(hostel=hostel) | Q(hostel__isnull=True)
    )[:5] if hostel else []

    # Student's complaints & maintenance
    my_complaints = HostelComplaint.objects.filter(student=student)[:5] if student else []
    my_maintenance = HostelMaintenanceRequest.objects.filter(student=student)[:5] if student else []

    # Facilities
    facilities = hostel.facilities.all()[:8] if hostel else []

    # Today's Mess Menu
    today_day = timezone.now().strftime('%A')
    today_mess = HostelMessMenu.objects.filter(day_of_week=today_day).first()

    # Roommates / Room info
    room_info = None
    roommates = []
    if student and student.room_number and hostel:
        room_info = HostelRoom.objects.filter(hostel=hostel, room_number=student.room_number).first()
        roommates = Student.objects.filter(
            assigned_hostel=hostel,
            room_number=student.room_number
        ).exclude(id=student.id)

    # Nearby CIT Hostels for switching tabs if admin
    all_hostels = Hostel.objects.filter(is_active=True)

    context = {
        'hostel': hostel,
        'student': student,
        'announcements': announcements,
        'my_complaints': my_complaints,
        'my_maintenance': my_maintenance,
        'facilities': facilities,
        'today_mess': today_mess,
        'room_info': room_info,
        'roommates': roommates,
        'all_hostels': all_hostels,
    }
    return render(request, 'hostel/dashboard.html', context)


@login_required
@hostel_access_required
def facilities_view(request):
    """View all amenities and infrastructure for resident's hostel."""
    hostel = _get_student_hostel(request)
    facilities_by_category = {}
    if hostel:
        for f in hostel.facilities.all():
            facilities_by_category.setdefault(f.get_category_display(), []).append(f)

    return render(request, 'hostel/facilities.html', {
        'hostel': hostel,
        'facilities_by_category': facilities_by_category,
    })


@login_required
@hostel_access_required
def rooms_view(request):
    """View hostel blocks, floor directories, and room layouts."""
    hostel = _get_student_hostel(request)
    student = getattr(request.user, 'student_profile', None)
    blocks = hostel.blocks.prefetch_related('rooms').all() if hostel else []
    
    # Standalone rooms if no blocks assigned
    standalone_rooms = hostel.rooms.filter(block__isnull=True) if hostel else []

    return render(request, 'hostel/rooms.html', {
        'hostel': hostel,
        'student': student,
        'blocks': blocks,
        'standalone_rooms': standalone_rooms,
    })


@login_required
@hostel_access_required
def complaints_view(request):
    """Resident complaint tracker and intake."""
    hostel = _get_student_hostel(request)
    student = getattr(request.user, 'student_profile', None)

    if request.method == 'POST':
        if not student or not hostel:
            messages.error(request, "Unable to file complaint: Student hostel assignment missing.")
            return redirect('hostel:complaints')

        title = request.POST.get('title', '').strip()
        category = request.POST.get('category', 'ELECTRICITY')
        priority = request.POST.get('priority', 'MEDIUM')
        description = request.POST.get('description', '').strip()
        room_number = request.POST.get('room_number', student.room_number or 'Unspecified')

        if title and description:
            complaint = HostelComplaint.objects.create(
                student=student,
                hostel=hostel,
                room_number=room_number,
                category=category,
                priority=priority,
                title=title,
                description=description
            )
            messages.success(request, f"Hostel Grievance #{complaint.id} submitted successfully.")
            return redirect('hostel:complaints')
        else:
            messages.error(request, "Please provide both a title and description.")

    complaints = HostelComplaint.objects.filter(student=student) if student else []
    return render(request, 'hostel/complaints.html', {
        'hostel': hostel,
        'student': student,
        'complaints': complaints,
        'categories': HostelComplaint.Category.choices,
        'priorities': HostelComplaint.Priority.choices,
    })


@login_required
@hostel_access_required
def maintenance_view(request):
    """Rapid maintenance requests (fan, light, plumbing, furniture)."""
    hostel = _get_student_hostel(request)
    student = getattr(request.user, 'student_profile', None)

    if request.method == 'POST':
        if not student or not hostel:
            messages.error(request, "Unable to log request: Assignment required.")
            return redirect('hostel:maintenance')

        item = request.POST.get('item', '').strip()
        description = request.POST.get('description', '').strip()
        priority = request.POST.get('priority', 'MEDIUM')
        room_number = request.POST.get('room_number', student.room_number or 'Unspecified')

        if item and description:
            req = HostelMaintenanceRequest.objects.create(
                student=student,
                hostel=hostel,
                room_number=room_number,
                item=item,
                description=description,
                priority=priority
            )
            messages.success(request, f"Maintenance Ticket #{req.id} created. Duty electrician/plumber dispatched.")
            return redirect('hostel:maintenance')

    requests_list = HostelMaintenanceRequest.objects.filter(student=student) if student else []
    return render(request, 'hostel/maintenance.html', {
        'hostel': hostel,
        'student': student,
        'requests_list': requests_list,
        'priorities': HostelMaintenanceRequest.Priority.choices,
    })


@login_required
@hostel_access_required
def mess_view(request):
    """Hostel Dining & Mess schedule with weekly meal timings and resident feedback."""
    hostel = _get_student_hostel(request)
    student = getattr(request.user, 'student_profile', None)

    if request.method == 'POST':
        meal_type = request.POST.get('meal_type', 'LUNCH')
        try:
            rating = int(request.POST.get('rating', 4))
        except ValueError:
            rating = 4
        comments = request.POST.get('comments', '').strip()

        if student and hostel:
            HostelMessFeedback.objects.create(
                student=student,
                hostel=hostel,
                meal_type=meal_type,
                rating=rating,
                comments=comments
            )
            messages.success(request, "Your mess dining feedback has been recorded for the hostel committee.")
            return redirect('hostel:mess')

    menus = HostelMessMenu.objects.all().order_by('id')
    today_day = timezone.now().strftime('%A')
    feedbacks = HostelMessFeedback.objects.filter(hostel=hostel)[:8] if hostel else []

    return render(request, 'hostel/mess.html', {
        'hostel': hostel,
        'menus': menus,
        'today_day': today_day,
        'feedbacks': feedbacks,
        'meal_types': HostelMessFeedback.MealType.choices,
    })


@login_required
@hostel_access_required
def announcements_view(request):
    """Hostel resident announcement broadcasts."""
    hostel = _get_student_hostel(request)
    announcements = HostelAnnouncement.objects.filter(
        Q(hostel=hostel) | Q(hostel__isnull=True)
    ) if hostel else HostelAnnouncement.objects.all()

    return render(request, 'hostel/announcements.html', {
        'hostel': hostel,
        'announcements': announcements,
    })


@login_required
@hostel_access_required
def attendance_view(request):
    """Evening hostel check-in and attendance log."""
    hostel = _get_student_hostel(request)
    student = getattr(request.user, 'student_profile', None)
    records = HostelAttendance.objects.filter(student=student) if student else []

    return render(request, 'hostel/attendance.html', {
        'hostel': hostel,
        'student': student,
        'records': records,
        'statuses': HostelAttendance.Status.choices,
    })


@login_required
@hostel_access_required
def route_view(request):
    """Dedicated pedestrian route guide to assigned hostel building."""
    hostel = _get_student_hostel(request)
    return render(request, 'hostel/route.html', {
        'hostel': hostel,
    })


@login_required
@hostel_access_required
def events_view(request):
    """Hostel resident events, sports tournaments, and community meetings."""
    hostel = _get_student_hostel(request)
    events = HostelEvent.objects.filter(hostel=hostel) if hostel else HostelEvent.objects.all()

    return render(request, 'hostel/events.html', {
        'hostel': hostel,
        'events': events,
    })


@login_required
@hostel_access_required
def emergency_view(request):
    """24/7 Hostel & Campus Emergency Contact Directory."""
    hostel = _get_student_hostel(request)

    return render(request, 'hostel/emergency.html', {
        'hostel': hostel,
    })


@login_required
def admin_analytics_view(request):
    """
    Hostel Operational Command Center for College Administrators and Wardens.
    """
    user = request.user
    if not (user.is_superuser or user.role in [User.Role.SUPER_ADMIN, User.Role.COLLEGE_ADMIN]):
        return HttpResponseForbidden("Administrative clearance required to view master hostel analytics.")

    hostels = Hostel.objects.all()
    total_capacity = sum(h.capacity for h in hostels)
    total_occupied = sum(h.occupied_count() for h in hostels)
    total_available = max(0, total_capacity - total_occupied)
    overall_occupancy = round((total_occupied / total_capacity) * 100, 1) if total_capacity > 0 else 0

    open_complaints = HostelComplaint.objects.exclude(status=HostelComplaint.Status.CLOSED).count()
    pending_maintenance = HostelMaintenanceRequest.objects.exclude(status=HostelMaintenanceRequest.Status.COMPLETED).count()

    boys_hostels = hostels.filter(category=Hostel.Category.BOYS)
    girls_hostels = hostels.filter(category=Hostel.Category.GIRLS)

    context = {
        'hostels': hostels,
        'total_capacity': total_capacity,
        'total_occupied': total_occupied,
        'total_available': total_available,
        'overall_occupancy': overall_occupancy,
        'open_complaints': open_complaints,
        'pending_maintenance': pending_maintenance,
        'boys_hostels': boys_hostels,
        'girls_hostels': girls_hostels,
    }
    return render(request, 'hostel/admin_analytics.html', context)


# -------------------------------------------------------------
# REST API Endpoints (Strictly Guarded with 403 Forbidden)
# -------------------------------------------------------------

@login_required
@hostel_access_required
def api_hostel_root(request):
    """Protected API returning accessible hostel summary."""
    hostel = _get_student_hostel(request)
    if not hostel:
        hostel = Hostel.objects.first()

    return JsonResponse({
        'status': 'success',
        'hostel': {
            'id': hostel.id,
            'name': hostel.name,
            'code': hostel.code,
            'category': hostel.category,
            'capacity': hostel.capacity,
            'occupied': hostel.occupied_count(),
            'available': hostel.available_count(),
            'occupancy_percentage': hostel.occupancy_percentage(),
        }
    })


@login_required
@hostel_access_required
def api_hostel_facilities(request):
    """Protected API returning facilities for resident hostel."""
    hostel = _get_student_hostel(request)
    if not hostel:
        return JsonResponse({'facilities': []})

    facilities = [
        {'name': f.name, 'category': f.get_category_display(), 'status': f.status, 'icon': f.icon}
        for f in hostel.facilities.all()
    ]
    return JsonResponse({
        'hostel': hostel.name,
        'code': hostel.code,
        'facilities': facilities
    })


@login_required
@hostel_access_required
def api_hostel_rooms(request):
    """Protected API returning rooms for resident hostel."""
    hostel = _get_student_hostel(request)
    if not hostel:
        return JsonResponse({'rooms': []})

    rooms = [
        {
            'room_number': r.room_number,
            'block': r.block.name if r.block else 'Main',
            'floor': r.floor,
            'type': r.get_room_type_display(),
            'capacity': r.capacity,
            'occupied': r.occupied,
            'is_available': r.is_available
        }
        for r in hostel.rooms.all()
    ]
    return JsonResponse({
        'hostel': hostel.name,
        'code': hostel.code,
        'rooms': rooms
    })


@login_required
@hostel_access_required
def api_hostel_routes(request):
    """Protected API returning navigation waypoints for resident hostel."""
    hostel = _get_student_hostel(request)
    if not hostel:
        return JsonResponse({'error': 'No assigned hostel'}, status=404)

    route_waypoints = [
        {"name": "CIT Main Gate", "lat": 11.0291, "lng": 77.0268},
        {"name": "Admin Roundabout", "lat": 11.0283, "lng": 77.0271},
        {"name": "Central Quad", "lat": 11.0276, "lng": 77.0271},
        {"name": "South Living Spine", "lat": 11.0266, "lng": 77.0271},
        {"name": "Hostel Residential Junction", "lat": 11.0254, "lng": 77.0275},
        {"name": hostel.name, "lat": hostel.latitude, "lng": hostel.longitude},
    ]
    return JsonResponse({
        'hostel': hostel.name,
        'code': hostel.code,
        'waypoints': route_waypoints
    })


@login_required
@hostel_access_required
def api_hostel_complaints(request):
    """Protected API handling complaints retrieval and submission."""
    student = getattr(request.user, 'student_profile', None)
    hostel = _get_student_hostel(request)

    if request.method == 'POST':
        import json
        try:
            data = json.loads(request.body) if request.body else request.POST
        except Exception:
            data = request.POST

        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        category = data.get('category', 'OTHER')
        priority = data.get('priority', 'MEDIUM')
        room = data.get('room_number', getattr(student, 'room_number', 'Assigned'))

        if not title or not description:
            return JsonResponse({'error': 'Title and description are required'}, status=400)

        complaint = HostelComplaint.objects.create(
            student=student,
            hostel=hostel,
            room_number=room,
            category=category,
            priority=priority,
            title=title,
            description=description
        )
        return JsonResponse({
            'status': 'created',
            'complaint_id': complaint.id,
            'title': complaint.title,
            'category': complaint.get_category_display(),
            'status_display': complaint.get_status_display()
        }, status=201)

    complaints = [
        {
            'id': c.id,
            'title': c.title,
            'category': c.get_category_display(),
            'priority': c.get_priority_display(),
            'status': c.get_status_display(),
            'created_at': c.created_at.strftime('%Y-%m-%d %H:%M')
        }
        for c in HostelComplaint.objects.filter(student=student)
    ] if student else []
    return JsonResponse({'complaints': complaints})


@login_required
@hostel_access_required
def api_hostel_maintenance(request):
    """Protected API handling maintenance request ticket creation and listing."""
    student = getattr(request.user, 'student_profile', None)
    hostel = _get_student_hostel(request)

    if request.method == 'POST':
        import json
        try:
            data = json.loads(request.body) if request.body else request.POST
        except Exception:
            data = request.POST

        item = data.get('item', '').strip()
        description = data.get('description', '').strip()
        priority = data.get('priority', 'MEDIUM')
        room = data.get('room_number', getattr(student, 'room_number', 'Assigned'))

        if not item or not description:
            return JsonResponse({'error': 'Item and description are required'}, status=400)

        req = HostelMaintenanceRequest.objects.create(
            student=student,
            hostel=hostel,
            room_number=room,
            item=item,
            description=description,
            priority=priority
        )
        return JsonResponse({
            'status': 'created',
            'ticket_id': req.id,
            'item': req.item,
            'priority': req.get_priority_display(),
            'status_display': req.get_status_display()
        }, status=201)

    tickets = [
        {
            'id': t.id,
            'item': t.item,
            'room_number': t.room_number,
            'priority': t.get_priority_display(),
            'status': t.get_status_display(),
            'created_at': t.created_at.strftime('%Y-%m-%d %H:%M')
        }
        for t in HostelMaintenanceRequest.objects.filter(student=student)
    ] if student else []
    return JsonResponse({'maintenance_requests': tickets})


@login_required
@hostel_access_required
def api_hostel_details(request, hostel_code):
    """Protected API returning structured hostel data for specific hostel code."""
    hostel = get_object_or_404(Hostel, code__iexact=hostel_code)

    data = {
        'id': hostel.id,
        'name': hostel.name,
        'code': hostel.code,
        'category': hostel.category,
        'category_display': hostel.get_category_display(),
        'latitude': hostel.latitude,
        'longitude': hostel.longitude,
        'capacity': hostel.capacity,
        'occupied': hostel.occupied_count(),
        'available': hostel.available_count(),
        'occupancy_percentage': hostel.occupancy_percentage(),
        'floor_count': hostel.floor_count,
        'warden_name': hostel.warden_name,
        'emergency_contacts': {
            'warden': hostel.warden_contact,
            'security': hostel.security_contact,
            'medical': hostel.medical_contact,
        },
        'facilities': [
            {'name': f.name, 'category': f.get_category_display(), 'status': f.status, 'icon': f.icon}
            for f in hostel.facilities.all()
        ]
    }
    return JsonResponse(data)


@login_required
@hostel_access_required
def api_hostel_route(request, hostel_code):
    """Protected API returning route waypoint coordinates to the hostel."""
    hostel = get_object_or_404(Hostel, code__iexact=hostel_code)

    route_waypoints = [
        {"name": "CIT Main Gate", "lat": 11.0291, "lng": 77.0268},
        {"name": "Admin Roundabout", "lat": 11.0283, "lng": 77.0271},
        {"name": "Central Quad", "lat": 11.0276, "lng": 77.0271},
        {"name": "South Living Spine", "lat": 11.0266, "lng": 77.0271},
        {"name": "Hostel Residential Junction", "lat": 11.0254, "lng": 77.0275},
        {"name": hostel.name, "lat": hostel.latitude, "lng": hostel.longitude},
    ]
    return JsonResponse({
        'hostel': hostel.name,
        'code': hostel.code,
        'waypoints': route_waypoints
    })


@login_required
@hostel_access_required
def outpass_view(request):
    """
    Hostel Resident Out-Pass Portal.
    Allows students to request day outings, weekend leaves, and emergency passes with QR verification.
    Allows wardens and administrators to review, approve/reject, or mark out-passes returned.
    """
    hostel = _get_student_hostel(request)
    student = getattr(request.user, 'student_profile', None)
    is_admin = request.user.is_superuser or request.user.role in [User.Role.SUPER_ADMIN, User.Role.COLLEGE_ADMIN]

    if request.method == 'POST':
        if not student:
            messages.error(request, "Student profile required to submit an out-pass request.")
            return redirect('hostel:outpass')

        pass_type = request.POST.get('pass_type', HostelOutPass.PassType.LOCAL_OUTING)
        destination = request.POST.get('destination', '').strip()
        reason = request.POST.get('reason', '').strip()
        contact_phone = request.POST.get('contact_phone', '').strip() or '+91 98401 23456'
        parent_phone = request.POST.get('parent_phone', '').strip() or '+91 94440 98765'
        dep_str = request.POST.get('departure_time')
        ret_str = request.POST.get('expected_return_time')

        now = timezone.now()
        try:
            from django.utils.dateparse import parse_datetime
            departure_time = parse_datetime(dep_str) if dep_str else now
            expected_return_time = parse_datetime(ret_str) if ret_str else now + timezone.timedelta(hours=4)
        except Exception:
            departure_time = now
            expected_return_time = now + timezone.timedelta(hours=4)

        if not departure_time:
            departure_time = now
        if not expected_return_time:
            expected_return_time = now + timezone.timedelta(hours=4)

        if destination and reason:
            import random
            rand_code = random.randint(1000, 9999)
            pass_code = f"OP-2026-CIT-{rand_code}"
            
            auto_approve = (pass_type == HostelOutPass.PassType.LOCAL_OUTING)
            status = HostelOutPass.Status.APPROVED if auto_approve else HostelOutPass.Status.PENDING

            outpass = HostelOutPass.objects.create(
                pass_code=pass_code,
                student=student,
                hostel=hostel or student.assigned_hostel or Hostel.objects.first(),
                pass_type=pass_type,
                destination=destination,
                reason=reason,
                contact_phone=contact_phone,
                parent_phone=parent_phone,
                departure_time=departure_time,
                expected_return_time=expected_return_time,
                status=status,
                approval_notes="Auto-verified digital pass for daytime outing." if auto_approve else "Awaiting warden review."
            )
            if auto_approve:
                messages.success(request, f"Out-Pass {outpass.pass_code} approved! Present your QR pass at Main Gate.")
            else:
                messages.success(request, f"Out-Pass {outpass.pass_code} submitted. Warden notification sent.")
            return redirect('hostel:outpass')
        else:
            messages.error(request, "Please enter destination and reason for the out-pass.")

    if is_admin:
        all_outpasses = HostelOutPass.objects.filter(hostel=hostel).select_related('student', 'student__user')
        my_outpasses = all_outpasses[:20]
        pending_outpasses = all_outpasses.filter(status=HostelOutPass.Status.PENDING)
    else:
        my_outpasses = HostelOutPass.objects.filter(student=student) if student else []
        pending_outpasses = []

    return render(request, 'hostel/outpass.html', {
        'hostel': hostel,
        'student': student,
        'my_outpasses': my_outpasses,
        'pending_outpasses': pending_outpasses,
        'is_admin': is_admin,
        'pass_types': HostelOutPass.PassType.choices,
        'statuses': HostelOutPass.Status.choices,
    })


@login_required
def outpass_action_view(request, pass_id):
    """Warden / Admin quick action for approving, rejecting, or marking an outpass returned."""
    user = request.user
    if not (user.is_superuser or user.role in [User.Role.SUPER_ADMIN, User.Role.COLLEGE_ADMIN]):
        messages.error(request, "Only authorized wardens can manage out-passes.")
        return redirect('hostel:outpass')

    outpass = get_object_or_404(HostelOutPass, id=pass_id)
    action = request.POST.get('action')

    if action == 'approve':
        outpass.status = HostelOutPass.Status.APPROVED
        outpass.approved_by = user
        outpass.approval_notes = f"Approved by {user.get_full_name() or user.username} on {timezone.now().strftime('%d %b %H:%M')}."
        outpass.save()
        messages.success(request, f"Out-Pass {outpass.pass_code} for {outpass.student.get_display_name()} approved.")
    elif action == 'reject':
        outpass.status = HostelOutPass.Status.REJECTED
        outpass.approved_by = user
        outpass.approval_notes = f"Rejected by {user.get_full_name() or user.username}."
        outpass.save()
        messages.warning(request, f"Out-Pass {outpass.pass_code} rejected.")
    elif action == 'return':
        outpass.status = HostelOutPass.Status.COMPLETED
        outpass.actual_return_time = timezone.now()
        outpass.save()
        messages.success(request, f"Student {outpass.student.get_display_name()} marked returned.")

    return redirect('hostel:outpass')


@login_required
@hostel_access_required
def room_allocate_view(request):
    """
    Room Allocation & Reallocation for Hostels.
    Warden / Admin can assign resident students to available rooms.
    """
    user = request.user
    is_admin = user.is_superuser or user.role in [User.Role.SUPER_ADMIN, User.Role.COLLEGE_ADMIN]
    hostel = _get_student_hostel(request)

    if request.method == 'POST' and is_admin:
        student_id = request.POST.get('student_id')
        room_number = request.POST.get('room_number')

        target_student = Student.objects.filter(student_id=student_id).first()
        target_room = HostelRoom.objects.filter(hostel=hostel, room_number=room_number).first()

        if target_student and target_room:
            target_student.assigned_hostel = hostel
            target_student.room_number = room_number
            target_student.accommodation_type = Student.AccommodationType.HOSTEL
            target_student.save()

            current_occupants = Student.objects.filter(assigned_hostel=hostel, room_number=room_number).count()
            target_room.occupied = current_occupants
            target_room.is_available = (current_occupants < target_room.capacity)
            target_room.save()

            messages.success(request, f"Student {target_student.get_display_name()} assigned to {hostel.code} Room {room_number}.")
        else:
            messages.error(request, "Student or room record not found.")
        return redirect('hostel:rooms')

    return redirect('hostel:rooms')


@login_required
def api_mess_checkin(request):
    """Real-time mess meal check-in API."""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST required'}, status=405)

    student = getattr(request.user, 'student_profile', None)
    if not student or not student.assigned_hostel:
        return JsonResponse({'status': 'error', 'message': 'Resident student profile required.'}, status=403)

    meal_type = request.POST.get('meal_type', HostelMessAttendance.MealType.LUNCH)
    diet = request.POST.get('diet', 'Vegetarian')
    today = timezone.now().date()

    record, created = HostelMessAttendance.objects.update_or_create(
        student=student,
        date=today,
        meal_type=meal_type,
        defaults={
            'hostel': student.assigned_hostel,
            'is_present': True,
            'special_diet': diet
        }
    )

    headcount = HostelMessAttendance.objects.filter(
        hostel=student.assigned_hostel,
        date=today,
        meal_type=meal_type,
        is_present=True
    ).count()

    return JsonResponse({
        'status': 'success',
        'message': f"Checked in for {record.get_meal_type_display()}!",
        'meal_type': meal_type,
        'kitchen_headcount': headcount,
        'date': str(today)
    })

