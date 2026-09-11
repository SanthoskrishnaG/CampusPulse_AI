from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from .models import TrafficObservation
from .detector import VehicleDetector

def traffic_dashboard(request):
    """
    Traffic & Gate Surveillance Dashboard:
    Live vehicle counts, congestion level gauges, and video/image analysis portal.
    """
    recent_observations = TrafficObservation.objects.all()[:10]
    latest = recent_observations.first()

    return render(request, 'traffic/dashboard.html', {
        'recent_observations': recent_observations,
        'latest': latest,
    })

def analyze_traffic_feed(request):
    """
    Upload image from campus CCTV or smartphone camera to run vehicle detection.
    """
    if request.method == 'POST' and request.FILES.get('image'):
        uploaded_img = request.FILES['image']
        location_name = request.POST.get('location_name', 'Campus Main Entrance')

        obs = TrafficObservation.objects.create(
            location_name=location_name,
            image=uploaded_img
        )

        # Run detection
        results = VehicleDetector.detect_vehicles(obs.image.path)

        obs.total_vehicles = results['total_vehicles']
        obs.car_count = results['car_count']
        obs.motorcycle_count = results['motorcycle_count']
        obs.bus_count = results['bus_count']
        obs.truck_count = results['truck_count']
        obs.congestion_level = results['congestion_level']
        obs.confidence = results['confidence']
        obs.save()

        messages.success(
            request,
            f"Analysis complete! Detected {obs.total_vehicles} vehicles ({obs.car_count} cars, {obs.motorcycle_count} bikes, {obs.bus_count} buses). Congestion status: {obs.get_congestion_level_display()}."
        )
        return redirect('traffic:dashboard')

    return redirect('traffic:dashboard')
