import json
from django.test import TestCase, Client
from django.utils import timezone
from apps.accounts.models import User
from apps.departments.models import Department
from apps.students.models import Student
from apps.transport.models import Bus, BusRoute, BusStop
from apps.parking.models import ParkingLot
from apps.analytics.models import MLModelRecord, MLPredictionLog, MLTrainingRun, ModelFeedback
from ml.utils.validation import (
    validate_academic_features,
    validate_canteen_features,
    validate_food_waste_features,
    validate_complaint_text,
    validate_energy_features,
    validate_transport_features,
    validate_parking_features
)
from ml.utils.drift import calculate_psi, interpret_psi
from ml.academic.predict import AcademicRiskPredictor
from ml.canteen.predict import CanteenDemandPredictor
from ml.canteen.waste_predict import FoodWastePredictor
from ml.hostel.mess_forecaster import HostelMessDemandForecaster
from ml.complaints.predict import ComplaintAITriage
from ml.complaints.duplicate import DuplicateComplaintDetector
from ml.energy.detect import EnergyAnomalyDetector
from ml.transport.predict import TransportETAPredictor
from ml.parking.predict import ParkingOccupancyPredictor
from apps.recommendations.engine import RecommendationEngine

class MLPipelineValidationTestCase(TestCase):
    """
    Tests input validation and defensive bounds checking across all ML domains.
    """

    def test_academic_validation_valid_and_invalid(self):
        valid = {
            'attendance_percentage': 82.5,
            'cgpa': 7.8,
            'internal_marks': 74.0,
            'backlog_count': 0,
            'semester': 6,
            'quiz_avg': 80.0,
            'assignment_avg': 85.0,
            'lms_hours_avg': 5.2,
            'trend_slope': 0.1
        }
        res = validate_academic_features(valid)
        self.assertEqual(res['attendance_percentage'], 82.5)

        # Missing field
        invalid_missing = valid.copy()
        del invalid_missing['attendance_percentage']
        with self.assertRaises(ValueError):
            validate_academic_features(invalid_missing)

        # Impossible attendance value (>100)
        invalid_att = valid.copy()
        invalid_att['attendance_percentage'] = 145.0
        with self.assertRaises(ValueError):
            validate_academic_features(invalid_att)

        # Negative backlogs
        invalid_backlogs = valid.copy()
        invalid_backlogs['backlog_count'] = -2
        with self.assertRaises(ValueError):
            validate_academic_features(invalid_backlogs)

    def test_canteen_validation(self):
        valid = {
            'day_of_week': 2,
            'meal_type': 'LUNCH',
            'is_event': 0,
            'is_weekend': 0,
            'student_base': 520
        }
        res = validate_canteen_features(valid)
        self.assertEqual(res['meal_type'], 'LUNCH')

        # Invalid meal type
        invalid = valid.copy()
        invalid['meal_type'] = 'MIDNIGHT_FEAST'
        with self.assertRaises(ValueError):
            validate_canteen_features(invalid)

    def test_complaint_text_validation(self):
        self.assertEqual(validate_complaint_text("Power cut in lab 3"), "Power cut in lab 3")
        with self.assertRaises(ValueError):
            validate_complaint_text("hi")
        with self.assertRaises(ValueError):
            validate_complaint_text("")

    def test_psi_drift_calculation(self):
        baseline = [10.0, 10.2, 9.8, 10.5, 10.1, 9.9, 10.3, 10.0, 10.1, 9.7] * 5
        # Identical distribution -> PSI should be ~0.0
        psi_zero = calculate_psi(baseline, baseline)
        self.assertLess(psi_zero, 0.05)

        # Shifted distribution
        shifted = [25.0, 26.0, 24.5, 27.0, 25.5, 26.2, 28.0, 25.1, 26.9, 25.4] * 5
        psi_high = calculate_psi(baseline, shifted)
        self.assertGreater(psi_high, 0.25)
        interpretation = interpret_psi(psi_high)
        self.assertTrue(interpretation['alert'])


class MLEndToEndInferenceTestCase(TestCase):
    """
    Tests live end-to-end model inference, prediction formatting, and database persistence.
    """

    def setUp(self):
        self.client = Client()
        self.dept = Department.objects.create(name="Computer Science", code="CSE")
        self.user = User.objects.create_user(username="teststu", password="password123", role=User.Role.STUDENT)
        self.student = Student.objects.create(
            user=self.user,
            student_id="CIT-STU-099",
            first_name="Siddharth",
            last_name="Kumar",
            department=self.dept,
            semester=6,
            attendance_percentage=62.0,
            cgpa=5.8,
            backlog_count=1
        )

        self.other_user = User.objects.create_user(username="otherstu", password="password123", role=User.Role.STUDENT)
        self.other_student = Student.objects.create(
            user=self.other_user,
            student_id="CIT-STU-100",
            first_name="Rithika",
            last_name="Sundar",
            department=self.dept,
            semester=6,
            attendance_percentage=94.0,
            cgpa=8.9,
            backlog_count=0
        )

        self.faculty_user = User.objects.create_user(username="testfac", password="password123", role=User.Role.FACULTY)

    def test_academic_risk_real_inference_and_logging(self):
        # Student with low attendance (62%) and low CGPA (5.8)
        res = AcademicRiskPredictor.predict_student_risk(self.student)
        self.assertTrue(res['success'])
        self.assertIn(res['risk_level'], ['MEDIUM', 'HIGH'])
        self.assertGreater(res['risk_score'], 30.0)
        self.assertIsNotNone(res['confidence'])
        self.assertGreater(len(res['factors']), 0)

        # Check that inference was logged into MLPredictionLog
        logged = MLPredictionLog.objects.filter(model_name="Academic_Risk_Classifier").first()
        self.assertIsNotNone(logged)
        self.assertEqual(logged.status, MLPredictionLog.Status.SUCCESS)

    def test_canteen_demand_and_waste_inference(self):
        res_demand = CanteenDemandPredictor.predict_meal_demand(day_of_week=2, meal_type='LUNCH')
        self.assertTrue(res_demand['success'])
        self.assertGreater(res_demand['predicted_demand'], 50)
        self.assertGreater(res_demand['recommended_prep'], res_demand['predicted_demand'])

        res_waste = FoodWastePredictor.predict_waste(
            meals_prepared=res_demand['recommended_prep'],
            predicted_demand=res_demand['predicted_demand'],
            meal_type='LUNCH',
            day_of_week=2
        )
        self.assertTrue(res_waste['success'])
        self.assertGreater(res_waste['predicted_waste_kg'], 0.0)

    def test_complaint_nlp_classification_and_duplicate_check(self):
        triage = ComplaintAITriage.triage_complaint("Severe water leakage from laboratory tap in Block C")
        self.assertTrue(triage['success'])
        self.assertEqual(triage['category'], 'WATER')
        self.assertIn('Plumbing', triage['target_department'])
        self.assertIsNotNone(triage['confidence'])

        dup = DuplicateComplaintDetector.check_duplicate("Severe water leak in lab tap Block C", category='WATER')
        self.assertIn('is_duplicate', dup)
        self.assertIn('similarity_score', dup)

    def test_energy_anomaly_detection(self):
        # Normal daytime reading
        norm = EnergyAnomalyDetector.inspect_reading(hour=11, is_weekend=False, occupancy=100, kwh=42.0)
        self.assertTrue(norm['success'])

        # Nighttime spike (85 kWh at 2 AM)
        spike = EnergyAnomalyDetector.inspect_reading(hour=2, is_weekend=False, occupancy=2, kwh=85.0)
        self.assertTrue(spike['success'])
        self.assertTrue(spike['is_anomaly'])
        self.assertEqual(spike['anomaly_type'], 'NIGHT_LEAK')

    def test_deterministic_recommendations_no_randomness(self):
        # Two consecutive runs with identical inputs must produce identical outputs
        run1 = RecommendationEngine.recommend_career_paths(self.student)
        run2 = RecommendationEngine.recommend_career_paths(self.student)
        self.assertEqual(len(run1), len(run2))
        self.assertEqual(run1[0]['fit_score'], run2[0]['fit_score'])
        self.assertEqual(run1[0]['title'], run2[0]['title'])


class MLRESTEndpointsTestCase(TestCase):
    """
    Tests REST APIs under /api/ml/* including authorization boundaries.
    """

    def setUp(self):
        self.client = Client()
        self.dept = Department.objects.create(name="Information Technology", code="IT")
        self.student_user = User.objects.create_user(username="stu1", password="password123", role=User.Role.STUDENT)
        self.student = Student.objects.create(
            user=self.student_user,
            student_id="CIT-IT-001",
            first_name="Ananya",
            last_name="Rao",
            department=self.dept,
            attendance_percentage=88.0,
            cgpa=8.2
        )

        self.attacker_user = User.objects.create_user(username="stu2", password="password123", role=User.Role.STUDENT)
        self.attacker_student = Student.objects.create(
            user=self.attacker_user,
            student_id="CIT-IT-002",
            first_name="Rohan",
            last_name="Varma",
            department=self.dept,
            attendance_percentage=71.0,
            cgpa=6.4
        )

        self.route = BusRoute.objects.create(code="R-01", name="Express Corridor", distance_km=14.0)
        self.bus = Bus.objects.create(bus_number="TN-38-CIT-9901", route=self.route, capacity=52, current_passengers=30)
        self.lot = ParkingLot.objects.create(code="PKG-CENTRAL", name="Central Bay", total_slots=80)

    def test_academic_risk_own_record_success(self):
        self.client.force_login(self.student_user)
        res = self.client.post('/api/ml/academic-risk/predict/', json.dumps({}), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['student_id'], 'CIT-IT-001')

    def test_academic_risk_cross_student_blocked(self):
        self.client.force_login(self.attacker_user)
        # Attempting to query student 1's profile
        res = self.client.post('/api/ml/academic-risk/predict/', json.dumps({'student_id': 'CIT-IT-001'}), content_type='application/json')
        self.assertEqual(res.status_code, 403)
        self.assertFalse(res.json()['success'])

    def test_canteen_and_waste_apis(self):
        self.client.force_login(self.student_user)
        res = self.client.get('/api/ml/canteen/demand/?meal_type=LUNCH')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json()['success'])

        res_waste = self.client.post(
            '/api/ml/canteen/waste/predict/',
            json.dumps({'meals_prepared': 400, 'predicted_demand': 370, 'meal_type': 'LUNCH'}),
            content_type='application/json'
        )
        self.assertEqual(res_waste.status_code, 200)
        self.assertTrue(res_waste.json()['success'])

    def test_transport_and_parking_apis(self):
        res_bus = self.client.get(f'/api/ml/transport/eta/{self.bus.id}/')
        self.assertEqual(res_bus.status_code, 200)
        self.assertTrue(res_bus.json()['success'])

        res_pkg = self.client.get(f'/api/ml/parking/predict/{self.lot.code}/')
        self.assertEqual(res_pkg.status_code, 200)
        self.assertTrue(res_pkg.json()['success'])

    def test_feedback_submission_and_monitoring_metrics(self):
        self.client.force_login(self.student_user)
        fb_res = self.client.post(
            '/api/ml/feedback/submit/',
            json.dumps({'model_name': 'Canteen_Food_Demand_Forecaster', 'actual_outcome': '365', 'notes': 'POS lunch count'}),
            content_type='application/json'
        )
        self.assertEqual(fb_res.status_code, 200)
        self.assertTrue(fb_res.json()['success'])

        met_res = self.client.get('/api/ml/monitoring/metrics/')
        self.assertEqual(met_res.status_code, 200)
        self.assertTrue(met_res.json()['success'])
        self.assertGreater(met_res.json()['active_models_count'], 0)
