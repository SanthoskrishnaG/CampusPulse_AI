from django.db import models
from django.conf import settings
from django.utils import timezone

class Hostel(models.Model):
    class Category(models.TextChoices):
        BOYS = 'boys', 'Boys Hostel'
        GIRLS = 'girls', 'Girls Hostel'

    name = models.CharField(max_length=100, help_text="e.g. Boys Hostel 1")
    code = models.CharField(max_length=20, unique=True, help_text="e.g. BH-1, GH-1")
    category = models.CharField(max_length=10, choices=Category.choices, default=Category.BOYS)
    latitude = models.FloatField(default=11.0253)
    longitude = models.FloatField(default=77.0268)
    floor_count = models.PositiveIntegerField(default=5)
    capacity = models.PositiveIntegerField(default=400)
    description = models.TextField(blank=True)
    
    # Staff / Emergency Contacts
    warden_name = models.CharField(max_length=100, default="Hostel Warden")
    warden_contact = models.CharField(max_length=50, default="+91 422 2574071 (CIT Ext 204)")
    security_contact = models.CharField(max_length=50, default="+91 422 2574072 (CIT Security)")
    medical_contact = models.CharField(max_length=50, default="+91 422 2574075 (CIT Health Centre)")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category', 'code']

    def __str__(self):
        return f"{self.name} ({self.code})"

    def occupied_count(self):
        # Calculate from assigned students
        assigned = self.resident_students.count()
        return assigned if assigned > 0 else int(self.capacity * 0.85)

    def available_count(self):
        return max(0, self.capacity - self.occupied_count())

    def occupancy_percentage(self):
        if self.capacity == 0:
            return 0.0
        return round((self.occupied_count() / self.capacity) * 100.0, 1)


class HostelBlock(models.Model):
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='blocks')
    name = models.CharField(max_length=50, help_text="e.g. Block A, Block B")
    floor_count = models.PositiveIntegerField(default=4)

    class Meta:
        unique_together = ('hostel', 'name')
        ordering = ['hostel', 'name']

    def __str__(self):
        return f"{self.hostel.code} - {self.name}"


class HostelRoom(models.Model):
    class RoomType(models.TextChoices):
        SINGLE = 'SINGLE', 'Single Occupancy'
        DOUBLE = 'DOUBLE', 'Double Sharing'
        TRIPLE = 'TRIPLE', 'Triple Sharing'
        QUAD = 'QUAD', 'Four Sharing'

    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='rooms')
    block = models.ForeignKey(HostelBlock, on_delete=models.CASCADE, related_name='rooms', null=True, blank=True)
    room_number = models.CharField(max_length=20, help_text="e.g. B-101, G-204")
    floor = models.PositiveIntegerField(default=1)
    room_type = models.CharField(max_length=20, choices=RoomType.choices, default=RoomType.DOUBLE)
    capacity = models.PositiveIntegerField(default=2)
    occupied = models.PositiveIntegerField(default=2)
    is_available = models.BooleanField(default=False)

    class Meta:
        unique_together = ('hostel', 'room_number')
        ordering = ['hostel', 'room_number']

    def __str__(self):
        return f"{self.hostel.code} Room {self.room_number}"


class HostelFacility(models.Model):
    class Category(models.TextChoices):
        UTILITY = 'UTILITY', 'Essential Utilities'
        ACADEMIC = 'ACADEMIC', 'Study & Research'
        RECREATION = 'RECREATION', 'Recreation & Wellness'
        SAFETY = 'SAFETY', 'Safety & Health'

    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='facilities')
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.UTILITY)
    icon = models.CharField(max_length=10, default="✨")
    status = models.CharField(max_length=50, default="Operational")
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['hostel', 'category', 'name']

    def __str__(self):
        return f"{self.hostel.code}: {self.name} ({self.status})"


class HostelAnnouncement(models.Model):
    class Priority(models.TextChoices):
        INFO = 'INFO', 'Notice / Information'
        WARNING = 'WARNING', 'Important Update'
        URGENT = 'URGENT', 'Urgent / Emergency'

    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='announcements', null=True, blank=True, help_text="Null for all hostels")
    title = models.CharField(max_length=200)
    content = models.TextField()
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.INFO)
    is_public = models.BooleanField(default=False, help_text="Whether visible to public campus")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        target = self.hostel.code if self.hostel else "ALL HOSTELS"
        return f"[{target}] {self.title}"


class HostelComplaint(models.Model):
    class Category(models.TextChoices):
        WATER = 'WATER', 'Drinking Water / RO Filter'
        ELECTRICITY = 'ELECTRICITY', 'Power / Light / Fan'
        WIFI = 'WIFI', 'Campus Wi-Fi / LAN'
        ROOM = 'ROOM', 'Room Furniture & Bed'
        BATHROOM = 'BATHROOM', 'Washroom & Plumbing'
        CLEANING = 'CLEANING', 'Housekeeping & Hygiene'
        SECURITY = 'SECURITY', 'Hostel Security / Biometric'
        OTHER = 'OTHER', 'Other Hostel Issues'

    class Priority(models.TextChoices):
        LOW = 'LOW', 'Low'
        MEDIUM = 'MEDIUM', 'Medium'
        HIGH = 'HIGH', 'High'
        URGENT = 'URGENT', 'Urgent'

    class Status(models.TextChoices):
        REPORTED = 'REPORTED', 'Reported'
        VERIFIED = 'VERIFIED', 'Verified'
        ASSIGNED = 'ASSIGNED', 'Assigned'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        RESOLVED = 'RESOLVED', 'Resolved'
        CLOSED = 'CLOSED', 'Closed'

    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='hostel_complaints')
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='complaints')
    room_number = models.CharField(max_length=20)
    category = models.CharField(max_length=30, choices=Category.choices, default=Category.ELECTRICITY)
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.MEDIUM)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.REPORTED)
    title = models.CharField(max_length=200)
    description = models.TextField()
    resolution_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"HC-{self.id}: {self.title} ({self.status})"


class HostelMaintenanceRequest(models.Model):
    class Priority(models.TextChoices):
        LOW = 'LOW', 'Routine'
        MEDIUM = 'MEDIUM', 'Standard'
        HIGH = 'HIGH', 'High Priority'
        EMERGENCY = 'EMERGENCY', 'Emergency'

    class Status(models.TextChoices):
        REPORTED = 'REPORTED', 'Submitted'
        IN_PROGRESS = 'IN_PROGRESS', 'Technician Assigned'
        COMPLETED = 'COMPLETED', 'Completed'

    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='maintenance_requests')
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='maintenance_requests')
    room_number = models.CharField(max_length=20)
    item = models.CharField(max_length=100, help_text="e.g. Ceiling Fan, Light Fixture, Door Latch, Water Tap")
    description = models.TextField()
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.MEDIUM)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.REPORTED)
    technician_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"HMR-{self.id}: {self.item} - Room {self.room_number} [{self.status}]"


class HostelMessMenu(models.Model):
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='mess_menus', null=True, blank=True)
    day_of_week = models.CharField(max_length=20, help_text="Monday, Tuesday, etc.")
    breakfast = models.TextField(help_text="Idli, Sambar, Chutney, Tea/Coffee")
    lunch = models.TextField(help_text="Rice, Sambar, Rasam, Kootu, Curd")
    snacks = models.TextField(help_text="Sundal, Tea / Coffee")
    dinner = models.TextField(help_text="Chapathi, Dal, Mixed Rice, Milk")
    timing_info = models.CharField(max_length=100, default="Breakfast: 7:30-9:00 | Lunch: 12:30-2:00 | Dinner: 7:30-9:00")
    special_notes = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"Mess Menu - {self.day_of_week} ({self.hostel.code if self.hostel else 'General'})"


class HostelEvent(models.Model):
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=200)
    description = models.TextField()
    event_date = models.DateTimeField()
    location = models.CharField(max_length=100, default="Hostel Common Room")
    organizer = models.CharField(max_length=100, default="Hostel Committee")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['event_date']

    def __str__(self):
        return f"{self.title} ({self.hostel.code})"


class HostelMessFeedback(models.Model):
    class MealType(models.TextChoices):
        BREAKFAST = 'BREAKFAST', 'Breakfast'
        LUNCH = 'LUNCH', 'Lunch'
        SNACKS = 'SNACKS', 'Evening Snacks'
        DINNER = 'DINNER', 'Dinner'

    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='hostel_mess_feedbacks')
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='mess_feedbacks')
    meal_type = models.CharField(max_length=20, choices=MealType.choices, default=MealType.LUNCH)
    rating = models.PositiveSmallIntegerField(default=4, help_text="Rating out of 5")
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Mess Feedback - {self.student.get_display_name()} ({self.meal_type}: {self.rating}/5)"


class HostelAttendance(models.Model):
    class Status(models.TextChoices):
        PRESENT = 'PRESENT', 'Present (In-Campus/Hostel)'
        LATE = 'LATE', 'Late Return'
        ON_LEAVE = 'ON_LEAVE', 'Official Home Pass'
        ABSENT = 'ABSENT', 'Unexcused Absence'

    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='hostel_attendance_records')
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PRESENT)
    verified_by = models.CharField(max_length=100, default="Duty Resident Tutor")
    remarks = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'date')
        ordering = ['-date', 'student']

    def __str__(self):
        return f"{self.date} - {self.student.student_id}: {self.get_status_display()}"

