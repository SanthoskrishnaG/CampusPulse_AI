import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Bus, BusRoute, BusStop
from .simulation import TransportSimulationEngine
from apps.common.views import SIMULATION_STATE

def transport_dashboard(request):
    """
    Fleet Command Center: Live bus trackers, occupancy gauges, route status,
    and simulated GPS telemetry across routes R-01 to R-04.
    """
    buses = Bus.objects.filter(is_active=True).select_related('route')
    routes = BusRoute.objects.filter(is_active=True).prefetch_related('stops')
    live_buses = TransportSimulationEngine.get_live_bus_telemetry()

    routes_data = []
    for r in routes:
        stops_list = [
            {
                'id': s.id,
                'name': s.name,
                'sequence': s.sequence,
                'latitude': s.latitude,
                'longitude': s.longitude,
                'offset_mins': s.estimated_offset_mins
            }
            for s in r.stops.all()
        ]
        routes_data.append({
            'id': r.id,
            'code': r.code,
            'name': r.name,
            'start_point': r.start_point,
            'end_point': r.end_point,
            'distance_km': r.distance_km,
            'estimated_duration_mins': r.estimated_duration_mins,
            'stops': stops_list
        })

    return render(request, 'transport/dashboard.html', {
        'buses': buses,
        'routes': routes,
        'routes_json': json.dumps(routes_data),
        'live_buses': live_buses,
        'simulation_state': SIMULATION_STATE,
    })

def live_telemetry_api(request):
    """
    Real-time polling endpoint for live bus map markers and passenger telemetry.
    Supports optional corridor filter (e.g. ?route=R-01).
    """
    route_filter = request.GET.get('route')
    data = TransportSimulationEngine.get_live_bus_telemetry()
    if route_filter:
        data = [b for b in data if b.get('route_code') == route_filter]
    return JsonResponse({
        'status': 'ok',
        'simulation': SIMULATION_STATE,
        'buses': data
    })

def route_list(request):
    routes = BusRoute.objects.filter(is_active=True).prefetch_related('stops', 'buses')
    return render(request, 'transport/routes.html', {'routes': routes})
