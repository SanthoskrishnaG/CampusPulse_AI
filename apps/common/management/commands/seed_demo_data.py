import random
import uuid
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction

from apps.accounts.models import User
from apps.common.models import CampusLocation, WeatherCache
from apps.departments.models import Department, DepartmentAnnouncement, DepartmentResource
from apps.faculty.models import Faculty
from apps.students.models import Student
from apps.academics.models import Course, CourseOffering, Enrollment, WeeklyPerformanceRecord, AcademicRiskAssessment, AcademicIntervention
from apps.clubs.models import Club, ClubMembership, ClubAnnouncement, ClubAchievement
from apps.events.models import Event, EventRegistration, EventFeedback, Certificate
from apps.projects.models import Project, Team, TeamMember
from apps.complaints.models import Complaint, ComplaintStatusHistory
from apps.transport.models import BusRoute, Bus, BusStop
from apps.parking.models import ParkingLot, ParkingSlot
from apps.canteen.models import Canteen, MenuItem, MealRecord
from apps.energy.models import EnergyMeter, EnergyReading, EnergyAnomaly
from apps.waste.models import WasteRecord, WasteImagePrediction
from apps.notifications.models import Notification
from ml.complaints.predict import ComplaintAITriage
from ml.academic.predict import AcademicRiskPredictor

class Command(BaseCommand):
    help = 'Seeds a realistic campus environment with 500+ students, 50+ faculty, 20+ clubs, 100+ events, 500+ complaints, and smart operations.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Initializing CampusPulse AI Complete Campus Seeding Engine..."))

        with transaction.atomic():
            self.seed_rbac_users()
            departments = self.seed_departments()
            self.seed_locations()
            faculty_list = self.seed_faculty(departments)
            courses = self.seed_courses(departments, faculty_list)
            students = self.seed_students(departments)
            self.seed_academics(students, courses)
            clubs = self.seed_clubs(departments, faculty_list, students)
            self.seed_events(departments, clubs, students)
            self.seed_projects(departments, students, faculty_list)
            self.seed_complaints(students)
            self.seed_transport()
            self.seed_parking()
            self.seed_canteen()
            self.seed_energy()
            self.seed_waste()

        # Run ML risk inference outside transaction to persist assessments
        self.stdout.write("Running baseline ML risk assessments across students...")
        AcademicRiskPredictor.batch_assess_all_students()

        self.stdout.write(self.style.SUCCESS("\n[SUCCESS] CampusPulse AI populated with complete, production-grade demonstration data!"))

    def seed_rbac_users(self):
        self.stdout.write("-> Creating 12 RBAC demo accounts (password: admin123)...")
        demo_accounts = [
            ('superadmin', 'superadmin@campuspulse.local', User.Role.SUPER_ADMIN, 'Santhosh', 'Krishna'),
            ('collegeadmin', 'admin@campuspulse.local', User.Role.COLLEGE_ADMIN, 'Arun', 'Kumar'),
            ('deptadmin', 'deptadmin@campuspulse.local', User.Role.DEPARTMENT_ADMIN, 'Dr. Rajesh', 'Sharma'),
            ('faculty', 'faculty@campuspulse.local', User.Role.FACULTY, 'Dr. Priya', 'Sundaram'),
            ('student', 'student@campuspulse.local', User.Role.STUDENT, 'Aarav', 'Patel'),
            ('clubadmin', 'club@campuspulse.local', User.Role.CLUB_ADMIN, 'Kiran', 'Deshmukh'),
            ('clubmember', 'member@campuspulse.local', User.Role.CLUB_MEMBER, 'Sneha', 'Reddy'),
            ('transportmgr', 'transport@campuspulse.local', User.Role.TRANSPORT_MANAGER, 'Gopal', 'Menon'),
            ('canteenmgr', 'canteen@campuspulse.local', User.Role.CANTEEN_MANAGER, 'Manoj', 'Venkatesh'),
            ('maintenance', 'maintenance@campuspulse.local', User.Role.MAINTENANCE_STAFF, 'Ramesh', 'Yadav'),
            ('facilitymgr', 'facility@campuspulse.local', User.Role.FACILITY_MANAGER, 'Suresh', 'Babu'),
            ('security', 'security@campuspulse.local', User.Role.SECURITY_STAFF, 'Balaji', 'Singh'),
        ]

        for username, email, role, first, last in demo_accounts:
            u, created = User.objects.get_or_create(
                username=username,
                defaults={'email': email, 'role': role, 'first_name': first, 'last_name': last}
            )
            u.set_password('admin123')
            if role == User.Role.SUPER_ADMIN:
                u.is_staff = True
                u.is_superuser = True
            u.save()

    def seed_departments(self):
        self.stdout.write("-> Creating 7 Academic Departments...")
        dept_data = [
            ('Computer Science & Engineering', 'CSE', 'Dr. Rajesh Sharma', 'cse@campuspulse.local', 'Alan Turing Block', 2001),
            ('Information Technology', 'IT', 'Dr. Meenakshi Sundaram', 'it@campuspulse.local', 'Ada Lovelace Tower', 2004),
            ('Electronics & Communication', 'ECE', 'Dr. K. S. Raman', 'ece@campuspulse.local', 'Maxwell Hall', 2000),
            ('Electrical & Electronics', 'EEE', 'Dr. Ananya Bose', 'eee@campuspulse.local', 'Tesla Complex', 2000),
            ('Mechanical Engineering', 'MECH', 'Dr. Harish Patel', 'mech@campuspulse.local', 'Newton Workshop Center', 2002),
            ('Civil Engineering', 'CIVIL', 'Dr. V. Narayanan', 'civil@campuspulse.local', 'Visvesvaraya Block', 2003),
            ('Artificial Intelligence & Data Science', 'AIDS', 'Dr. Shalini Gupta', 'aids@campuspulse.local', 'AI Innovation Center', 2021),
        ]
        departments = []
        for name, code, hod, email, building, year in dept_data:
            d, _ = Department.objects.get_or_create(
                code=code,
                defaults={'name': name, 'hod_name': hod, 'email': email, 'building': building, 'established_year': year}
            )
            # Add notices
            DepartmentAnnouncement.objects.get_or_create(
                department=d,
                title=f"Welcome to Semester V - {d.code} Academic Guidelines",
                defaults={'content': f"All {d.name} students are requested to complete laboratory registrations and elective selections before Friday."}
            )
            departments.append(d)
        return departments

    def seed_locations(self):
        self.stdout.write("-> Seeding Campus Geographic Locations...")
        locations = [
            ("Alan Turing Computing Block", "BLK-A", CampusLocation.Category.ACADEMIC_BLOCK, 12.9718, 77.5942, 5, 600),
            ("Ada Lovelace IT Complex", "BLK-B", CampusLocation.Category.ACADEMIC_BLOCK, 12.9722, 77.5948, 4, 500),
            ("Tesla & EEE Research Wing", "BLK-C", CampusLocation.Category.ACADEMIC_BLOCK, 12.9712, 77.5955, 3, 400),
            ("Central Artificial Intelligence Lab", "LAB-AI", CampusLocation.Category.LABORATORY, 12.9719, 77.5944, 2, 120),
            ("Main University Auditorium", "AUD-MAIN", CampusLocation.Category.AUDITORIUM, 12.9725, 77.5938, 1, 1200),
            ("Central Dining Hall & Canteen", "CAN-MAIN", CampusLocation.Category.CANTEEN, 12.9708, 77.5940, 2, 450),
            ("North Parking Lot", "PKG-NORTH", CampusLocation.Category.PARKING, 12.9730, 77.5945, 1, 80),
            ("East Parking Lot", "PKG-EAST", CampusLocation.Category.PARKING, 12.9715, 77.5960, 1, 70),
            ("Main Gate Bus Terminal", "STOP-GATE1", CampusLocation.Category.BUS_STOP, 12.9702, 77.5935, 1, 200),
            ("Library & Student Innovation Hub", "LIB-HUB", CampusLocation.Category.ACADEMIC_BLOCK, 12.9716, 77.5950, 4, 800),
        ]
        for name, code, cat, lat, lng, floors, cap in locations:
            CampusLocation.objects.get_or_create(
                code=code,
                defaults={'name': name, 'category': cat, 'latitude': lat, 'longitude': lng, 'floor_count': floors, 'capacity': cap}
            )

    def seed_faculty(self, departments):
        self.stdout.write("-> Seeding 50+ Faculty Members...")
        first_names = ['Rajesh', 'Priya', 'Meenakshi', 'Arun', 'Ananya', 'Harish', 'Shalini', 'Kavita', 'Sanjay', 'Deepak', 'Swati', 'Vikram', 'Ramesh', 'Sunita', 'Gautam']
        last_names = ['Sharma', 'Sundaram', 'Kumar', 'Bose', 'Patel', 'Gupta', 'Iyer', 'Menon', 'Nair', 'Verma', 'Singh', 'Reddy', 'Rao', 'Deshmukh']
        specs = ['Machine Learning & Deep Learning', 'Cloud & Distributed Systems', 'VLSI & Embedded IoT', 'Renewable Energy Grids', 'Computational Mechanics', 'Structural Modeling', 'Natural Language Processing']

        faculty_list = []
        emp_idx = 101

        # Link default faculty user
        default_fac_user = User.objects.get(username='faculty')
        fac_obj, _ = Faculty.objects.get_or_create(
            user=default_fac_user,
            defaults={
                'department': departments[0],
                'employee_id': f"FAC-{emp_idx}",
                'designation': Faculty.Designation.ASSOCIATE_PROF,
                'specialization': "Machine Learning & Explainable AI",
                'cabin_location': "Alan Turing Block 304"
            }
        )
        faculty_list.append(fac_obj)

        for i in range(52):
            emp_idx += 1
            username = f"faculty_{emp_idx}"
            dept = random.choice(departments)
            first = random.choice(first_names)
            last = random.choice(last_names)
            user, _ = User.objects.get_or_create(
                username=username,
                defaults={'email': f"{username}@campuspulse.local", 'first_name': first, 'last_name': last, 'role': User.Role.FACULTY}
            )
            user.set_password('admin123')
            user.save()

            f, _ = Faculty.objects.get_or_create(
                user=user,
                defaults={
                    'department': dept,
                    'employee_id': f"FAC-{emp_idx}",
                    'designation': random.choice([Faculty.Designation.ASSISTANT_PROF, Faculty.Designation.ASSOCIATE_PROF, Faculty.Designation.PROFESSOR]),
                    'specialization': random.choice(specs),
                    'cabin_location': f"{dept.building} Room {random.randint(201, 405)}"
                }
            )
            faculty_list.append(f)

        return faculty_list

    def seed_courses(self, departments, faculty_list):
        self.stdout.write("-> Seeding Department Courses & Offerings...")
        course_catalog = [
            ('CS501', 'Artificial Intelligence & Machine Learning', 'CSE', 4),
            ('CS502', 'Database Systems & Cloud Architectures', 'CSE', 3),
            ('CS503', 'Design and Analysis of Algorithms', 'CSE', 4),
            ('IT501', 'Web Technologies & REST Frameworks', 'IT', 3),
            ('IT502', 'Information & Network Security', 'IT', 3),
            ('EC501', 'Digital Signal Processing & Microcontrollers', 'ECE', 4),
            ('EE501', 'Smart Energy Grids & Power Systems', 'EEE', 4),
            ('ME501', 'Robotics, Kinematics & Mechatronics', 'MECH', 4),
            ('CV501', 'Structural Mechanics & Environmental Engg', 'CIVIL', 3),
            ('AI501', 'Deep Learning & Neural Computer Vision', 'AIDS', 4),
        ]
        courses = []
        for code, name, dept_code, creds in course_catalog:
            dept = next((d for d in departments if d.code == dept_code), departments[0])
            c, _ = Course.objects.get_or_create(
                code=code,
                defaults={'name': name, 'department': dept, 'credits': creds, 'semester': 5}
            )
            fac = next((f for f in faculty_list if f.department == dept), faculty_list[0])
            CourseOffering.objects.get_or_create(course=c, faculty=fac, academic_year='2025-2026', semester=5)
            courses.append(c)
        return courses

    def seed_students(self, departments):
        self.stdout.write("-> Seeding 500+ Realistic Students with Skills & Performance Metrics...")
        first_names = ['Aarav', 'Diya', 'Kavya', 'Siddharth', 'Vikram', 'Ananya', 'Rohan', 'Sneha', 'Tanvi', 'Varun', 'Neha', 'Aditya', 'Meera', 'Rahul', 'Ishaan', 'Pooja', 'Nikhil', 'Rhea', 'Karan', 'Simran']
        last_names = ['Patel', 'Nair', 'Iyer', 'Rao', 'Singh', 'Sharma', 'Verma', 'Reddy', 'Deshmukh', 'Menon', 'Gupta', 'Kumar', 'Joshi', 'Bose', 'Pillai', 'Chopra']
        
        skill_sets = [
            "Python, PyTorch, Scikit-learn, SQL",
            "JavaScript, React, Node.js, CSS, HTML5",
            "Django, Python, PostgreSQL, REST APIs, Docker",
            "Embedded C, Arduino, IoT, Circuit Design",
            "SolidWorks, ANSYS, AutoCAD, C++",
            "Data Analysis, Pandas, PowerBI, Tableau, Statistics",
            "Java, Spring Boot, Microservices, MySQL",
            "Computer Vision, OpenCV, PyTorch, Flask"
        ]

        interest_sets = [
            "Machine Learning, Robotics, Computer Vision",
            "Full Stack Web Development, Cloud Computing",
            "Cyber Security, Ethical Hacking, Networks",
            "Renewable Energy, Smart Campus IoT",
            "Autonomous Vehicles, CAD Modeling",
            "Natural Language Processing, Generative AI"
        ]

        students = []

        # Default student account
        default_stu_user = User.objects.get(username='student')
        s_obj, _ = Student.objects.get_or_create(
            student_id="STU2026-0001",
            defaults={
                'user': default_stu_user,
                'first_name': "Aarav",
                'last_name': "Patel",
                'department': departments[0],
                'program': "B.Tech",
                'semester': 5,
                'section': "A",
                'admission_year': 2023,
                'cgpa': 8.65,
                'attendance_percentage': 89.5,
                'skills': "Python, PyTorch, Django, Docker, Machine Learning",
                'interests': "Machine Learning, Computer Vision, Robotics",
                'career_interests': "AI Research Engineer",
                'backlog_count': 0
            }
        )
        students.append(s_obj)

        random.seed(42)
        for i in range(2, 520):
            sid = f"STU2026-{i:04d}"
            dept = random.choice(departments)
            first = random.choice(first_names)
            last = random.choice(last_names)
            
            # Correlated performance metrics (Realistic!)
            base_perf = random.betavariate(5, 2) # Skewed towards 7-9 CGPA
            cgpa = round(3.5 + base_perf * 6.4, 2)
            attendance = round(np_clip_val(cgpa * 9.2 + random.normalvariate(5, 7), 42.0, 99.0), 1)
            backlogs = 0 if cgpa >= 6.5 else random.choice([1, 2, 3])

            s, _ = Student.objects.get_or_create(
                student_id=sid,
                defaults={
                    'first_name': first,
                    'last_name': last,
                    'department': dept,
                    'program': "B.Tech",
                    'semester': random.choice([3, 5, 7]),
                    'section': random.choice(['A', 'B', 'C']),
                    'admission_year': 2023,
                    'cgpa': cgpa,
                    'attendance_percentage': attendance,
                    'skills': random.choice(skill_sets),
                    'interests': random.choice(interest_sets),
                    'career_interests': "Software Engineer",
                    'backlog_count': backlogs
                }
            )
            students.append(s)

        return students

    def seed_academics(self, students, courses):
        self.stdout.write("-> Seeding Course Enrollments & Weekly Trajectory Time Series...")
        offerings = list(CourseOffering.objects.all())
        if not offerings:
            return

        for s in students[:120]:
            # Enroll in 3 offerings
            sample_offerings = random.sample(offerings, min(3, len(offerings)))
            for off in sample_offerings:
                Enrollment.objects.get_or_create(
                    student=s,
                    course_offering=off,
                    defaults={
                        'attendance_percentage': s.attendance_percentage,
                        'internal_marks': round(np_clip_val(s.cgpa * 9.5 + random.normalvariate(0, 5), 30.0, 98.0), 1),
                        'grade': 'A' if s.cgpa > 8.5 else ('B+' if s.cgpa > 7.0 else 'C')
                    }
                )

            # Generate 5-week sequential behavior records for DL trajectory model
            base_att = s.attendance_percentage
            base_quiz = s.cgpa * 9.5
            trend_type = random.choice(['stable', 'slip', 'decline'] if s.attendance_percentage < 75 else ['stable', 'improving'])

            for w in range(1, 6):
                if trend_type == 'decline':
                    att_w = max(35.0, base_att - (w * 8.0))
                    quiz_w = max(30.0, base_quiz - (w * 9.0))
                elif trend_type == 'slip':
                    att_w = max(50.0, base_att - (w * 3.0))
                    quiz_w = max(45.0, base_quiz - (w * 3.5))
                else:
                    att_w = min(100.0, base_att + (w * 1.0))
                    quiz_w = min(100.0, base_quiz + (w * 1.5))

                WeeklyPerformanceRecord.objects.get_or_create(
                    student=s,
                    week_number=w,
                    defaults={
                        'attendance_rate': round(att_w, 1),
                        'quiz_score': round(quiz_w, 1),
                        'assignment_score': round(quiz_w + random.normalvariate(2, 4), 1),
                        'lms_activity_hours': round(random.uniform(2.5, 7.5), 1)
                    }
                )

    def seed_clubs(self, departments, faculty_list, students):
        self.stdout.write("-> Seeding 20+ Campus Student Clubs...")
        club_data = [
            ("Campus Turing Coding Society", "CODING", Club.Category.TECHNICAL, "Competitive programming, hackathons, and algorithm sprints.", "C++, Python, Data Structures"),
            ("Robotics & Embedded Systems Club", "ROBOTICS", Club.Category.TECHNICAL, "Autonomous robotics, drone systems, and microcontrollers.", "Arduino, ROS, Circuit Design"),
            ("AI & Data Science Innovators", "AI_CLUB", Club.Category.TECHNICAL, "Machine learning, computer vision, NLP, and Kaggle sprints.", "PyTorch, Scikit-Learn, Deep Learning"),
            ("Campus Web3 & Cyber Defense", "CYBER", Club.Category.TECHNICAL, "Cyber security, blockchain protocols, and network pen-testing.", "Cryptography, Linux, Network Security"),
            ("Design & UI/UX Guild", "DESIGN", Club.Category.TECHNICAL, "Human-centered UI/UX design, design systems, and wireframing.", "Figma, CSS, User Research"),
            ("Debate & Model United Nations", "DEBATE", Club.Category.CULTURAL, "Public speaking, parliamentary debating, and diplomatic policy.", "Public Speaking, Critical Thinking"),
            ("Music & Soundscapes Society", "MUSIC", Club.Category.CULTURAL, "Classical, fusion band, and acoustic campus performances.", "Instrumental Performance, Audio Production"),
            ("Dramatics & Theater Ensemble", "DRAMA", Club.Category.CULTURAL, "Street plays, stage theater, and dramatic writing.", "Stagecraft, Voice Modulation"),
            ("Campus Photography & Cinema Club", "PHOTO", Club.Category.CULTURAL, "Photography, documentary filmmaking, and editing.", "Cinematography, Premier Pro"),
            ("Fine Arts & Graphic Studio", "ARTS", Club.Category.CULTURAL, "Painting, canvas art, sculpting, and digital illustrations.", "Visual Arts, Illustration"),
            ("Campus Cricket Association", "CRICKET", Club.Category.SPORTS, "Inter-university cricket tournaments and practice clinics.", "Team Athletics, Strategic Planning"),
            ("Football & Soccer League", "FOOTBALL", Club.Category.SPORTS, "Campus soccer squad and 5-a-side league tournaments.", "Physical Fitness, Coordination"),
            ("Basketball Society", "BASKETBALL", Club.Category.SPORTS, "Intramural basketball league and campus court tournaments.", "Agility, Court Tactics"),
            ("Athletics & Track Club", "TRACK", Club.Category.SPORTS, "Sprinting, marathon training, and cross-country running.", "Endurance, Athleticism"),
            ("Badminton & Table Tennis Club", "RACQUET", Club.Category.SPORTS, "Racquet sports clinics and annual campus open.", "Reflexes, Hand-eye Coordination"),
            ("Rotaract Community Service", "ROTARACT", Club.Category.SOCIAL, "Blood donation drives, village education, and eco drives.", "Community Outreach, Social Leadership"),
            ("NSS (National Service Scheme)", "NSS", Club.Category.SOCIAL, "Civic engagement, campus tree plantation, and cleanliness.", "Civic Responsibility, Volunteerism"),
            ("Animal Welfare & Care Circle", "PAWS", Club.Category.SOCIAL, "Campus stray animal feeding, vaccination, and adoption.", "Compassion, Animal Care"),
            ("Campus Sustainability & Green Cell", "ECO", Club.Category.SOCIAL, "Waste segregation drives, solar energy awareness, and zero plastic.", "Environmental Policy, Sustainability"),
            ("Entrepreneurship & Startup Incubator", "E_CELL", Club.Category.ENTREPRENEURSHIP, "Business plan pitching, angel investor connects, and MVP demos.", "Business Models, Pitching, Venture Dev"),
            ("Women in Engineering & Leadership", "WIE", Club.Category.ENTREPRENEURSHIP, "Leadership summits, hackathons, and mentorship for women in tech.", "Executive Leadership, Mentorship")
        ]

        clubs = []
        for name, code, cat, desc, skills in club_data:
            c, _ = Club.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'category': cat,
                    'description': desc,
                    'skills_developed': skills,
                    'faculty_coordinator': random.choice(faculty_list),
                    'student_lead': random.choice(students)
                }
            )
            # Add demo memberships
            for s in random.sample(students[:150], random.randint(12, 28)):
                ClubMembership.objects.get_or_create(club=c, student=s, defaults={'role': ClubMembership.Role.MEMBER})
            clubs.append(c)

        return clubs

    def seed_events(self, departments, clubs, students):
        self.stdout.write("-> Seeding 100+ Campus Events & Turnout Forecasts...")
        event_types = Event.EventType.choices
        titles = [
            "National Hackathon: HackPulse 2026",
            "Workshop on Deep Learning & Vision Transformers",
            "Guest Lecture on Quantum Computing Frontiers",
            "Annual Technical Symposium: Technova",
            "Hands-on Workshop: Building Full-Stack Cloud Apps",
            "Campus Placement Readiness & Mock Interviews",
            "Inter-College Basketball Championship",
            "Cultural Night: Rhythm & Beats 2026",
            "Seminar: Autonomous Electric Mobility Systems",
            "Sustainability Drive: Zero Waste Campus Initiative",
            "Workshop on Microservices with Docker and Kubernetes",
            "Code Sprint: 12-Hour Algorithmic Challenge",
            "Design Sprint: UI/UX for Intelligent Systems",
            "Startup Pitch Day: Venture Spark 2026",
            "Workshop on Cybersecurity & Penetration Testing"
        ]

        now = timezone.now()
        for i in range(105):
            etype = random.choice(event_types)[0]
            title = f"{random.choice(titles)} (Session {i+1})"
            days_offset = random.randint(-40, 30) # Past and future
            start = now + timedelta(days=days_offset, hours=random.randint(9, 16))
            end = start + timedelta(hours=random.randint(2, 5))
            cap = random.choice([60, 80, 100, 150, 250, 400])

            dept = random.choice(departments) if random.random() < 0.6 else None
            club = random.choice(clubs) if not dept else None
            status = Event.Status.COMPLETED if days_offset < 0 else Event.Status.UPCOMING

            ev, created = Event.objects.get_or_create(
                title=title,
                defaults={
                    'description': f"Comprehensive campus session covering practical methodologies, expert speaker sessions, and project demonstrations in {title}.",
                    'event_type': etype,
                    'department': dept,
                    'club': club,
                    'location_name': random.choice(["Main Auditorium", "AI Seminar Hall", "Turing Lab 2", "Maxwell Conference Room", "Sports Arena"]),
                    'start_time': start,
                    'end_time': end,
                    'capacity': cap,
                    'speaker': random.choice(["Dr. Arvind Krishna (Industry Fellow)", "Prof. Sarah Jenkins (MIT Alum)", "Alumni Tech Lead, Google", "Dr. Shalini Gupta"]),
                    'status': status,
                    'predicted_attendance': int(cap * random.uniform(0.72, 0.92)),
                    'predicted_no_show_rate': round(random.uniform(8.0, 18.0), 1)
                }
            )

            # Add registrations
            reg_count = min(cap, random.randint(30, int(cap * 1.1)))
            for s in random.sample(students[:180], min(reg_count, 180)):
                reg, _ = EventRegistration.objects.get_or_create(
                    event=ev,
                    student=s,
                    defaults={'attended': (days_offset < 0 and random.random() < 0.85)}
                )
                if reg.attended:
                    Certificate.objects.get_or_create(
                        certificate_id=f"CERT-{ev.id}-{s.student_id}",
                        defaults={'event': ev, 'student': s}
                    )
                    if random.random() < 0.4:
                        EventFeedback.objects.get_or_create(
                            event=ev,
                            student=s,
                            defaults={'rating': random.choice([4, 5, 5, 4, 3]), 'comments': "Incredible hands-on depth and practical demonstrations!"}
                        )

    def seed_projects(self, departments, students, faculty_list):
        self.stdout.write("-> Seeding Capstone Projects & Teams...")
        projects_data = [
            ("AI-Powered Campus Traffic & Congestion Monitor", "Python, Computer Vision, OpenCV, Django, PostgreSQL", "Developing edge-based surveillance inference to quantify gate bottlenecks."),
            ("Autonomous Microgrid Solar Battery Storage Controller", "Embedded C, IoT, Python, Power Electronics", "Intelligent load shifting algorithm optimizing campus solar battery life."),
            ("Decentralized Student Credential & Transcript Verification", "Solidity, Web3, React, Node.js, Cryptography", "Tamper-evident blockchain architecture for issuing degree certificates."),
            ("Predictive Campus Food Supply Chain Optimizer", "Python, Scikit-learn, Time Series, FastAPI", "Forecasting kitchen ingredient provisioning to eliminate food waste."),
            ("Autonomous Campus Delivery Rover Navigation", "ROS, Python, LiDAR, SLAM, C++", "Indoor and outdoor autonomous rover navigating between academic blocks.")
        ]

        for title, skills, desc in projects_data:
            creator = random.choice(students[:50])
            p, _ = Project.objects.get_or_create(
                title=title,
                defaults={
                    'description': desc,
                    'required_skills': skills,
                    'department': creator.department,
                    'creator': creator,
                    'mentor': random.choice(faculty_list),
                    'status': Project.Status.OPEN
                }
            )
            team, _ = Team.objects.get_or_create(project=p, defaults={'name': f"Core {p.title[:15]}"})
            TeamMember.objects.get_or_create(team=team, student=creator, defaults={'role_in_team': "Project Lead & Architect"})
            # Add complementary members
            for s in random.sample(students[51:150], 2):
                TeamMember.objects.get_or_create(team=team, student=s, defaults={'role_in_team': "Specialist Contributor"})

    def seed_complaints(self, students):
        self.stdout.write("-> Seeding 500+ Natural Language Complaints & AI Triage...")
        complaint_samples = [
            ("Ceiling fan making spark in Room 302 Block C", "The fan regulator is burning and sparking when switched on. Please fix immediately.", "ELECTRICAL", "URGENT"),
            ("Water tap dripping continuously in 2nd floor restroom Block A", "Restroom washbasin tap pipe has a cracked joint leaking clean water onto floor.", "WATER", "MEDIUM"),
            ("No Wi-Fi connectivity in Library reading room", "Laptops cannot authenticate to campus eduroam inside 3rd floor quiet zone.", "NETWORK", "HIGH"),
            ("Broken bench and missing screws in Lecture Hall 104", "Wooden bench plank is loose, sharp nails exposed. Risk of injury.", "CLASSROOM", "MEDIUM"),
            ("Air conditioner blowing warm air in Seminar Hall B", "AC compressor is tripping after 5 minutes of running.", "ELECTRICAL", "HIGH"),
            ("Bus Route 4 arrived 40 minutes late at Metro stop", "Morning commuter bus did not adhere to scheduled timetable causing missed first period.", "TRANSPORT", "MEDIUM"),
            ("Cold food served during lunch service counter 2", "The rice and dal were unheated at 1:15 PM lunch rush.", "CANTEEN", "LOW"),
            ("Unauthorized motorcycle parking blocking ramp in East Lot", "Two-wheelers parked directly in front of wheelchair access ramp.", "PARKING", "MEDIUM"),
            ("Stray dogs wandering near Cafeteria pathway", "Pack of aggressive dogs spotted near student walkway.", "SECURITY", "HIGH"),
            ("Projector lamp dead in Alan Turing Lab 3", "Faculty cannot display presentation slides for CS501 lab.", "LABORATORY", "HIGH"),
        ]

        admin_user = User.objects.filter(role=User.Role.MAINTENANCE_STAFF).first()

        for i in range(510):
            sample = random.choice(complaint_samples)
            s = random.choice(students[:200])
            title = f"{sample[0]} (Ticket #{i+1})"
            desc = sample[1]
            triage = ComplaintAITriage.triage_complaint(f"{title}. {desc}")

            status = random.choice([Complaint.Status.SUBMITTED, Complaint.Status.ASSIGNED, Complaint.Status.IN_PROGRESS, Complaint.Status.RESOLVED])
            c = Complaint.objects.create(
                user=s.user if s.user else User.objects.first(),
                title=title,
                description=desc,
                category=triage['category'],
                priority=sample[3] if random.random() < 0.4 else triage['priority'],
                target_department=triage['target_department'],
                location_extracted=triage['location_extracted'],
                confidence=triage['confidence'],
                sla_hours=triage['sla_hours'],
                status=status,
                assigned_to=admin_user if status != Complaint.Status.SUBMITTED else None
            )

            ComplaintStatusHistory.objects.create(
                complaint=c,
                status=c.status,
                updated_by=admin_user,
                comments=f"AI auto-triaged to {c.target_department} with {c.priority} priority."
            )

    def seed_transport(self):
        self.stdout.write("-> Seeding Smart Bus Fleet & Simulated GPS Routes...")
        routes_data = [
            ("Route 1 - City Center Express", "R-01", "City Railway Central", "Campus Main Terminal", 14.5, 40),
            ("Route 2 - Metro Tech Corridor", "R-02", "South Metro Station", "Campus Main Terminal", 11.2, 30),
            ("Route 3 - North Suburbs Shuttle", "R-03", "North Town Square", "Campus Main Terminal", 16.0, 45),
            ("Route 4 - East Campus Ring Connector", "R-04", "East Junction", "Campus Main Terminal", 9.8, 25),
        ]
        
        bus_stops_data = [
            ("Central Metro Station", 12.9650, 77.5850),
            ("MG Road Junction", 12.9680, 77.5890),
            ("Indiranagar 100ft Road", 12.9700, 77.5910),
            ("Campus Outer Ring Gate", 12.9710, 77.5930),
            ("Campus Terminal Main", 12.9716, 77.5946)
        ]

        for name, code, start, end, dist, dur in routes_data:
            r, _ = BusRoute.objects.get_or_create(
                code=code,
                defaults={'name': name, 'start_point': start, 'end_point': end, 'distance_km': dist, 'estimated_duration_mins': dur}
            )
            # Add stops
            for seq, (sname, slat, slng) in enumerate(bus_stops_data, start=1):
                BusStop.objects.get_or_create(
                    route=r,
                    sequence=seq,
                    defaults={'name': f"{r.code} - {sname}", 'latitude': slat, 'longitude': slng, 'estimated_offset_mins': seq * 7}
                )

            # Assign 2-3 buses per route
            for b_idx in range(1, 4):
                bnum = f"KA-01-CP-{r.code[2:]}{b_idx:02d}"
                Bus.objects.get_or_create(
                    bus_number=bnum,
                    defaults={
                        'route': r,
                        'driver_name': f"Driver {random.choice(['Murugan', 'Govind', 'Ramu', 'Satish'])}",
                        'driver_phone': "+91-9876543210",
                        'capacity': 52,
                        'current_passengers': random.randint(20, 48),
                        'is_active': True
                    }
                )

    def seed_parking(self):
        self.stdout.write("-> Seeding 3 Smart Parking Lots & 200+ Individual Sensor Bays...")
        lots_data = [
            ("North Academic Parking Lot", "PKG-NORTH", 80, 12.9730, 77.5945),
            ("East Engineering Parking Lot", "PKG-EAST", 75, 12.9715, 77.5960),
            ("Auditorium South Visitor Bay", "PKG-AUDI", 65, 12.9705, 77.5935),
        ]
        for name, code, total, lat, lng in lots_data:
            lot, _ = ParkingLot.objects.get_or_create(
                code=code,
                defaults={'name': name, 'total_slots': total, 'latitude': lat, 'longitude': lng}
            )
            for s in range(1, total + 1):
                snum = f"{code[-2:]}-{s:02d}"
                is_occ = (random.random() < 0.68) # 68% realistic occupancy
                ParkingSlot.objects.get_or_create(
                    lot=lot,
                    slot_number=snum,
                    defaults={'is_occupied': is_occ, 'slot_type': ParkingSlot.SlotType.CAR if s <= int(total*0.75) else ParkingSlot.SlotType.MOTORCYCLE}
                )

    def seed_canteen(self):
        self.stdout.write("-> Seeding Canteen Menu & Historical Meals...")
        canteen, _ = Canteen.objects.get_or_create(
            code="CAN-MAIN",
            defaults={'name': "Campus Central Dining Hall", 'location_name': "Central Complex", 'seating_capacity': 450}
        )

        menu = [
            ("Masala Dosa & Sambar", MenuItem.MealCategory.BREAKFAST, 40.00),
            ("Idli Vada Combo", MenuItem.MealCategory.BREAKFAST, 35.00),
            ("Executive Veg Thali", MenuItem.MealCategory.LUNCH, 75.00),
            ("South Indian Meals Thali", MenuItem.MealCategory.LUNCH, 60.00),
            ("Paneer Butter Masala Combo", MenuItem.MealCategory.LUNCH, 90.00),
            ("Samosa & Masala Chai", MenuItem.MealCategory.SNACKS, 25.00),
            ("Filter Coffee & Biscuits", MenuItem.MealCategory.SNACKS, 20.00),
            ("Chapati & Mixed Vegetable Curry", MenuItem.MealCategory.DINNER, 55.00),
        ]
        for name, cat, price in menu:
            MenuItem.objects.get_or_create(canteen=canteen, name=name, defaults={'category': cat, 'price': price})

        # Past 30 days meal sales records
        today = timezone.now().date()
        for d in range(30):
            rec_date = today - timedelta(days=d)
            for mtype in ['BREAKFAST', 'LUNCH', 'SNACKS', 'DINNER']:
                prep = random.randint(280, 420) if mtype == 'LUNCH' else random.randint(150, 260)
                sold = int(prep * random.uniform(0.88, 0.98))
                waste = round((prep - sold) * 0.28, 1)
                MealRecord.objects.get_or_create(
                    canteen=canteen,
                    date=rec_date,
                    meal_type=mtype,
                    defaults={'meals_prepared': prep, 'meals_sold': sold, 'leftover_waste_kg': waste}
                )

    def seed_energy(self):
        self.stdout.write("-> Seeding Energy Meters & Telemetry Spikes...")
        meters_data = [
            ("Alan Turing Computer Block", "MTR-TURING", "Alan Turing Computing Block", 52.0),
            ("Ada Lovelace IT Tower", "MTR-LOVELACE", "Ada Lovelace IT Complex", 45.0),
            ("Central AI Research Facility", "MTR-AILAB", "Central AI Research Lab", 65.0),
            ("Central Dining & Kitchen", "MTR-CANTEEN", "Central Dining Hall", 38.0),
            ("University Library Complex", "MTR-LIBRARY", "Library Hub", 40.0),
        ]
        for name, mid, bname, base in meters_data:
            m, _ = EnergyMeter.objects.get_or_create(
                meter_id=mid,
                defaults={'name': name, 'building_name': bname, 'baseline_kwh': base}
            )
            # Create readings
            for h in range(12):
                read = EnergyReading.objects.create(
                    meter=m,
                    kwh_consumed=round(base + random.uniform(-4, 12), 1),
                    temperature=28.0,
                    occupancy_estimate=120
                )
            # Add 1 active anomaly for demonstration
            if mid == "MTR-AILAB":
                EnergyAnomaly.objects.get_or_create(
                    meter=m,
                    defaults={
                        'anomaly_score': -0.38,
                        'kwh_observed': 94.5,
                        'kwh_expected': 25.0,
                        'severity': EnergyAnomaly.Severity.CRITICAL,
                        'anomaly_type': EnergyAnomaly.AnomalyType.NIGHT_LEAK,
                        'explanation': "High nocturnal load (94.5 kWh vs 25.0 kWh expected). Multiple GPU workstation nodes operational after building lockup.",
                        'resolved': False
                    }
                )

    def seed_waste(self):
        self.stdout.write("-> Seeding Waste Records & TrashNet Classifications...")
        today = timezone.now().date()
        for d in range(14):
            WasteRecord.objects.get_or_create(
                date=today - timedelta(days=d),
                defaults={
                    'building_name': "Central Campus Complex",
                    'dry_waste_kg': round(random.uniform(35, 55), 1),
                    'wet_waste_kg': round(random.uniform(28, 45), 1),
                    'recyclable_kg': round(random.uniform(20, 38), 1),
                    'e_waste_kg': round(random.uniform(1.5, 4.0), 1)
                }
            )

def np_clip_val(val, min_v, max_v):
    return max(min_v, min(max_v, val))
