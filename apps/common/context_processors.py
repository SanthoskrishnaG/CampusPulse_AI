import json
from django.conf import settings
from .weather import WeatherService
from apps.accounts.models import User

from config.campus_config import CAMPUS_CONFIG

def campus_context(request):
    """
    Injects campus metadata, user permissions, weather, and system stats into templates.
    """
    unread_notifications = 0
    if request.user.is_authenticated:
        try:
            from apps.notifications.models import Notification
            unread_notifications = Notification.objects.filter(user=request.user, is_read=False).count()
        except Exception:
            unread_notifications = 0

    can_access_hostel = False
    student_profile = None
    assigned_hostel = None

    if request.user.is_authenticated:
        if request.user.is_superuser or getattr(request.user, 'role', '') in [User.Role.SUPER_ADMIN, User.Role.COLLEGE_ADMIN]:
            can_access_hostel = True
        elif getattr(request.user, 'role', '') in [User.Role.STUDENT, User.Role.CLUB_MEMBER]:
            student_profile = getattr(request.user, 'student_profile', None)
            if student_profile and getattr(student_profile, 'accommodation_type', '') in ['hostel', 'HOSTEL']:
                can_access_hostel = True
                assigned_hostel = getattr(student_profile, 'assigned_hostel', None)

    return {
        'CAMPUS_NAME': settings.CAMPUS_NAME,
        'CAMPUS_SHORT_NAME': getattr(settings, 'CAMPUS_SHORT_NAME', 'CIT'),
        'CAMPUS_LAT': settings.CAMPUS_LAT,
        'CAMPUS_LNG': settings.CAMPUS_LNG,
        'CAMPUS_CONFIG': CAMPUS_CONFIG,
        'CAMPUS_CONFIG_JSON': json.dumps(CAMPUS_CONFIG),
        'current_weather': WeatherService.get_current_weather(),
        'unread_notifications_count': unread_notifications,
        'ROLES': User.Role,
        'can_access_hostel': can_access_hostel,
        'student_profile': student_profile,
        'assigned_hostel': assigned_hostel,
        'DATA_MODE': getattr(settings, 'DATA_MODE', 'DEMO'),
    }

