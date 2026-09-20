import json
import time
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.conf import settings

from apps.accounts.models import User
from apps.students.models import Student
from apps.transport.models import Bus
from apps.parking.models import ParkingLot
from apps.analytics.models import MLModelRecord, MLPredictionLog, MLTrainingRun, ModelFeedback, ModelDriftRecord
from ml.academic.predict import AcademicRiskPredictor
from ml.canteen.predict import CanteenDemandPredictor
from ml.canteen.waste_predict import FoodWastePredictor
from ml.hostel.mess_forecaster import HostelMessDemandForecaster
from ml.complaints.predict import ComplaintAITriage
from ml.complaints.duplicate import DuplicateComplaintDetector
from ml.energy.detect import EnergyAnomalyDetector
from ml.transport.predict import TransportETAPredictor
from ml.parking.predict import ParkingOccupancyPredictor
from ml.registry.registry import ModelRegistry

def error_response(message: str, status: int = 400, model: str = None, version: str = None):
    return JsonResponse({
        'success': False,
        'prediction': None,
        'message': message,
        'model': model,
        'model_version': version,
        'timestamp': timezone.now().isoformat()
    }, status=status)


@csrf_exempt
@login_required
def api_academic_risk_predict(request):
    """
    POST /api/ml/academic-risk/predict/
    Role-gated inference: Students can only predict their own risk;
    Faculty and Admins can query any assigned student.
    """
    if request.method != 'POST':
        return error_response("Method not allowed. Use POST.", status=405)

    try:
        data = json.loads(request.body) if request.body else {}
    except Exception:
        data = {}

    student_id = data.get('student_id')
    user = request.user

    if student_id:
        try:
            target_student = Student.objects.get(student_id=student_id)
        except Student.DoesNotExist:
            return error_response(f"Student '{student_id}' not found.", status=404)
    else:
        # Default to logged-in user's student profile
        target_student = getattr(user, 'student_profile', None)
        if not target_student:
            return error_response("No student specified and authenticated user has no student profile.", status=400)

    # RBAC boundary: A student cannot query other students' academic risk
    is_admin_or_faculty = user.is_superuser or getattr(user, 'role', '') in [
        User.Role.SUPER_ADMIN, User.Role.COLLEGE_ADMIN, User.Role.DEPARTMENT_ADMIN, User.Role.FACULTY
    ]
    if not is_admin_or_faculty and target_student.user != user:
        return error_response("Forbidden: You can only query your own academic risk profile.", status=403)

    result = AcademicRiskPredictor.predict_student_risk(target_student)
    if not result.get('success'):
        return error_response(result.get('recommended_action', 'Prediction unavailable.'), status=503)

    return JsonResponse({
        'success': True,
        'model': result['model_name'],
        'model_version': result['model_version'],
        'student_id': target_student.student_id,
        'prediction': result['risk_level'],
        'risk_score': result['risk_score'],
        'confidence': result['confidence'],
        'factors': result['factors'],
        'recommended_action': result['recommended_action'],
        'latency_ms': result['latency_ms'],
        'data_mode': getattr(settings, 'DATA_MODE', 'DEMO'),
        'timestamp': timezone.now().isoformat()
    })


def api_canteen_demand_forecast(request):
    """
    GET /api/ml/canteen/demand/
    Forecasts meal demand and recommended prep buffer for campus dining.
    """
    now = timezone.now()
    try:
        day_of_week = int(request.GET.get('day_of_week', now.weekday()))
    except ValueError:
        day_of_week = now.weekday()

    meal_type = request.GET.get('meal_type', 'LUNCH').upper()
    is_event = request.GET.get('is_event', '0') in ('1', 'true', 'True')
    student_base = int(request.GET.get('student_base', 520))

    result = CanteenDemandPredictor.predict_meal_demand(
        day_of_week=day_of_week,
        meal_type=meal_type,
        is_event_day=is_event,
        student_base=student_base,
        user=request.user if request.user.is_authenticated else None
    )

    if not result.get('success'):
        return error_response(result.get('message', 'Prediction unavailable.'), status=503)

    return JsonResponse({
        'success': True,
        'model': result['model'],
        'model_version': result['version'],
        'meal_type': meal_type,
        'prediction': result['predicted_demand'],
        'recommended_prep': result['recommended_prep'],
        'advice': result['advice'],
        'latency_ms': result['latency_ms'],
        'data_mode': getattr(settings, 'DATA_MODE', 'DEMO'),
        'timestamp': timezone.now().isoformat()
    })


@csrf_exempt
def api_food_waste_predict(request):
    """
    POST /api/ml/canteen/waste/predict/
    Forecasts post-service leftover organic food waste (kg).
    """
    if request.method != 'POST':
        return error_response("Method not allowed. Use POST.", status=405)

    try:
        data = json.loads(request.body) if request.body else {}
    except Exception:
        data = {}

    meals_prepared = data.get('meals_prepared')
    predicted_demand = data.get('predicted_demand')
    meal_type = data.get('meal_type', 'LUNCH')
    day_of_week = data.get('day_of_week', timezone.now().weekday())
    is_event = bool(data.get('is_event', False))

    if meals_prepared is None or predicted_demand is None:
        return error_response("meals_prepared and predicted_demand are required numeric fields.", status=400)

    try:
        result = FoodWastePredictor.predict_waste(
            meals_prepared=int(meals_prepared),
            predicted_demand=int(predicted_demand),
            meal_type=str(meal_type),
            day_of_week=int(day_of_week),
            is_event=is_event
        )
    except Exception as e:
        return error_response(f"Invalid input: {e}", status=400)

    if not result.get('success'):
        return error_response(result.get('message', 'Prediction unavailable.'), status=503)

    return JsonResponse({
        'success': True,
        'model': result['model'],
        'model_version': result['version'],
        'prediction': result['predicted_waste_kg'],
        'surplus_portions': result['surplus_portions'],
        'advice': result['advice'],
        'data_mode': getattr(settings, 'DATA_MODE', 'DEMO'),
        'timestamp': timezone.now().isoformat()
    })


@login_required
def api_hostel_mess_demand(request):
    """
    GET /api/ml/hostel/mess/demand/
    Forecasts residential hostel mess attendance for BH-1, BH-2, GH-1, GH-2.
    Hostel students can only query their own assigned hostel; Admins have full oversight.
    """
    hostel_code = request.GET.get('hostel_code', 'BH-1').upper().strip()
    user = request.user

    is_admin = user.is_superuser or getattr(user, 'role', '') in [User.Role.SUPER_ADMIN, User.Role.COLLEGE_ADMIN]
    if not is_admin:
        student = getattr(user, 'student_profile', None)
        if not student or student.accommodation_type != Student.AccommodationType.HOSTEL:
            return error_response("Forbidden: Hostel mess forecasts are restricted to authorized hostel students.", status=403)
        if student.assigned_hostel and student.assigned_hostel.code != hostel_code:
            return error_response(f"Forbidden: You cannot query mess telemetry for {hostel_code}.", status=403)

    now = timezone.now()
    day_of_week = int(request.GET.get('day_of_week', now.weekday()))
    meal_type = request.GET.get('meal_type', 'DINNER').upper()
    is_event = request.GET.get('is_event', '0') in ('1', 'true', 'True')

    result = HostelMessDemandForecaster.forecast_hostel_mess(
        hostel_code=hostel_code,
        day_of_week=day_of_week,
        meal_type=meal_type,
        is_event=is_event
    )

    if not result.get('success'):
        return error_response(result.get('message', 'Prediction unavailable.'), status=503)

    return JsonResponse({
        'success': True,
        'model': result['model'],
        'model_version': result['version'],
        'hostel_code': result['hostel_code'],
        'meal_type': result['meal_type'],
        'prediction': result['predicted_demand'],
        'recommended_prep': result['recommended_prep'],
        'expected_waste_kg': result['expected_waste_kg'],
        'advice': result['advice'],
        'data_mode': getattr(settings, 'DATA_MODE', 'DEMO'),
        'timestamp': timezone.now().isoformat()
    })


@csrf_exempt
def api_complaint_classify(request):
    """
    POST /api/ml/complaints/classify/
    NLP triage classifying raw natural language text into CIT department and priority.
    """
    if request.method != 'POST':
        return error_response("Method not allowed. Use POST.", status=405)

    try:
        data = json.loads(request.body) if request.body else {}
    except Exception:
        data = {}

    text = data.get('text', '').strip()
    if not text:
        return error_response("Complaint text is required.", status=400)

    try:
        result = ComplaintAITriage.triage_complaint(text, user=request.user if request.user.is_authenticated else None)
    except Exception as e:
        return error_response(f"Invalid input: {e}", status=400)

    if not result.get('success'):
        return error_response(result.get('message', 'Prediction unavailable.'), status=503)

    return JsonResponse({
        'success': True,
        'model': result['model_name'],
        'model_version': result['model_version'],
        'prediction': result['category'],
        'priority': result['priority'],
        'target_department': result['target_department'],
        'location_extracted': result['location_extracted'],
        'confidence': result['confidence'],
        'sla_hours': result['sla_hours'],
        'latency_ms': result['latency_ms'],
        'data_mode': getattr(settings, 'DATA_MODE', 'DEMO'),
        'timestamp': timezone.now().isoformat()
    })


@csrf_exempt
def api_complaint_check_duplicate(request):
    """
    POST /api/ml/complaints/check-duplicate/
    Evaluates incoming complaint text for cosine similarity against active unresolved issues.
    """
    if request.method != 'POST':
        return error_response("Method not allowed. Use POST.", status=405)

    try:
        data = json.loads(request.body) if request.body else {}
    except Exception:
        data = {}

    text = data.get('text', '').strip()
    category = data.get('category', None)

    if not text:
        return error_response("Complaint text is required.", status=400)

    result = DuplicateComplaintDetector.check_duplicate(text, category=category)
    return JsonResponse({
        'success': True,
        'model': "Duplicate_Complaint_TFIDF_Detector",
        'model_version': "1.0.0",
        'is_duplicate': result['is_duplicate'],
        'similarity_score': result['similarity_score'],
        'matched_complaint_id': result['matched_complaint_id'],
        'matched_complaint_title': result['matched_complaint_title'],
        'recommendation': result['recommendation'],
        'data_mode': getattr(settings, 'DATA_MODE', 'DEMO'),
        'timestamp': timezone.now().isoformat()
    })


@csrf_exempt
def api_energy_detect_anomaly(request):
    """
    POST /api/ml/energy/detect/
    Runs Isolation Forest unsupervised anomaly detection on real-time power reading.
    """
    if request.method != 'POST':
        return error_response("Method not allowed. Use POST.", status=405)

    try:
        data = json.loads(request.body) if request.body else {}
    except Exception:
        data = {}

    hour = data.get('hour', timezone.now().hour)
    is_weekend = bool(data.get('is_weekend', timezone.now().weekday() >= 5))
    occupancy = data.get('occupancy', 80)
    kwh = data.get('kwh_consumed')
    baseline = float(data.get('baseline', 45.0))

    if kwh is None:
        return error_response("kwh_consumed is a required float parameter.", status=400)

    try:
        result = EnergyAnomalyDetector.inspect_reading(
            hour=int(hour),
            is_weekend=is_weekend,
            occupancy=int(occupancy),
            kwh=float(kwh),
            baseline=baseline,
            user=request.user if request.user.is_authenticated else None
        )
    except Exception as e:
        return error_response(f"Invalid input: {e}", status=400)

    if not result.get('success'):
        return error_response(result.get('message', 'Prediction unavailable.'), status=503)

    return JsonResponse({
        'success': True,
        'model': result['model'],
        'model_version': result['version'],
        'is_anomaly': result['is_anomaly'],
        'prediction': "ANOMALY" if result['is_anomaly'] else "NORMAL",
        'anomaly_score': result['anomaly_score'],
        'severity': result['severity'],
        'anomaly_type': result['anomaly_type'],
        'explanation': result['explanation'],
        'latency_ms': result['latency_ms'],
        'data_mode': getattr(settings, 'DATA_MODE', 'DEMO'),
        'timestamp': timezone.now().isoformat()
    })


def api_transport_eta(request, bus_id: int):
    """
    GET /api/ml/transport/eta/<bus_id>/
    Computes real-time arrival duration and delay using Random Forest Regressor.
    """
    try:
        bus = Bus.objects.select_related('route').get(id=bus_id)
    except Bus.DoesNotExist:
        return error_response(f"Bus ID {bus_id} not found.", status=404)

    if not bus.route:
        return error_response(f"Bus {bus.bus_number} has no active assigned route.", status=400)

    stops = list(bus.route.stops.order_by('sequence'))
    stop_count = len(stops) if stops else 4

    result = TransportETAPredictor.predict_eta(
        distance_km=bus.route.distance_km,
        stop_sequence=stop_count,
        passenger_count=bus.current_passengers,
        capacity=bus.capacity
    )

    if not result.get('success'):
        return error_response(result.get('message', 'Prediction unavailable.'), status=503)

    return JsonResponse({
        'success': True,
        'model': result['model'],
        'model_version': result['version'],
        'bus_number': bus.bus_number,
        'route_code': bus.route.code,
        'prediction': result['eta_mins'],
        'predicted_delay_mins': result['predicted_delay_mins'],
        'status': result['status'],
        'occupancy_pct': result['occupancy_pct'],
        'data_mode': getattr(settings, 'DATA_MODE', 'DEMO'),
        'timestamp': timezone.now().isoformat()
    })


def api_parking_occupancy(request, lot_code: str):
    """
    GET /api/ml/parking/predict/<lot_code>/
    Forecasts occupancy count, vacancy, and congestion status.
    """
    try:
        lot = ParkingLot.objects.get(code=lot_code.upper())
    except ParkingLot.DoesNotExist:
        return error_response(f"Parking Lot '{lot_code}' not found.", status=404)

    now = timezone.now()
    hour = request.GET.get('hour', None)
    hour = int(hour) if hour is not None else now.hour

    result = ParkingOccupancyPredictor.predict_occupancy(
        total_slots=lot.total_slots,
        hour=hour
    )

    if not result.get('success'):
        return error_response(result.get('message', 'Prediction unavailable.'), status=503)

    return JsonResponse({
        'success': True,
        'model': result['model'],
        'model_version': result['version'],
        'lot_code': lot.code,
        'lot_name': lot.name,
        'total_slots': result['total_slots'],
        'current_occupied_live': lot.occupied_count(),
        'prediction': result['predicted_occupied'],
        'predicted_available': result['predicted_available'],
        'occupancy_percentage': result['occupancy_percentage'],
        'status': result['status'],
        'trend_summary': result['trend_summary'],
        'data_mode': getattr(settings, 'DATA_MODE', 'DEMO'),
        'timestamp': timezone.now().isoformat()
    })


@csrf_exempt
@login_required
def api_submit_feedback(request):
    """
    POST /api/ml/feedback/submit/
    Closes the real-world feedback loop by recording ground truth outcomes.
    """
    if request.method != 'POST':
        return error_response("Method not allowed. Use POST.", status=405)

    try:
        data = json.loads(request.body) if request.body else {}
    except Exception:
        data = {}

    model_name = data.get('model_name')
    actual_outcome = data.get('actual_outcome')
    log_id = data.get('prediction_log_id')
    notes = data.get('notes', '')

    if not model_name or actual_outcome is None:
        return error_response("model_name and actual_outcome are required fields.", status=400)

    pred_log = None
    error_delta = None
    if log_id:
        try:
            pred_log = MLPredictionLog.objects.get(id=log_id)
            # If both predicted and actual are float numbers, compute error delta
            try:
                p_val = float(pred_log.prediction)
                a_val = float(actual_outcome)
                error_delta = round(abs(p_val - a_val), 3)
            except (ValueError, TypeError):
                pass
        except MLPredictionLog.DoesNotExist:
            pass

    feedback = ModelFeedback.objects.create(
        prediction_log=pred_log,
        model_name=model_name,
        actual_outcome=str(actual_outcome),
        error_delta=error_delta,
        notes=notes,
        reported_by=request.user
    )

    return JsonResponse({
        'success': True,
        'feedback_id': feedback.id,
        'model_name': model_name,
        'error_delta': error_delta,
        'message': "Ground truth feedback successfully logged for model retraining calibration.",
        'timestamp': timezone.now().isoformat()
    })


@login_required
def api_monitoring_metrics(request):
    """
    GET /api/ml/monitoring/metrics/
    Returns real-time inference telemetry: total volume, average latency,
    active models, and drift status.
    """
    total_preds = MLPredictionLog.objects.count()
    success_preds = MLPredictionLog.objects.filter(status=MLPredictionLog.Status.SUCCESS).count()

    # Calculate average latency from last 100 predictions
    recent_logs = list(MLPredictionLog.objects.all()[:100])
    avg_latency = (
        round(sum(l.latency_ms for l in recent_logs) / len(recent_logs), 2)
        if recent_logs else 0.0
    )

    # Active model registry summary
    models_dict = ModelRegistry.get_all_models()
    active_models_count = sum(1 for m in models_dict.values() if m.get('is_active'))

    # Recent drift alerts
    drift_alerts = list(ModelDriftRecord.objects.filter(is_drift_detected=True)[:5].values(
        'model_name', 'metric_name', 'drift_score', 'detected_at'
    ))

    # Recent feedback submissions
    feedback_count = ModelFeedback.objects.count()

    return JsonResponse({
        'success': True,
        'total_predictions': total_preds,
        'success_rate_pct': round((success_preds / max(total_preds, 1)) * 100.0, 1),
        'average_latency_ms': avg_latency,
        'active_models_count': active_models_count,
        'feedback_records_count': feedback_count,
        'drift_alerts': drift_alerts,
        'data_mode': getattr(settings, 'DATA_MODE', 'DEMO'),
        'timestamp': timezone.now().isoformat()
    })
