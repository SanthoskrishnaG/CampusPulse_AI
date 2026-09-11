import time
import math
from django.utils import timezone
from .models import Bus, BusRoute, BusStop
from apps.common.views import SIMULATION_STATE

class TransportSimulationEngine:
    """
    Realistic Campus Bus Movement Simulator.
    Interpolates bus location along its designated route stops based on simulation clock
    and speed multiplier (1x, 2x, 5x, 10x) without erratic teleportation.
    """

    @classmethod
    def get_live_bus_telemetry(cls):
        buses = Bus.objects.filter(is_active=True).select_related('route')
        speed_multiplier = SIMULATION_STATE.get('speed', 1.0)
        is_running = SIMULATION_STATE.get('running', True)

        # Simulation clock based on current time
        t = time.time() * (speed_multiplier if is_running else 0.0)

        telemetry = []
        for i, bus in enumerate(buses):
            if not bus.route:
                continue

            stops = list(bus.route.stops.order_by('sequence'))
            if len(stops) < 2:
                continue

            # Calculate route progression (0.0 to 1.0) with offset per bus
            cycle_duration = max(bus.route.estimated_duration_mins * 60.0 / max(speed_multiplier, 0.1), 30.0)
            progress = ((t + (i * 120)) % cycle_duration) / cycle_duration

            # Determine which stop segment the bus is currently traversing
            num_segments = len(stops) - 1
            segment_idx = int(progress * num_segments)
            segment_idx = min(segment_idx, num_segments - 1)
            seg_progress = (progress * num_segments) - segment_idx

            stop_a = stops[segment_idx]
            stop_b = stops[segment_idx + 1]

            # Linear interpolation between stop A and stop B
            lat = stop_a.latitude + (stop_b.latitude - stop_a.latitude) * seg_progress
            lng = stop_a.longitude + (stop_b.longitude - stop_a.longitude) * seg_progress

            # ETA calculation (remaining time along route)
            remaining_mins = max(1, int((1.0 - progress) * bus.route.estimated_duration_mins))
            
            # Delay prediction based on passenger count and morning/evening peak hours
            now = timezone.now()
            hour = now.hour
            is_peak = 1 if (8 <= hour <= 10 or 16 <= hour <= 18) else 0
            predicted_delay = int(is_peak * 6 + (bus.occupancy_percentage() > 85) * 4)

            telemetry.append({
                'bus_id': bus.id,
                'bus_number': bus.bus_number,
                'route_name': bus.route.name,
                'route_code': bus.route.code,
                'latitude': round(lat, 6),
                'longitude': round(lng, 6),
                'current_passengers': bus.current_passengers,
                'capacity': bus.capacity,
                'occupancy_pct': bus.occupancy_percentage(),
                'next_stop': stop_b.name,
                'eta_mins': remaining_mins,
                'predicted_delay_mins': predicted_delay,
                'speed_kmh': round(28.0 + math.sin(t * 0.1) * 8.0, 1),
                'status': 'ON_TIME' if predicted_delay < 5 else 'DELAYED'
            })

        return telemetry
