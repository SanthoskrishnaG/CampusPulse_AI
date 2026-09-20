from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from apps.accounts.decorators import role_required
from ml.registry.registry import ModelRegistry
from apps.common.views import SIMULATION_STATE

@login_required
def command_center_dashboard(request):
    """
    CampusPulse Master Command Center:
    Unified administrative telemetry across Academics, Complaints, Transport,
    Parking, Canteen, Energy, and Sustainability.
    """
    from apps.students.models import Student
    from apps.faculty.models import Faculty
    from apps.departments.models import Department
    from apps.academics.models import AcademicRiskAssessment
    from apps.events.models import Event
    from apps.clubs.models import Club
    from apps.complaints.models import Complaint
    from apps.transport.models import Bus
    from apps.parking.models import ParkingLot
    from apps.energy.models import EnergyAnomaly, EnergyReading
    from apps.canteen.models import MealRecord
    from apps.waste.models import WasteRecord

    # Core Stats
    total_students = Student.objects.count()
    total_faculty = Faculty.objects.count()
    total_departments = Department.objects.count()
    total_events = Event.objects.count()
    total_clubs = Club.objects.count()

    # Academic Risk breakdown
    risk_high = AcademicRiskAssessment.objects.filter(risk_level='HIGH').count()
    risk_med = AcademicRiskAssessment.objects.filter(risk_level='MEDIUM').count()
    risk_low = AcademicRiskAssessment.objects.filter(risk_level='LOW').count()

    # Complaints breakdown
    open_complaints = Complaint.objects.exclude(status__in=['RESOLVED', 'REJECTED']).count()
    urgent_complaints = Complaint.objects.filter(priority='URGENT').exclude(status='RESOLVED').count()

    # Transport
    buses = Bus.objects.filter(is_active=True)
    avg_bus_occupancy = round(sum(b.occupancy_percentage() for b in buses) / max(len(buses), 1), 1)

    # Parking
    lots = ParkingLot.objects.filter(is_active=True)
    total_slots = sum(l.total_slots for l in lots)
    occupied_slots = sum(l.occupied_count() for l in lots)
    parking_occ_pct = round((occupied_slots / max(total_slots, 1)) * 100.0, 1)

    # Energy
    active_anomalies = EnergyAnomaly.objects.filter(resolved=False).count()

    context = {
        'total_students': total_students,
        'total_faculty': total_faculty,
        'total_departments': total_departments,
        'total_events': total_events,
        'total_clubs': total_clubs,
        'risk_high': risk_high,
        'risk_med': risk_med,
        'risk_low': risk_low,
        'open_complaints': open_complaints,
        'urgent_complaints': urgent_complaints,
        'bus_count': len(buses),
        'avg_bus_occupancy': avg_bus_occupancy,
        'parking_occ_pct': parking_occ_pct,
        'active_anomalies': active_anomalies,
        'simulation': SIMULATION_STATE,
    }
    return render(request, 'analytics/command_center.html', context)

@login_required
@role_required('SUPER_ADMIN', 'COLLEGE_ADMIN')
def model_registry_view(request):
    """
    ML/DL Model Governance & Monitoring Dashboard:
    Displays registered models, versions, evaluation metrics, live prediction volume,
    latency telemetry, and retraining controls.
    """
    from apps.analytics.models import MLPredictionLog, MLTrainingRun, ModelFeedback, ModelDriftRecord
    models_dict = ModelRegistry.get_all_models()

    total_predictions = MLPredictionLog.objects.count()
    recent_logs = list(MLPredictionLog.objects.all()[:50])
    avg_latency = (
        round(sum(l.latency_ms for l in recent_logs) / len(recent_logs), 1)
        if recent_logs else 0.0
    )

    recent_training_runs = MLTrainingRun.objects.all()[:8]
    recent_predictions = MLPredictionLog.objects.all()[:10]
    recent_feedback = ModelFeedback.objects.all()[:5]
    drift_records = ModelDriftRecord.objects.all()[:5]

    context = {
        'models': models_dict,
        'total_predictions': total_predictions,
        'avg_latency': avg_latency,
        'recent_training_runs': recent_training_runs,
        'recent_predictions': recent_predictions,
        'recent_feedback': recent_feedback,
        'drift_records': drift_records,
    }
    return render(request, 'analytics/model_registry.html', context)

@login_required
@role_required('SUPER_ADMIN', 'COLLEGE_ADMIN')
def trigger_model_retrain_api(request, model_name):
    """
    Triggers re-training and re-evaluation of an ML/DL model pipeline.
    """
    try:
        if 'Academic' in model_name:
            from ml.academic.train import train_academic_risk_models
            from ml.academic.sequential_model import SequentialStudentTrajectoryModel
            train_academic_risk_models()
            SequentialStudentTrajectoryModel().train_and_save()
        elif 'Complaint' in model_name:
            from ml.complaints.train import train_complaint_classifier
            train_complaint_classifier()
        elif 'Event' in model_name:
            from ml.events.train import train_event_attendance_model
            train_event_attendance_model()
        elif 'Food_Waste' in model_name or 'Waste' in model_name:
            from ml.canteen.waste_train import train_food_waste_model
            train_food_waste_model()
        elif 'Canteen' in model_name:
            from ml.canteen.train import train_canteen_demand_model
            train_canteen_demand_model()
        elif 'Energy' in model_name:
            from ml.energy.train import train_energy_anomaly_model
            train_energy_anomaly_model()
        elif 'Transport' in model_name:
            from ml.transport.train import train_transport_models
            train_transport_models()
        elif 'Parking' in model_name:
            from ml.parking.train import train_parking_model
            train_parking_model()

        messages.success(request, f"Successfully retrained, evaluated, and deployed {model_name}!")
    except Exception as e:
        messages.error(request, f"Retraining failed: {str(e)}")

    return redirect('analytics:model_registry')
