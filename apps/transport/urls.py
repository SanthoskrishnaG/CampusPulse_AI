from django.urls import path
from . import views

app_name = 'transport'

urlpatterns = [
    path('', views.route_list, name='routes'),
    path('dashboard/', views.transport_dashboard, name='dashboard'),
    path('api/live-telemetry/', views.live_telemetry_api, name='api_live_telemetry'),
]
