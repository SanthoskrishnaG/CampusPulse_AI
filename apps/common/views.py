import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from .models import CampusLocation, AuditLog
from apps.accounts.decorators import role_required

# In-memory simulation state (Start, Pause, Reset, 1x, 2x, 5x, 10x)
SIMULATION_STATE = {
    'running': True,
    'speed': 1.0,
    'step': 0,
    'bus_progress': 0.15,
    'parking_occupancy_factor': 0.72,
    'energy_spike_active': False
}

def home_view(request):
    """
    Public landing page for CampusPulse AI showcasing key capabilities,
    campus telemetry highlights, and entry points.
    """
    if request.user.is_authenticated:
        return redirect('accounts:role_redirect')

    # Seeded / Live summary counters
    from apps.students.models import Student
    from apps.events.models import Event
    from apps.clubs.models import Club
    from apps.complaints.models import Complaint

    try:
        student_count = Student.objects.count()
        event_count = Event.objects.count()
        club_count = Club.objects.count()
        complaint_count = Complaint.objects.count()
    except Exception:
        student_count = 520
        event_count = 114
        club_count = 22
        complaint_count = 538

    context = {
        'student_count': student_count,
        'event_count': event_count,
        'club_count': club_count,
        'complaint_count': complaint_count,
    }
    return render(request, 'common/home.html', context)

def map_view(request):
    """
    Interactive Leaflet AI Campus Map with all campus locations.
    """
    locations = CampusLocation.objects.filter(is_active=True)
    return render(request, 'common/map.html', {'locations': locations})

def map_locations_api(request):
    """
    JSON endpoint for Leaflet map loading campus coordinates.
    """
    locations = CampusLocation.objects.filter(is_active=True).values(
        'id', 'name', 'code', 'category', 'latitude', 'longitude', 'floor_count', 'capacity', 'description'
    )
    return JsonResponse(list(locations), safe=False)

@csrf_exempt
def simulation_control_api(request):
    """
    Controllable multi-speed campus simulator (1x, 2x, 5x, 10x).
    """
    global SIMULATION_STATE
    if request.method == 'POST':
        try:
            data = json.loads(request.body) if request.body else request.POST
            action = data.get('action')
            speed = float(data.get('speed', SIMULATION_STATE['speed']))

            if action == 'start':
                SIMULATION_STATE['running'] = True
            elif action == 'pause':
                SIMULATION_STATE['running'] = False
            elif action == 'reset':
                SIMULATION_STATE['step'] = 0
                SIMULATION_STATE['bus_progress'] = 0.0
            
            if speed in [1.0, 2.0, 5.0, 10.0]:
                SIMULATION_STATE['speed'] = speed

            return JsonResponse({'status': 'ok', 'simulation': SIMULATION_STATE})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse(SIMULATION_STATE)

@login_required
@role_required('SUPER_ADMIN', 'COLLEGE_ADMIN')
def audit_log_view(request):
    """
    Administrative audit trail table with search and pagination.
    """
    logs_list = AuditLog.objects.select_related('user').all()
    q = request.GET.get('q')
    if q:
        logs_list = logs_list.filter(action__icontains=q) | logs_list.filter(details__icontains=q)
    
    paginator = Paginator(logs_list, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'common/audit_logs.html', {'page_obj': page_obj, 'q': q})

def global_search_api(request):
    """
    Fast, categorized global campus search endpoint (Ctrl+K).
    Searches Students, Events, Departments, Clubs, Complaints, Buses, and Campus Locations.
    """
    query = request.GET.get('q', '').strip()
    if not query or len(query) < 2:
        return JsonResponse({'results': []})

    results = []

    # 1. Students
    try:
        from apps.students.models import Student
        students = Student.objects.filter(
            roll_number__icontains=query
        ).select_related('user', 'department')[:5]
        for s in students:
            results.append({
                'category': 'Students',
                'title': f"{s.user.get_full_name() or s.user.username} ({s.roll_number})",
                'subtitle': f"{s.department.name if s.department else 'General'} · Sem {s.current_semester}",
                'url': f"/students/{s.id}/",
                'badge': '🎓 Student'
            })
    except Exception:
        pass

    # 2. Events
    try:
        from apps.events.models import Event
        events = Event.objects.filter(title__icontains=query)[:5]
        for e in events:
            results.append({
                'category': 'Events',
                'title': e.title,
                'subtitle': f"{e.get_category_display()} · {e.start_time.strftime('%b %d, %H:%M')}",
                'url': f"/events/{e.id}/",
                'badge': '📅 Event'
            })
    except Exception:
        pass

    # 3. Departments
    try:
        from apps.departments.models import Department
        depts = Department.objects.filter(name__icontains=query)[:4]
        for d in depts:
            results.append({
                'category': 'Departments',
                'title': f"{d.name} ({d.code})",
                'subtitle': f"Block: {d.building_block} · HOD: {d.hod_name or 'Assigned'}",
                'url': f"/departments/{d.id}/",
                'badge': '🏛️ Department'
            })
    except Exception:
        pass

    # 4. Clubs
    try:
        from apps.clubs.models import Club
        clubs = Club.objects.filter(name__icontains=query)[:4]
        for c in clubs:
            results.append({
                'category': 'Clubs',
                'title': c.name,
                'subtitle': f"{c.get_category_display()} · {c.members_count} Members",
                'url': f"/clubs/{c.id}/",
                'badge': '✨ Club'
            })
    except Exception:
        pass

    # 5. Complaints
    try:
        from apps.complaints.models import Complaint
        complaints = Complaint.objects.filter(
            ticket_number__icontains=query
        ) | Complaint.objects.filter(title__icontains=query)[:4]
        for cp in complaints[:4]:
            results.append({
                'category': 'Complaints',
                'title': f"{cp.ticket_number}: {cp.title[:35]}",
                'subtitle': f"Category: {cp.nlp_predicted_category or cp.category} · Priority: {cp.priority}",
                'url': f"/complaints/{cp.id}/",
                'badge': '🛠️ Ticket'
            })
    except Exception:
        pass

    # 6. Transport / Buses
    try:
        from apps.transport.models import Bus
        buses = Bus.objects.filter(bus_number__icontains=query)[:3]
        for b in buses:
            results.append({
                'category': 'Transport',
                'title': f"Bus {b.bus_number}",
                'subtitle': f"Route: {b.route.route_name if b.route else 'Campus Shuttle'}",
                'url': "/transport/",
                'badge': '🚌 Bus'
            })
    except Exception:
        pass

    # 7. Campus Locations / Buildings
    try:
        locations = CampusLocation.objects.filter(name__icontains=query)[:4]
        for loc in locations:
            results.append({
                'category': 'Campus Map',
                'title': f"{loc.name} ({loc.code})",
                'subtitle': f"Category: {loc.get_category_display()} · Capacity: {loc.capacity}",
                'url': f"/map/?lat={loc.latitude}&lng={loc.longitude}",
                'badge': '📍 Location'
            })
    except Exception:
        pass

    return JsonResponse({'results': results})

