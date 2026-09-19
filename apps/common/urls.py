from django.urls import path
from . import views

app_name = 'common'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('map/', views.map_view, name='map'),
    path('api/map-locations/', views.map_locations_api, name='api_map_locations'),
    path('api/campus-config/', views.campus_config_api, name='api_campus_config'),
    path('api/simulation-control/', views.simulation_control_api, name='api_simulation_control'),
    path('api/global-search/', views.global_search_api, name='api_global_search'),
    path('audit-logs/', views.audit_log_view, name='audit_logs'),
]
