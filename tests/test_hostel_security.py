from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ValidationError
from apps.accounts.models import User
from apps.students.models import Student
from apps.departments.models import Department
from apps.hostel.models import (
    Hostel, HostelBlock, HostelRoom, HostelFacility,
    HostelMessMenu, HostelAnnouncement
)
from apps.ai_assistant.assistant import CampusAIAssistant

class HostelSecurityRBACPlatformTests(TestCase):
    """
    Automated test suite verifying the strict role-based access control,
    gender segregation, Day Scholar/Faculty isolation, and onboarding flows for CIT Hostel Facility Module.
    """

    def setUp(self):
        self.client = Client()

        # Department
        self.dept = Department.objects.create(name="Computer Science & Engineering", code="CSE")

        # 1. Hostels Setup (4 Dedicated Buildings)
        self.bh1 = Hostel.objects.create(
            name="Boys Hostel 1",
            code="BH-1",
            category=Hostel.Category.BOYS,
            latitude=11.0253,
            longitude=77.0268,
            capacity=450,
            warden_name="Dr. K. Senthil Kumar",
            warden_contact="+91 94431 82910"
        )
        self.bh2 = Hostel.objects.create(
            name="Boys Hostel 2",
            code="BH-2",
            category=Hostel.Category.BOYS,
            latitude=11.0248,
            longitude=77.0270,
            capacity=400,
            warden_name="Dr. R. Balasubramanian",
            warden_contact="+91 94432 71829"
        )
        self.gh1 = Hostel.objects.create(
            name="Girls Hostel 1",
            code="GH-1",
            category=Hostel.Category.GIRLS,
            latitude=11.0252,
            longitude=77.0280,
            capacity=420,
            warden_name="Dr. M. Vijayalakshmi",
            warden_contact="+91 94433 62738"
        )
        self.gh2 = Hostel.objects.create(
            name="Girls Hostel 2",
            code="GH-2",
            category=Hostel.Category.GIRLS,
            latitude=11.0247,
            longitude=77.0283,
            capacity=380,
            warden_name="Dr. S. Radha",
            warden_contact="+91 94434 51647"
        )

        # 2. Super Admin User
        self.admin_user = User.objects.create_user(
            username='super_admin_test',
            email='admin@cit.edu.in',
            password='Password123!',
            role=User.Role.SUPER_ADMIN
        )

        # 3. Faculty User (Must NEVER have hostel access or onboarding questions)
        self.faculty_user = User.objects.create_user(
            username='faculty_test',
            email='faculty@cit.edu.in',
            password='Password123!',
            role=User.Role.FACULTY
        )

        # 4. Day Scholar Student (Strictly Blocked from Hostel)
        self.day_scholar_user = User.objects.create_user(
            username='dayscholar_test',
            email='dayscholar@cit.edu.in',
            password='Password123!',
            role=User.Role.STUDENT
        )
        self.day_scholar = Student.objects.create(
            user=self.day_scholar_user,
            student_id="STU-DS-01",
            first_name="Day",
            last_name="Scholar",
            department=self.dept,
            accommodation_type=Student.AccommodationType.DAY_SCHOLAR,
            hostel_category=None,
            assigned_hostel=None,
            is_accommodation_configured=True
        )

        # 5. Boys Hostel Student
        self.boys_hostel_user = User.objects.create_user(
            username='boys_student_test',
            email='boys_student@cit.edu.in',
            password='Password123!',
            role=User.Role.STUDENT
        )
        self.boys_student = Student.objects.create(
            user=self.boys_hostel_user,
            student_id="STU-BH-01",
            first_name="Boys",
            last_name="Resident",
            department=self.dept,
            accommodation_type=Student.AccommodationType.HOSTEL,
            hostel_category=Student.HostelCategory.BOYS,
            assigned_hostel=self.bh1,
            room_number="A-204",
            is_accommodation_configured=True
        )

        # 6. Girls Hostel Student
        self.girls_hostel_user = User.objects.create_user(
            username='girls_student_test',
            email='girls_student@cit.edu.in',
            password='Password123!',
            role=User.Role.STUDENT
        )
        self.girls_student = Student.objects.create(
            user=self.girls_hostel_user,
            student_id="STU-GH-01",
            first_name="Girls",
            last_name="Resident",
            department=self.dept,
            accommodation_type=Student.AccommodationType.HOSTEL,
            hostel_category=Student.HostelCategory.GIRLS,
            assigned_hostel=self.gh1,
            room_number="B-102",
            is_accommodation_configured=True
        )

    # 1. Day Scholar Student cannot access hostel dashboard -> 403 Forbidden
    def test_01_day_scholar_denied_hostel_dashboard(self):
        self.client.login(username='dayscholar_test', password='Password123!')
        response = self.client.get(reverse('hostel:dashboard'))
        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "Hostel Access Restricted", status_code=403)

    # 2. Day Scholar Student cannot access hostel rooms view -> 403 Forbidden
    def test_02_day_scholar_denied_hostel_rooms(self):
        self.client.login(username='dayscholar_test', password='Password123!')
        response = self.client.get(reverse('hostel:rooms'))
        self.assertEqual(response.status_code, 403)

    # 3. Day Scholar Student cannot access hostel facilities view -> 403 Forbidden
    def test_03_day_scholar_denied_hostel_facilities(self):
        self.client.login(username='dayscholar_test', password='Password123!')
        response = self.client.get(reverse('hostel:facilities'))
        self.assertEqual(response.status_code, 403)

    # 4. Day Scholar Student cannot access hostel mess menu -> 403 Forbidden
    def test_04_day_scholar_denied_hostel_mess(self):
        self.client.login(username='dayscholar_test', password='Password123!')
        response = self.client.get(reverse('hostel:mess'))
        self.assertEqual(response.status_code, 403)

    # 5. Day Scholar Student cannot access hostel complaints -> 403 Forbidden
    def test_05_day_scholar_denied_hostel_complaints(self):
        self.client.login(username='dayscholar_test', password='Password123!')
        response = self.client.get(reverse('hostel:complaints'))
        self.assertEqual(response.status_code, 403)

    # 6. Day Scholar Student cannot access hostel maintenance requests -> 403 Forbidden
    def test_06_day_scholar_denied_hostel_maintenance(self):
        self.client.login(username='dayscholar_test', password='Password123!')
        response = self.client.get(reverse('hostel:maintenance'))
        self.assertEqual(response.status_code, 403)

    # 7. Day Scholar Student cannot access hostel routes -> 403 Forbidden
    def test_07_day_scholar_denied_hostel_routes(self):
        self.client.login(username='dayscholar_test', password='Password123!')
        for endpoint in ['hostel:route', 'hostel:routes']:
            response = self.client.get(reverse(endpoint))
            self.assertEqual(response.status_code, 403)

    # 8. Faculty user cannot access hostel dashboard or views -> 403 Forbidden
    def test_08_faculty_denied_hostel_access(self):
        self.client.login(username='faculty_test', password='Password123!')
        for endpoint in ['hostel:dashboard', 'hostel:rooms', 'hostel:facilities', 'hostel:mess', 'hostel:complaints', 'hostel:maintenance', 'hostel:route', 'hostel:routes', 'hostel:emergency']:
            response = self.client.get(reverse(endpoint))
            self.assertEqual(response.status_code, 403)

    # 9. Unauthenticated user redirected or denied -> 302 or 403
    def test_09_unauthenticated_user_blocked(self):
        response = self.client.get(reverse('hostel:dashboard'))
        self.assertIn(response.status_code, [302, 403])

    # 10. Boys Hostel student cannot access Girls Hostel details or API -> 403 Forbidden
    def test_10_boys_hostel_student_denied_girls_hostel_api(self):
        self.client.login(username='boys_student_test', password='Password123!')
        response = self.client.get(reverse('hostel:api_details', args=[self.gh1.code]))
        self.assertEqual(response.status_code, 403)

    # 11. Girls Hostel student cannot access Boys Hostel details or API -> 403 Forbidden
    def test_11_girls_hostel_student_denied_boys_hostel_api(self):
        self.client.login(username='girls_student_test', password='Password123!')
        response = self.client.get(reverse('hostel:api_details', args=[self.bh1.code]))
        self.assertEqual(response.status_code, 403)

    # 12. Authorized Hostel student CAN access their assigned hostel dashboard -> 200 OK
    def test_12_authorized_hostel_student_allowed(self):
        self.client.login(username='boys_student_test', password='Password123!')
        dash_resp = self.client.get(reverse('hostel:dashboard'))
        self.assertEqual(dash_resp.status_code, 200)
        self.assertContains(dash_resp, "Boys Hostel 1")

        for endpoint in ['hostel:rooms', 'hostel:facilities', 'hostel:mess', 'hostel:complaints', 'hostel:maintenance', 'hostel:events', 'hostel:emergency', 'hostel:route', 'hostel:routes']:
            response = self.client.get(reverse(endpoint))
            self.assertEqual(response.status_code, 200)

        # Can also access their own hostel API
        api_resp = self.client.get(reverse('hostel:api_details', args=[self.bh1.code]))
        self.assertEqual(api_resp.status_code, 200)
        self.assertEqual(api_resp.json()['code'], 'BH-1')

    # 13. Admin/Superuser CAN access all hostel views and admin analytics -> 200 OK
    def test_13_admin_allowed_all_views_and_analytics(self):
        self.client.login(username='super_admin_test', password='Password123!')
        dash_resp = self.client.get(reverse('hostel:dashboard'))
        self.assertEqual(dash_resp.status_code, 200)

        analytics_resp = self.client.get(reverse('hostel:admin_analytics'))
        self.assertEqual(analytics_resp.status_code, 200)
        self.assertContains(analytics_resp, "Hostel Facilities Command Center")

        # Admin can access any hostel API
        bh_api = self.client.get(reverse('hostel:api_details', args=[self.bh1.code]))
        self.assertEqual(bh_api.status_code, 200)
        gh_api = self.client.get(reverse('hostel:api_details', args=[self.gh1.code]))
        self.assertEqual(gh_api.status_code, 200)

    # 14. Day Scholar calling /api/hostel/... APIs -> 403 Forbidden
    def test_14_day_scholar_denied_apis(self):
        self.client.login(username='dayscholar_test', password='Password123!')
        for api_url in ['/api/hostel/facilities/', '/api/hostel/rooms/', '/api/hostel/routes/']:
            resp = self.client.get(api_url)
            self.assertEqual(resp.status_code, 403)
            self.assertIn("Hostel facilities are available only to authorized hostel students", resp.json().get('detail', ''))

    # 15. Faculty calling /api/hostel/... APIs -> 403 Forbidden
    def test_15_faculty_denied_apis(self):
        self.client.login(username='faculty_test', password='Password123!')
        for api_url in ['/api/hostel/facilities/', '/api/hostel/rooms/', '/api/hostel/routes/']:
            resp = self.client.get(api_url)
            self.assertEqual(resp.status_code, 403)
            self.assertIn("Hostel facilities are restricted to authorized hostel students", resp.json().get('detail', ''))

    # 16. Data Validation: Mismatched gender category and hostel raises ValidationError
    def test_16_mismatched_hostel_category_validation(self):
        stu = Student(
            student_id="STU-VAL-01",
            first_name="Test",
            department=self.dept,
            accommodation_type=Student.AccommodationType.HOSTEL,
            hostel_category=Student.HostelCategory.BOYS,
            assigned_hostel=self.gh1  # Mismatch: Girls hostel assigned to Boys category
        )
        with self.assertRaises(ValidationError):
            stu.clean()

    # 17. AI Assistant Strict Role-Based Hostel Intelligence
    def test_17_ai_assistant_hostel_security_filtering(self):
        # Day scholar asking about hostel
        ds_answer = CampusAIAssistant.answer_query("Where is my hostel?", self.day_scholar_user)
        self.assertIn("Hostel facilities are available only to authorized hostel students", ds_answer)

        # Faculty asking about hostel
        fac_answer = CampusAIAssistant.answer_query("Where is my hostel?", self.faculty_user)
        self.assertIn("Hostel facilities are restricted to authorized hostel students", fac_answer)

        # Resident asking where is my hostel
        resident_answer = CampusAIAssistant.answer_query("Where is my hostel?", self.boys_hostel_user)
        self.assertIn("Boys Hostel 1 (BH-1)", resident_answer)
        self.assertIn("A-204", resident_answer)

        # Resident asking how to reach my hostel
        route_answer = CampusAIAssistant.answer_query("How do I reach my hostel?", self.boys_hostel_user)
        self.assertIn("Route to Boys Hostel 1 (BH-1)", route_answer)

        # Resident asking for facilities
        fac_query_answer = CampusAIAssistant.answer_query("What facilities are available in my hostel?", self.boys_hostel_user)
        self.assertIn("Authorized Facilities in Boys Hostel 1 (BH-1)", fac_query_answer)

    # 18. Student Login & Onboarding Flow Separation
    def test_18_student_onboarding_and_faculty_isolation(self):
        # New student without accommodation setup
        new_stu_user = User.objects.create_user(
            username='new_student',
            password='Password123!',
            role=User.Role.STUDENT
        )
        Student.objects.create(
            user=new_stu_user,
            student_id="STU-NEW-01",
            first_name="New",
            department=self.dept,
            is_accommodation_configured=False
        )
        self.client.login(username='new_student', password='Password123!')
        resp = self.client.get(reverse('accounts:role_redirect'))
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, reverse('accounts:accommodation_setup'))

        # Faculty user logs in -> NEVER redirected to accommodation setup
        self.client.login(username='faculty_test', password='Password123!')
        fac_resp = self.client.get(reverse('accounts:role_redirect'))
        self.assertEqual(fac_resp.status_code, 302)
        self.assertEqual(fac_resp.url, reverse('faculty:dashboard'))

        # Faculty tries to access accommodation setup directly -> redirected to faculty dashboard
        fac_accom_resp = self.client.get(reverse('accounts:accommodation_setup'))
        self.assertEqual(fac_accom_resp.status_code, 302)
        self.assertEqual(fac_accom_resp.url, reverse('faculty:dashboard'))
