from django.db import models
from apps.students.models import Student
from apps.faculty.models import Faculty

class Club(models.Model):
    class Category(models.TextChoices):
        TECHNICAL = 'TECHNICAL', 'Technical & Coding'
        CULTURAL = 'CULTURAL', 'Cultural & Arts'
        SPORTS = 'SPORTS', 'Sports & Athletics'
        SOCIAL = 'SOCIAL', 'Community & Social Service'
        ENTREPRENEURSHIP = 'ENTREPRENEURSHIP', 'Innovation & Entrepreneurship'

    name = models.CharField(max_length=150, unique=True)
    code = models.CharField(max_length=30, unique=True)
    category = models.CharField(max_length=40, choices=Category.choices, default=Category.TECHNICAL)
    description = models.TextField()
    skills_developed = models.CharField(max_length=255, default="Leadership, Teamwork")
    faculty_coordinator = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True, blank=True, related_name='coordinated_clubs')
    student_lead = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, blank=True, related_name='led_clubs')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"

    def member_count(self):
        return self.memberships.filter(is_approved=True).count()

class ClubMembership(models.Model):
    class Role(models.TextChoices):
        MEMBER = 'MEMBER', 'General Member'
        CORE_LEAD = 'CORE_LEAD', 'Core Committee Lead'
        PRESIDENT = 'PRESIDENT', 'Club President'
        SECRETARY = 'SECRETARY', 'Club Secretary'

    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='memberships')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='club_memberships')
    role = models.CharField(max_length=30, choices=Role.choices, default=Role.MEMBER)
    joined_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=True)

    class Meta:
        unique_together = ('club', 'student')

    def __str__(self):
        return f"{self.student.get_display_name()} in {self.club.name} ({self.role})"

class ClubAnnouncement(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='announcements')
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.club.name}] {self.title}"

class ClubAchievement(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='achievements')
    title = models.CharField(max_length=200)
    competition = models.CharField(max_length=200)
    position = models.CharField(max_length=100, default="1st Place / Winner")
    award_date = models.DateField()

    def __str__(self):
        return f"{self.club.name} - {self.title} ({self.position})"
