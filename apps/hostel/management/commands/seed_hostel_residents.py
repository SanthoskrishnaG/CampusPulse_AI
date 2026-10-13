import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.accounts.models import User
from apps.students.models import Student
from apps.hostel.models import (
    Hostel, HostelBlock, HostelRoom, HostelFacility,
    HostelAnnouncement, HostelComplaint, HostelMaintenanceRequest,
    HostelMessMenu, HostelMessFeedback, HostelAttendance,
    HostelOutPass, HostelMessAttendance
)

class Command(BaseCommand):
    help = "Seeds comprehensive hostel resident rooms, allocations, outpasses, and mess data"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Initializing CIT Hostel Living & Resident Data Seeding..."))

        # 1. Verify / Create 4 Hostels
        hostels_data = [
            ("BH-1", "Boys Hostel 1 (Senior Hall)", "boys", 11.0253, 77.0268, 420),
            ("BH-2", "Boys Hostel 2 (Junior Hall)", "boys", 11.0248, 77.0270, 380),
            ("GH-1", "Girls Hostel 1 (Kalpana Hall)", "girls", 11.0252, 77.0280, 400),
            ("GH-2", "Girls Hostel 2 (Sarojini Hall)", "girls", 11.0247, 77.0283, 350),
        ]

        hostels = {}
        for code, name, cat, lat, lng, cap in hostels_data:
            h, _ = Hostel.objects.update_or_create(
                code=code,
                defaults={
                    'name': name,
                    'category': cat,
                    'latitude': lat,
                    'longitude': lng,
                    'capacity': cap,
                    'floor_count': 5,
                    'warden_name': f"Prof. {'Natarajan' if cat == 'boys' else 'Meenakshi'}",
                    'warden_contact': "+91 422 2574071 (CIT Ext 204)",
                    'security_contact': "+91 422 2574072 (CIT Security)",
                    'medical_contact': "+91 422 2574075 (CIT Health Centre)",
                    'is_active': True
                }
            )
            hostels[code] = h
        self.stdout.write("  [+] Synchronized 4 Hostels.")

        # 2. Seed Blocks & Rooms
        for code, hostel in hostels.items():
            for block_name in ["Block A", "Block B", "Block C"]:
                block, _ = HostelBlock.objects.get_or_create(
                    hostel=hostel,
                    name=block_name,
                    defaults={'floor_count': 4}
                )

                # 6 rooms per block per floor (Floors 1 to 3) = 18 rooms per block
                prefix = block_name[-1]  # 'A', 'B', 'C'
                for floor in [1, 2, 3]:
                    for r in range(1, 7):
                        r_num = f"{prefix}-{floor}0{r}"
                        room_type = HostelRoom.RoomType.DOUBLE if r % 2 == 0 else HostelRoom.RoomType.TRIPLE
                        cap = 2 if room_type == HostelRoom.RoomType.DOUBLE else 3
                        HostelRoom.objects.update_or_create(
                            hostel=hostel,
                            room_number=r_num,
                            defaults={
                                'block': block,
                                'floor': floor,
                                'room_type': room_type,
                                'capacity': cap,
                                'occupied': cap - 1 if r == 1 else cap,
                                'is_available': (r == 1)
                            }
                        )
        self.stdout.write(f"  [+] Seeded {HostelRoom.objects.count()} resident rooms across all blocks.")

        # 3. Allocate Student Residents
        # Make student (Aarav Patel) resident in BH-1, Room B-204
        demo_student_user = User.objects.filter(username='student').first()
        if demo_student_user and hasattr(demo_student_user, 'student_profile'):
            sp = demo_student_user.student_profile
            sp.accommodation_type = Student.AccommodationType.HOSTEL
            sp.hostel_category = Student.HostelCategory.BOYS
            sp.assigned_hostel = hostels["BH-1"]
            sp.room_number = "B-204"
            sp.save()
            self.stdout.write("  [+] Configured demo student 'Aarav Patel' as resident in BH-1, Room B-204.")

        # Assign ~160 other students as hostelers
        all_students = list(Student.objects.all())
        boys_hostels = [hostels["BH-1"], hostels["BH-2"]]
        girls_hostels = [hostels["GH-1"], hostels["GH-2"]]

        assigned_count = 0
        for i, s in enumerate(all_students):
            if s.user and s.user.username == 'student':
                continue
            if i < 160:  # Assign first 160 students
                is_girl = (i % 3 == 0)
                h = random.choice(girls_hostels) if is_girl else random.choice(boys_hostels)
                cat = 'girls' if is_girl else 'boys'
                floor = random.randint(1, 3)
                block_char = random.choice(['A', 'B', 'C'])
                room_no = f"{block_char}-{floor}0{random.randint(1, 6)}"

                s.accommodation_type = Student.AccommodationType.HOSTEL
                s.hostel_category = cat
                s.assigned_hostel = h
                s.room_number = room_no
                s.save()
                assigned_count += 1
            else:
                s.accommodation_type = Student.AccommodationType.DAY_SCHOLAR
                s.save()

        self.stdout.write(f"  [+] Allocated {assigned_count} students to CIT Hostels.")

        # 4. Seed Out-Pass Records
        now = timezone.now()
        aarav_student = demo_student_user.student_profile if demo_student_user else None

        if aarav_student:
            # Active Approved OutPass for Aarav
            HostelOutPass.objects.update_or_create(
                pass_code="OP-2026-CIT-1042",
                defaults={
                    'student': aarav_student,
                    'hostel': hostels["BH-1"],
                    'pass_type': HostelOutPass.PassType.LOCAL_OUTING,
                    'destination': "Brookefields Mall & Gandhipuram, Coimbatore",
                    'reason': "Weekend book purchase and IEEE workshop supplies.",
                    'contact_phone': "+91 98401 23456",
                    'parent_phone': "+91 94440 98765",
                    'departure_time': now - timedelta(hours=2),
                    'expected_return_time': now + timedelta(hours=4),
                    'status': HostelOutPass.Status.APPROVED,
                    'approval_notes': "Approved by Duty Warden. Return before 8:30 PM roll call.",
                }
            )

            # Past Completed OutPass
            HostelOutPass.objects.update_or_create(
                pass_code="OP-2026-CIT-0881",
                defaults={
                    'student': aarav_student,
                    'hostel': hostels["BH-1"],
                    'pass_type': HostelOutPass.PassType.HOME_VISIT,
                    'destination': "Tiruppur Home",
                    'reason': "Family festival celebration.",
                    'contact_phone': "+91 98401 23456",
                    'parent_phone': "+91 94440 98765",
                    'departure_time': now - timedelta(days=5),
                    'expected_return_time': now - timedelta(days=3),
                    'actual_return_time': now - timedelta(days=3, hours=1),
                    'status': HostelOutPass.Status.COMPLETED,
                    'approval_notes': "Reported back on schedule.",
                }
            )

        # Seed other students' outpasses
        hostel_students = Student.objects.filter(accommodation_type='hostel').exclude(user__username='student')[:15]
        for idx, hs in enumerate(hostel_students):
            code_num = 1100 + idx
            st = random.choice([HostelOutPass.Status.PENDING, HostelOutPass.Status.APPROVED, HostelOutPass.Status.COMPLETED])
            HostelOutPass.objects.update_or_create(
                pass_code=f"OP-2026-CIT-{code_num}",
                defaults={
                    'student': hs,
                    'hostel': hs.assigned_hostel,
                    'pass_type': random.choice(list(HostelOutPass.PassType)),
                    'destination': "Coimbatore Railway Junction / Home",
                    'reason': "Weekend leave / Personal necessity.",
                    'contact_phone': "+91 98765 43210",
                    'parent_phone': "+91 98421 11223",
                    'departure_time': now + timedelta(days=1),
                    'expected_return_time': now + timedelta(days=3),
                    'status': st,
                    'approval_notes': "Parent verified via SMS." if st == HostelOutPass.Status.APPROVED else "",
                }
            )
        self.stdout.write(f"  [+] Seeded {HostelOutPass.objects.count()} Hostel Out-Pass records.")

        # 5. Seed Mess Attendance Records for Today
        today = now.date()
        resident_sample = Student.objects.filter(accommodation_type='hostel')[:80]
        for hs in resident_sample:
            for meal in [HostelMessAttendance.MealType.BREAKFAST, HostelMessAttendance.MealType.LUNCH]:
                HostelMessAttendance.objects.update_or_create(
                    student=hs,
                    date=today,
                    meal_type=meal,
                    defaults={
                        'hostel': hs.assigned_hostel,
                        'is_present': True,
                        'special_diet': "Vegetarian" if random.random() > 0.3 else "General",
                    }
                )
        self.stdout.write(f"  [+] Seeded {HostelMessAttendance.objects.count()} Mess Attendance records.")

        # 6. Ensure Weekly Mess Menus are Seeded
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        sample_menus = [
            ("Idli, Sambar, Coconut Chutney, Coffee/Tea", "Rice, Drumstick Sambar, Tomato Rasam, Cabbage Poriyal, Curd", "Sundal, Hot Tea", "Chapathi, Paneer Butter Masala, Veg Fried Rice, Milk"),
            ("Pongal, Medu Vada, Sambar, Chutney", "Variety Rice (Lemon & Curd), Potato Fry, Appalam", "Veg Puff, Tea/Coffee", "Poori, Potato Masala, Jeera Rice, Dal"),
            ("Puri Masala, Chana Curry, Tea/Coffee", "Rice, Mysore Rasam, Aviyal, Beans Poriyal, Curd", "Banana Bonda, Tea", "Dosa, Sambar, Tomato Chutney, Kheer"),
            ("Rava Upma, Coconut Chutney, Tea/Coffee", "Rice, Spinach Kootu, Pepper Rasam, Kara Kuzhambu, Curd", "Samosa, Tea", "Parotta, Veg Kurma, Ghee Rice, Milk"),
            ("Set Dosa, Vadakari, Filter Coffee", "South Indian Meals, Vatha Kuzhambu, Appalam, Curd", "Biscuits, Masala Tea", "Aloo Paratha, Curd, Pulao, Dal Fry"),
            ("Poori Bhaji, Chutney, Coffee/Tea", "Veg Biryani, Onion Raitha, Ennai Kathirikai, Payasam", "Bajji, Tea/Coffee", "Idiyappam, Coconut Milk, Veg Stew"),
            ("Masala Dosa, Sambar, Chutney", "Special Sunday Feast, Veg Biryani, Paneer 65, Ice Cream", "Sweet Corn, Tea", "Phulka, Dal Tadka, Peas Pulao, Fruit Custard")
        ]
        for d, menu in zip(days, sample_menus):
            HostelMessMenu.objects.update_or_create(
                day_of_week=d,
                defaults={
                    'breakfast': menu[0],
                    'lunch': menu[1],
                    'snacks': menu[2],
                    'dinner': menu[3],
                    'timing_info': "Breakfast: 7:30-9:00 AM | Lunch: 12:30-2:00 PM | Dinner: 7:30-9:00 PM",
                }
            )
        self.stdout.write("  [+] Verified complete 7-day CIT hostel mess menus.")

        self.stdout.write(self.style.SUCCESS("\n[SUCCESS] CIT Hostel resident ecosystem populated successfully!"))
