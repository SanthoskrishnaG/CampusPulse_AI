from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Bus, BusRoute, BusStop
from .simulation import TransportSimulationEngine

def transport_dashboard(request):
    """
    Fleet Command Center: Live bus trackers, occupancy gauges, route status,
    and simulated GPS telemetry.
    """
    buses = Bus.objects.filter(is_active=True).select_related('route')
    routes = BusRoute.objects.filter(is_active=True).prefetch_related('stops')
    live_buses = TransportSimulationEngine.get_live_bus_telemetry()

    return render(request, 'transport/dashboard.html', {
        'buses': buses,
        'routes': routes,
        'live_buses': live_buses,
    })

def live_telemetry_api(request):
    """
    Real-time polling endpoint for live bus map markers and passenger telemetry.
    """
    data = TransportSimulationEngine.get_live_bus_telemetry()
    return JsonResponse({'status': 'ok', 'buses': data})

def route_list(request):
    routes = BusRoute.objects.filter(is_active=True).prefetch_related('stops', 'buses')
    return render(request, 'transport/routes.html', {'routes': routes})
