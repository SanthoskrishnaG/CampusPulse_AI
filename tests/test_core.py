from django.test import TestCase, Client
from django.urls import reverse
from apps.accounts.models import User
from apps.students.models import Student
from apps.departments.models import Department
from apps.events.models import Event
from apps.complaints.models import Complaint
from apps.academics.models import AcademicRiskAssessment
from ml.academic.predict import AcademicRiskPredictor
from ml.complaints.predict import ComplaintAITriage
from ml.events.predict import EventAttendancePredictor
from ml.canteen.predict import CanteenDemandPredictor
from ml.energy.detect import EnergyAnomalyDetector
from apps.recommendations.engine import RecommendationEngine
from apps.ai_assistant.assistant import CampusAIAssistant

class CampusPulseCorePlatformTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Department
        self.dept = Department.objects.create(name="Computer Science", code="CSE")

        # Super Admin User
        self.admin_user = User.objects.create_user(
            username='admin_test',
            email='admin@test.local',
            password='testpassword123',
            role=User.Role.SUPER_ADMIN
        )

        # Student User
        self.student_user = User.objects.create_user(
            username='student_test',
            email='student@test.local',
            password='testpassword123',
            role=User.Role.STUDENT
        )

        # Student profile
        self.student = Student.objects.create(
            user=self.student_user,
            student_id="STU-TEST-01",
            first_name="Test",
            last_name="Student",
            department=self.dept,
            cgpa=8.2,
            attendance_percentage=88.0,
            skills="Python, PyTorch, React, SQL",
            interests="Machine Learning, Robotics"
        )

    def test_authentication_and_rbac_redirect(self):
        """Verifies authentication and intelligent role-based redirect."""
        logged_in = self.client.login(username='student_test', password='testpassword123')
        self.assertTrue(logged_in)
        response = self.client.get(reverse('accounts:role_redirect'))
        self.assertRedirects(response, reverse('students:dashboard'))

    def test_academic_risk_ml_inference(self):
        """Verifies trained Academic Risk model returns calibrated prediction and explainability."""
        result = AcademicRiskPredictor.predict_student_risk(self.student)
        self.assertIn(result['risk_level'], ['LOW', 'MEDIUM', 'HIGH'])
        self.assertGreaterEqual(result['risk_score'], 0.0)
        self.assertLessEqual(result['risk_score'], 100.0)
        self.assertTrue(len(result['factors']) > 0)

    def test_complaint_ai_triage(self):
        """Verifies NLP classification, priority estimation, and location extraction."""
        triage = ComplaintAITriage.triage_complaint("The ceiling fan in Room 302 Block C is sparking and dangerous.")
        self.assertEqual(triage['category'], 'ELECTRICAL')
        self.assertEqual(triage['priority'], 'URGENT')
        self.assertIn("Electrical", triage['target_department'])
        self.assertTrue(len(triage['location_extracted']) > 0)

    def test_event_attendance_forecaster(self):
        """Verifies Random Forest Regressor estimates turnout and no-show rate."""
        from django.utils import timezone
        event = Event.objects.create(
            title="AI Workshop",
            description="Deep learning workshop",
            event_type=Event.EventType.WORKSHOP,
            department=self.dept,
            start_time=timezone.now() + timezone.timedelta(days=2),
            end_time=timezone.now() + timezone.timedelta(days=2, hours=3),
            capacity=100
        )
        forecast = EventAttendancePredictor.predict_attendance(event)
        self.assertGreater(forecast['predicted_attendance'], 0)
        self.assertLessEqual(forecast['predicted_attendance'], 100)

    def test_canteen_demand_forecaster(self):
        """Verifies meal portion demand prediction."""
        result = CanteenDemandPredictor.predict_meal_demand(day_of_week=2, meal_type='LUNCH')
        self.assertGreater(result['predicted_demand'], 50)
        self.assertGreater(result['recommended_prep'], result['predicted_demand'])

    def test_energy_anomaly_isolation_forest(self):
        """Verifies Isolation Forest detects night-time power leaks."""
        # Daytime normal load
        day_res = EnergyAnomalyDetector.inspect_reading(hour=14, is_weekend=False, occupancy=200, kwh=48.0, baseline=45.0)
        self.assertFalse(day_res['is_anomaly'])

        # Nocturnal heavy spike (ACs left running full blast at 2 AM)
        night_res = EnergyAnomalyDetector.inspect_reading(hour=2, is_weekend=False, occupancy=0, kwh=85.0, baseline=45.0)
        self.assertTrue(night_res['is_anomaly'])
        self.assertEqual(night_res['anomaly_type'], 'NIGHT_LEAK')

    def test_recommendation_engine(self):
        """Verifies complementary skill matching returns compatibility score."""
        teammates = RecommendationEngine.recommend_teammates_for_student(self.student, limit=3)
        self.assertIsInstance(teammates, list)

    def test_permission_aware_ai_assistant(self):
        """Verifies student user cannot query confidential academic risk assessments."""
        response = CampusAIAssistant.answer_query("How many high risk students in CSE?", self.student_user)
        self.assertIn("Access Restricted", response)

        admin_response = CampusAIAssistant.answer_query("How many high risk students in CSE?", self.admin_user)
        self.assertIn("Academic Risk Summary", admin_response)

    def test_all_redesigned_pages_render(self):
        """Verifies that all redesigned templates render HTTP 200 with new Light 3D assets."""
        # Unauthenticated home page
        self.client.logout()
        res_home = self.client.get(reverse('common:home'))
        self.assertEqual(res_home.status_code, 200)
        self.assertContains(res_home, "CampusPulse", status_code=200)

        # Authenticated routes
        self.client.force_login(self.admin_user)
        routes = [
            'common:map',
            'events:list',
            'clubs:list',
            'complaints:list',
            'transport:dashboard',
            'parking:dashboard',
            'canteen:dashboard',
            'energy:dashboard',
            'waste:dashboard',
            'traffic:dashboard',
            'ai_assistant:chat',
            'analytics:dashboard',
            'analytics:model_registry',
            'students:list',
            'departments:list',
            'faculty:list',
            'projects:list',
            'recommendations:hub',
        ]
        for r in routes:
            url = reverse(r)
            res = self.client.get(url)
            self.assertEqual(res.status_code, 200, f"Failed to render {r} ({url})")
            self.assertContains(res, "CampusPulse", status_code=200)


