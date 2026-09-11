from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Unified User model for CampusPulse AI supporting 12 RBAC roles.
    """
    class Role(models.TextChoices):
        SUPER_ADMIN = 'SUPER_ADMIN', 'Super Administrator'
        COLLEGE_ADMIN = 'COLLEGE_ADMIN', 'College Administrator'
        DEPARTMENT_ADMIN = 'DEPARTMENT_ADMIN', 'Department Administrator'
        FACULTY = 'FACULTY', 'Faculty Member'
        STUDENT = 'STUDENT', 'Student'
        CLUB_ADMIN = 'CLUB_ADMIN', 'Club Administrator'
        CLUB_MEMBER = 'CLUB_MEMBER', 'Club Member'
        TRANSPORT_MANAGER = 'TRANSPORT_MANAGER', 'Transport Manager'
        MAINTENANCE_STAFF = 'MAINTENANCE_STAFF', 'Maintenance Staff'
        CANTEEN_MANAGER = 'CANTEEN_MANAGER', 'Canteen Manager'
        SECURITY_STAFF = 'SECURITY_STAFF', 'Security Staff'
        FACILITY_MANAGER = 'FACILITY_MANAGER', 'Facility Manager'

    role = models.CharField(
        max_length=30,
        choices=Role.choices,
        default=Role.STUDENT,
        help_text="Designated system role governing permissions and dashboard views."
    )
    phone = models.CharField(max_length=20, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_super_admin(self):
        return self.role == self.Role.SUPER_ADMIN or self.is_superuser

    def is_college_admin(self):
        return self.role in [self.Role.COLLEGE_ADMIN, self.Role.SUPER_ADMIN] or self.is_superuser

    def is_department_admin(self):
        return self.role in [self.Role.DEPARTMENT_ADMIN, self.Role.COLLEGE_ADMIN, self.Role.SUPER_ADMIN] or self.is_superuser

    def is_faculty(self):
        return self.role == self.Role.FACULTY

    def is_student(self):
        return self.role in [self.Role.STUDENT, self.Role.CLUB_MEMBER]

    def is_club_admin(self):
        return self.role == self.Role.CLUB_ADMIN

    def is_transport_manager(self):
        return self.role in [self.Role.TRANSPORT_MANAGER, self.Role.SUPER_ADMIN]

    def is_canteen_manager(self):
        return self.role in [self.Role.CANTEEN_MANAGER, self.Role.SUPER_ADMIN]

    def is_maintenance_or_facility(self):
        return self.role in [self.Role.MAINTENANCE_STAFF, self.Role.FACILITY_MANAGER, self.Role.SUPER_ADMIN]

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
