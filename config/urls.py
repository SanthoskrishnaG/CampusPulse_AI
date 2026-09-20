"""
CampusPulse AI - Root URL Configuration
Unified routing across all 14 campus domains and REST APIs.
"""

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from apps.common import views as common_views

urlpatterns = [
    # Administrative Core
    path('admin/', admin.site.urls),
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),

    # Public Landing, Geo Map & System Audit
    path('', include('apps.common.urls', namespace='common')),
    path('common/map/', common_views.map_view, name='common_map_direct'),

    # Core Academic & Institutional Domains
    path('departments/', include('apps.departments.urls', namespace='departments')),
    path('faculty/', include('apps.faculty.urls', namespace='faculty')),
    path('students/', include('apps.students.urls', namespace='students')),
    path('academics/', include('apps.academics.urls', namespace='academics')),

    # Student Engagement & Co-Curricular
    path('clubs/', include('apps.clubs.urls', namespace='clubs')),
    path('events/', include('apps.events.urls', namespace='events')),
    path('projects/', include('apps.projects.urls', namespace='projects')),
    path('recommendations/', include('apps.recommendations.urls', namespace='recommendations')),

    # Smart Campus Operations
    path('complaints/', include('apps.complaints.urls', namespace='complaints')),
    path('transport/', include('apps.transport.urls', namespace='transport')),
    path('traffic/', include('apps.traffic.urls', namespace='traffic')),
    path('parking/', include('apps.parking.urls', namespace='parking')),
    path('canteen/', include('apps.canteen.urls', namespace='canteen')),
    path('energy/', include('apps.energy.urls', namespace='energy')),
    path('waste/', include('apps.waste.urls', namespace='waste')),
    path('hostel/', include('apps.hostel.urls', namespace='hostel')),
    path('api/hostel/', include('apps.hostel.api_urls')),
    path('api/ml/', include('apps.analytics.api_urls')),

    # AI Intelligence & Notification
    path('assistant/', include('apps.ai_assistant.urls', namespace='ai_assistant')),
    path('notifications/', include('apps.notifications.urls', namespace='notifications')),
    path('analytics/', include('apps.analytics.urls', namespace='analytics')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
else:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]
