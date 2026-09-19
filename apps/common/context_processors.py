import json
from django.conf import settings
from .weather import WeatherService
from apps.accounts.models import User

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

    campus_config = getattr(settings, 'CAMPUS_CONFIG', {})

    return {
        'CAMPUS_NAME': settings.CAMPUS_NAME,
        'CAMPUS_SHORT_NAME': getattr(settings, 'CAMPUS_SHORT_NAME', 'CIT'),
        'CAMPUS_LAT': settings.CAMPUS_LAT,
        'CAMPUS_LNG': settings.CAMPUS_LNG,
        'CAMPUS_CONFIG': campus_config,
        'CAMPUS_CONFIG_JSON': json.dumps(campus_config),
        'current_weather': WeatherService.get_current_weather(),
        'unread_notifications_count': unread_notifications,
        'ROLES': User.Role,
    }

