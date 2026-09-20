from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.hostel.models import (
    Hostel, HostelBlock, HostelRoom, HostelFacility,
    HostelAnnouncement, HostelComplaint, HostelMaintenanceRequest,
    HostelMessMenu, HostelEvent, HostelMessFeedback, HostelAttendance
)
from apps.common.models import CampusLocation
from apps.students.models import Student
from apps.departments.models import Department
from apps.accounts.models import User
import datetime

class Command(BaseCommand):
    help = "Seed initial CIT Hostel data (BH-1, BH-2, GH-1, GH-2), blocks, rooms, facilities, menus, and resident links."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("=== Seeding CIT Hostel Management Module ==="))

        # 1. Seed the 4 CIT Hostel Buildings
        hostels_data = [
            {
                'name': 'Boys Hostel 1',
                'code': 'BH-1',
                'category': Hostel.Category.BOYS,
                'latitude': 11.02530,
                'longitude': 77.02680,
                'warden_name': 'Dr. K. Senthil Kumar',
                'warden_contact': '+91 94431 82910 (Ext 204)',
                'security_contact': '+91 422 2574071 (BH-1 Security Desk)',
                'medical_contact': '+91 422 2574075 (CIT Health Centre)',
                'capacity': 450,
                'floor_count': 4,
                'description': 'Senior Boys Residential Hall (Kaveri & Bhavani Blocks) with gigabit LAN and solar heating.',
            },
            {
                'name': 'Boys Hostel 2',
                'code': 'BH-2',
                'category': Hostel.Category.BOYS,
                'latitude': 11.02480,
                'longitude': 77.02700,
                'warden_name': 'Dr. R. Balasubramanian',
                'warden_contact': '+91 94432 71829 (Ext 205)',
                'security_contact': '+91 422 2574072 (BH-2 Security Desk)',
                'medical_contact': '+91 422 2574075 (CIT Health Centre)',
                'capacity': 400,
                'floor_count': 4,
                'description': 'Junior Boys Residential Hall (Vaigai & Amaravathi Blocks) adjacent to CIT sports pavilion.',
            },
            {
                'name': 'Girls Hostel 1',
                'code': 'GH-1',
                'category': Hostel.Category.GIRLS,
                'latitude': 11.02520,
                'longitude': 77.02800,
                'warden_name': 'Dr. M. Vijayalakshmi',
                'warden_contact': '+91 94433 62738 (Ext 206)',
                'security_contact': '+91 422 2574073 (GH-1 Cordon Security)',
                'medical_contact': '+91 422 2574075 (CIT Health Centre)',
                'capacity': 420,
                'floor_count': 4,
                'description': 'Senior Girls Residential Hall (Siruvani & Thamirabarani Blocks) with 24/7 security cordon.',
            },
            {
                'name': 'Girls Hostel 2',
                'code': 'GH-2',
                'category': Hostel.Category.GIRLS,
                'latitude': 11.02470,
                'longitude': 77.02830,
                'warden_name': 'Dr. S. Radha',
                'warden_contact': '+91 94434 51647 (Ext 207)',
                'security_contact': '+91 422 2574074 (GH-2 Cordon Security)',
                'medical_contact': '+91 422 2574075 (CIT Health Centre)',
                'capacity': 380,
                'floor_count': 4,
                'description': 'Junior Girls Residential Hall (Noyyal & Palar Blocks) with modern study halls and gymnasium.',
            },
        ]

        hostels = {}
        for hdata in hostels_data:
            h, created = Hostel.objects.update_or_create(
                code=hdata['code'],
                defaults=hdata
            )
            hostels[h.code] = h
            status = "Created" if created else "Updated"
            self.stdout.write(f"  [{status}] {h.name} ({h.code}) - {h.get_category_display()}")

            # Sync with CampusLocation for map display
            CampusLocation.objects.update_or_create(
                code=h.code,
                defaults={
                    'name': h.name,
                    'category': CampusLocation.Category.HOSTEL,
                    'latitude': h.latitude,
                    'longitude': h.longitude,
                    'floor_count': h.floor_count,
                    'capacity': h.capacity,
                    'description': h.description,
                    'is_active': True,
                }
            )

        # 2. Seed Hostel Blocks
        blocks_data = [
            ('BH-1', [('Block A - Kaveri', 4), ('Block B - Bhavani', 4)]),
            ('BH-2', [('Block C - Vaigai', 4), ('Block D - Amaravathi', 4)]),
            ('GH-1', [('Block A - Siruvani', 4), ('Block B - Thamirabarani', 4)]),
            ('GH-2', [('Block C - Noyyal', 4), ('Block D - Palar', 4)]),
        ]

        created_blocks = {}
        for hcode, blist in blocks_data:
            hostel = hostels[hcode]
            for bname, floors in blist:
                b, _ = HostelBlock.objects.update_or_create(
                    hostel=hostel,
                    name=bname,
                    defaults={
                        'floor_count': floors,
                    }
                )
                created_blocks[f"{hcode}_{bname}"] = b

        # 3. Seed Sample Rooms for each hostel
        room_types = [
            (HostelRoom.RoomType.SINGLE, 1, 1),
            (HostelRoom.RoomType.DOUBLE, 2, 2),
            (HostelRoom.RoomType.TRIPLE, 3, 3),
            (HostelRoom.RoomType.QUAD, 4, 3),
        ]

        for hcode, hostel in hostels.items():
            first_block = hostel.blocks.first()
            if not first_block:
                continue
            for floor in range(1, 4):
                for room_idx in range(1, 6):
                    room_num = f"{first_block.name[6]}-{floor}0{room_idx}"
                    rtype, cap, occ = room_types[(floor + room_idx) % len(room_types)]
                    HostelRoom.objects.update_or_create(
                        hostel=hostel,
                        room_number=room_num,
                        defaults={
                            'block': first_block,
                            'floor': floor,
                            'room_type': rtype,
                            'capacity': cap,
                            'occupied': occ,
                            'is_available': (occ < cap),
                        }
                    )

        # 4. Seed Facilities for all 4 Hostels
        facility_templates = [
            ("High-Speed Wi-Fi 6 Mesh", HostelFacility.Category.UTILITY, "📶", "1 Gbps optic fiber mesh network across all corridors"),
            ("RO Purified Drinking Water", HostelFacility.Category.UTILITY, "💧", "Multi-stage RO & UV water coolers on every floor"),
            ("Solar Water Heaters", HostelFacility.Category.UTILITY, "☀️", "Solar thermal hot water available 6 AM - 9 AM & 6 PM - 9 PM"),
            ("Central Dining Mess Hall", HostelFacility.Category.UTILITY, "🍽️", "Multi-cuisine South & North Indian hygienic dining facility"),
            ("Air-Conditioned Study Hall", HostelFacility.Category.ACADEMIC, "📚", "Silent study cubicles with power sockets and technical references"),
            ("Resident Fitness Gym", HostelFacility.Category.RECREATION, "🏋️", "Cardio treadmills, dumbbells, multi-gym stations"),
            ("Indoor Games Arena", HostelFacility.Category.RECREATION, "🏓", "Table Tennis, Carrom, Chess boards, and recreation TV hall"),
            ("24/7 Security & AI CCTV", HostelFacility.Category.SAFETY, "🛡️", "Biometric turnstiles and continuous security patrol"),
            ("Hostel Health Station", HostelFacility.Category.SAFETY, "🩺", "First aid, emergency oxygen, and 24/7 ambulance tie-up with CIT Health Centre"),
        ]

        for hcode, hostel in hostels.items():
            for fname, fcat, ficon, fdesc in facility_templates:
                HostelFacility.objects.update_or_create(
                    hostel=hostel,
                    name=fname,
                    defaults={
                        'category': fcat,
                        'icon': ficon,
                        'status': 'Operational',
                        'description': fdesc,
                    }
                )

        # 5. Seed 7-Day Mess Menus
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        menu_templates = [
            ("Idli, Medu Vada, Sambar, Coconut Chutney, Tea/Coffee",
             "South Indian Thali: Rice, Sambar, Rasam, Kootu, Poriyal, Curd, Appalam",
             "Samosa / Bajji with Mint Chutney, Masala Chai",
             "Phulka Roti, Paneer Butter Masala, Veg Pulao, Dal Tadka, Fruit Custard"),
            ("Pongal, Medu Vada, Tomato Chutney, Filter Coffee",
             "Variety Rice: Lemon Rice, Curd Rice, Potato Fry, Pickle, Buttermilk",
             "Pani Puri / Sundal, Green Tea",
             "Chapati, Mixed Veg Kurma, Jeera Rice, Dal Fry, Payasam"),
            ("Poori Masala, Coconut Chutney, Tea/Coffee",
             "Full Meals: Rice, Drumstick Sambar, Tomato Rasam, Cabbage Poriyal, Mor Kuzhambu",
             "Veg Cutlet with Tomato Ketchup, Hot Tea",
             "Parotta / Chapati, Veg Salna, Tomato Rice, Raitha, Gulab Jamun"),
            ("Rava Upma / Kichadi, Chutney, Sambar, Filter Coffee",
             "Meals: Rice, Arachivitta Sambar, Pepper Rasam, Raw Banana Fry, Curd",
             "Pakoda / Mysore Bonda, Cardamom Tea",
             "Phulka, Dal Makhani, Kashmiri Pulao, Green Salad, Ice Cream"),
            ("Masala Dosa / Plain Dosa, Sambar, 2 Chutneys, Tea",
             "Special Biryani: Veg Dum Biryani, Onion Raitha, Ennai Kathirikai, Papad",
             "Sweet Corn / Bread Sandwich, Tea",
             "Chapati, Paneer Tikka Masala, Steamed Rice, Rasam, Curd"),
            ("Aloo Paratha with Butter, Curd, Pickle, Tea",
             "Tamil Nadu Meals: Rice, Murungai Keerai Sambar, Garlic Rasam, Yam Varuval, Payasam",
             "Puffs / Banana Fritters, Filter Coffee",
             "Poori / Naan, Dal Maharani, Ghee Rice, Mixed Salad, Kesari"),
            ("Uttapam / Rava Idli, Kara Chutney, Sambar, Coffee",
             "Sunday Feast: Peas Pulao, Paneer Gravy / Chicken Chettinad, Veg Pulao, Ice Cream",
             "Biscuits & Tea / Coffee",
             "Phulka, Dal Tadka, Fried Rice, Manchurian, Sweet")
        ]

        for hcode, hostel in hostels.items():
            for idx, day_name in enumerate(days):
                bf, lu, sn, di = menu_templates[idx]
                HostelMessMenu.objects.update_or_create(
                    hostel=hostel,
                    day_of_week=day_name,
                    defaults={
                        'breakfast': bf,
                        'lunch': lu,
                        'snacks': sn,
                        'dinner': di,
                        'timing_info': 'Breakfast: 7:15-8:45 AM | Lunch: 12:30-2:00 PM | Dinner: 7:45-9:15 PM',
                        'special_notes': 'Special Sunday Feast' if day_name == 'Sunday' else ''
                    }
                )

        # 6. Seed Announcements
        announcements = [
            ("CIT Hostel Premier League (HPL) 2026",
             "Inter-hostel sports tournament kicks off next Saturday on the CIT main sports ground. Team registrations open till Thursday 5 PM at Warden office.",
             HostelAnnouncement.Priority.INFO),
            ("Scheduled Wi-Fi Gateway Firmware Upgrade",
             "Wi-Fi access points across BH-1, BH-2, GH-1, and GH-2 will undergo maintenance on Sunday 2:00 AM - 4:00 AM. Internet access will be temporarily paused.",
             HostelAnnouncement.Priority.WARNING),
            ("Mess Advisory Committee (MAC) Monthly Session",
             "Resident student representatives from each floor are requested to assemble in the Dining Hall conference room this Wednesday at 7:30 PM.",
             HostelAnnouncement.Priority.URGENT),
        ]

        for hcode, hostel in hostels.items():
            for title, content, priority in announcements:
                HostelAnnouncement.objects.update_or_create(
                    hostel=hostel,
                    title=title,
                    defaults={
                        'content': content,
                        'priority': priority,
                        'is_public': False,
                    }
                )

        # 7. Seed Sample Hostel Events
        now = timezone.now()
        for hcode, hostel in hostels.items():
            HostelEvent.objects.update_or_create(
                hostel=hostel,
                title=f"{hostel.name} Freshers & Cultural Night",
                defaults={
                    'description': "Annual residential freshers welcome evening with music, talents, and community dinner.",
                    'event_date': now + datetime.timedelta(days=12),
                    'location': "Hostel Common Quadrangle",
                    'organizer': "Hostel Student Council",
                }
            )

        # 8. Configure Demo Users
        self.stdout.write("2. Configuring Demo User Accounts for Role-Based Tests...")
        dept = Department.objects.first()

        # Check 'student' demo account
        demo_student_user = User.objects.filter(username='student').first()
        if demo_student_user:
            demo_student_profile, _ = Student.objects.get_or_create(
                user=demo_student_user,
                defaults={
                    'student_id': 'CIT-BH-001',
                    'first_name': 'Student',
                    'department': dept,
                }
            )
            demo_student_profile.accommodation_type = Student.AccommodationType.HOSTEL
            demo_student_profile.hostel_category = Student.HostelCategory.BOYS
            demo_student_profile.assigned_hostel = hostels['BH-1']
            demo_student_profile.room_number = 'A-204'
            demo_student_profile.is_accommodation_configured = True
            demo_student_profile.save()
            self.stdout.write(self.style.SUCCESS("  [Assigned] User 'student' -> Boys Hostel 1 (BH-1), Room A-204"))

        # Create or update a Day Scholar demo account 'dayscholar'
        ds_user, created = User.objects.get_or_create(
            username='dayscholar',
            defaults={
                'email': 'dayscholar@cit.edu.in',
                'first_name': 'Kavitha',
                'last_name': 'Ramesh',
                'role': User.Role.STUDENT
            }
        )
        if created:
            ds_user.set_password('dayscholar123')
            ds_user.save()

        ds_profile, _ = Student.objects.get_or_create(
            user=ds_user,
            defaults={
                'student_id': 'CIT-DS-002',
                'first_name': 'Kavitha',
                'last_name': 'Ramesh',
                'department': dept,
            }
        )
        ds_profile.accommodation_type = Student.AccommodationType.DAY_SCHOLAR
        ds_profile.hostel_category = None
        ds_profile.assigned_hostel = None
        ds_profile.room_number = ''
        ds_profile.is_accommodation_configured = True
        ds_profile.save()
        self.stdout.write(self.style.SUCCESS("  [Assigned] User 'dayscholar' -> Day Scholar (Strictly Blocked from Hostel)"))

        # Create or update a Girls Hostel demo account 'girlstudent'
        gh_user, created = User.objects.get_or_create(
            username='girlstudent',
            defaults={
                'email': 'girlstudent@cit.edu.in',
                'first_name': 'Ananya',
                'last_name': 'Sundaram',
                'role': User.Role.STUDENT
            }
        )
        if created:
            gh_user.set_password('girlstudent123')
            gh_user.save()

        gh_profile, _ = Student.objects.get_or_create(
            user=gh_user,
            defaults={
                'student_id': 'CIT-GH-003',
                'first_name': 'Ananya',
                'last_name': 'Sundaram',
                'department': dept,
            }
        )
        gh_profile.accommodation_type = Student.AccommodationType.HOSTEL
        gh_profile.hostel_category = Student.HostelCategory.GIRLS
        gh_profile.assigned_hostel = hostels['GH-1']
        gh_profile.room_number = 'B-102'
        gh_profile.is_accommodation_configured = True
        gh_profile.save()
        self.stdout.write(self.style.SUCCESS("  [Assigned] User 'girlstudent' -> Girls Hostel 1 (GH-1), Room B-102"))

        # 9. Seed Sample Complaints, Maintenance, Attendance & Feedback for demo student
        if demo_student_user:
            demo_student = demo_student_user.student_profile
            HostelComplaint.objects.get_or_create(
                student=demo_student,
                title="Slow Wi-Fi speed during evening hours",
                defaults={
                    'hostel': hostels['BH-1'],
                    'room_number': 'A-204',
                    'category': HostelComplaint.Category.WIFI,
                    'description': "Wi-Fi bandwidth drops significantly in 2nd floor Kaveri block between 8 PM and 10 PM.",
                    'status': HostelComplaint.Status.IN_PROGRESS,
                    'priority': HostelComplaint.Priority.MEDIUM,
                }
            )

            HostelMaintenanceRequest.objects.get_or_create(
                student=demo_student,
                item="Ceiling Fan Speed Regulator",
                room_number='A-204',
                defaults={
                    'hostel': hostels['BH-1'],
                    'description': "Fan regulator knob stuck at position 2 and making slight humming noise.",
                    'status': HostelMaintenanceRequest.Status.REPORTED,
                    'priority': HostelMaintenanceRequest.Priority.HIGH,
                }
            )

            HostelAttendance.objects.get_or_create(
                student=demo_student,
                date=datetime.date.today(),
                defaults={
                    'hostel': hostels['BH-1'],
                    'status': HostelAttendance.Status.PRESENT,
                    'verified_by': 'Tutor K. Murugan',
                    'remarks': 'Biometric entry verified at 8:15 PM'
                }
            )

            HostelMessFeedback.objects.get_or_create(
                student=demo_student,
                meal_type=HostelMessFeedback.MealType.LUNCH,
                defaults={
                    'hostel': hostels['BH-1'],
                    'rating': 5,
                    'comments': 'South Indian Meals with fresh curd and hot sambar was excellent today.'
                }
            )

        self.stdout.write(self.style.SUCCESS("=== CIT Hostel Data Seeding Successfully Completed ==="))
