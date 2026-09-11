import random
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import ParkingLot, ParkingSlot
from apps.common.views import SIMULATION_STATE

def parking_dashboard(request):
    """
    Smart Parking Command Center:
    Visual bay map, occupancy meters, real-time vacancies, and peak hour predictions.
    """
    lots = ParkingLot.objects.filter(is_active=True).prefetch_related('slots')
    selected_code = request.GET.get('lot')
    current_lot = lots.filter(code=selected_code).first() if selected_code else lots.first()

    slots = current_lot.slots.all() if current_lot else []

    # Occupancy predictions based on current time
    from django.utils import timezone
    hour = timezone.now().hour
    if 9 <= hour <= 11 or 13 <= hour <= 15:
        peak_status = "High Demand (Academic Core Hours)"
        predicted_trend = "Occupancy expected to remain above 85% until 4:00 PM"
    else:
        peak_status = "Moderate / Low Demand"
        predicted_trend = "Surplus vacancies available across all zones"

    return render(request, 'parking/dashboard.html', {
        'lots': lots,
        'current_lot': current_lot,
        'slots': slots,
        'peak_status': peak_status,
        'predicted_trend': predicted_trend,
    })

@csrf_exempt
def toggle_slot_api(request, slot_id):
    """
    Interactive simulation endpoint: simulate vehicle entry/exit on a specific slot.
    """
    slot = get_object_or_404(ParkingSlot, id=slot_id)
    slot.is_occupied = not slot.is_occupied
    slot.save()
    return JsonResponse({
        'status': 'ok',
        'slot_id': slot.id,
        'is_occupied': slot.is_occupied,
        'lot_occupancy': slot.lot.occupancy_percentage()
    })

def parking_telemetry_api(request):
    """
    JSON telemetry endpoint for real-time parking occupancy polling.
    """
    lots = ParkingLot.objects.filter(is_active=True)
    data = []
    for lot in lots:
        data.append({
            'code': lot.code,
            'name': lot.name,
            'total': lot.total_slots,
            'occupied': lot.occupied_count(),
            'available': lot.available_count(),
            'occupancy_pct': lot.occupancy_percentage()
        })
    return JsonResponse({'status': 'ok', 'lots': data})
