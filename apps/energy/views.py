from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from .models import EnergyMeter, EnergyReading, EnergyAnomaly
from ml.energy.detect import EnergyAnomalyDetector

def energy_dashboard(request):
    """
    Campus Energy Operations Center:
    Real-time kWh telemetry, meter breakdown, and anomaly alerts.
    """
    meters = EnergyMeter.objects.filter(is_active=True).prefetch_related('anomalies')
    recent_readings = EnergyReading.objects.select_related('meter')[:15]
    active_anomalies = EnergyAnomaly.objects.filter(resolved=False).select_related('meter')[:10]

    # Calculate total current load
    total_current_kwh = sum(m.baseline_kwh for m in meters)

    return render(request, 'energy/dashboard.html', {
        'meters': meters,
        'recent_readings': recent_readings,
        'active_anomalies': active_anomalies,
        'total_current_kwh': round(total_current_kwh, 1),
    })

def trigger_energy_scan(request):
    """
    Scans all meters with simulated live sensor readings and Isolation Forest.
    """
    now = timezone.now()
    hour = now.hour
    is_weekend = now.weekday() >= 5

    meters = EnergyMeter.objects.filter(is_active=True)
    detected = 0

    import random
    for m in meters:
        # Simulate current load
        if hour < 6 or hour > 20:
            reading_kwh = random.uniform(8.0, 22.0)
            if random.random() < 0.2: # Trigger anomaly on 1 meter for demonstration
                reading_kwh = random.uniform(55.0, 78.0)
        else:
            reading_kwh = m.baseline_kwh + random.uniform(-6.0, 15.0)

        reading = EnergyReading.objects.create(
            meter=m,
            kwh_consumed=round(reading_kwh, 1),
            temperature=28.0,
            occupancy_estimate=80
        )

        result = EnergyAnomalyDetector.inspect_reading(
            hour=hour,
            is_weekend=is_weekend,
            occupancy=80,
            kwh=reading_kwh,
            baseline=m.baseline_kwh
        )

        if result.get('is_anomaly'):
            EnergyAnomaly.objects.create(
                meter=m,
                reading=reading,
                anomaly_score=result['anomaly_score'],
                kwh_observed=result['kwh_observed'],
                kwh_expected=result['kwh_expected'],
                severity=result['severity'],
                anomaly_type=result['anomaly_type'],
                explanation=result['explanation']
            )
            detected += 1

    return JsonResponse({'status': 'ok', 'meters_scanned': len(meters), 'anomalies_detected': detected})
