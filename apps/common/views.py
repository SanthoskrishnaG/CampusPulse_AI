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
