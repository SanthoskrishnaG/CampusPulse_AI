from django.urls import path
from . import views

app_name = 'hostel'

urlpatterns = [
    # Resident Portal
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard_direct'),
    path('facilities/', views.facilities_view, name='facilities'),
    path('rooms/', views.rooms_view, name='rooms'),
    path('complaints/', views.complaints_view, name='complaints'),
    path('maintenance/', views.maintenance_view, name='maintenance'),
    path('mess/', views.mess_view, name='mess'),
    path('announcements/', views.announcements_view, name='announcements'),
    path('attendance/', views.attendance_view, name='attendance'),
    path('route/', views.route_view, name='route'),
    path('routes/', views.route_view, name='routes'),
    path('events/', views.events_view, name='events'),
    path('emergency/', views.emergency_view, name='emergency'),

    # Admin Oversight
    path('analytics/', views.admin_analytics_view, name='admin_analytics'),
    path('admin-analytics/', views.admin_analytics_view, name='admin_analytics_alias'),
    path('admin/analytics/', views.admin_analytics_view, name='admin_analytics_nested'),

    # Protected REST APIs
    path('api/', views.api_hostel_root, name='api_root'),
    path('api/facilities/', views.api_hostel_facilities, name='api_facilities'),
    path('api/rooms/', views.api_hostel_rooms, name='api_rooms'),
    path('api/routes/', views.api_hostel_routes, name='api_routes'),
    path('api/complaints/', views.api_hostel_complaints, name='api_complaints'),
    path('api/maintenance/', views.api_hostel_maintenance, name='api_maintenance'),
    path('api/<str:hostel_code>/', views.api_hostel_details, name='api_details'),
    path('api/<str:hostel_code>/route/', views.api_hostel_route, name='api_route'),
]
