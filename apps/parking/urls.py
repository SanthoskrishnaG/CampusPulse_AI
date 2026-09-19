from django.urls import path
from . import views

app_name = 'parking'

urlpatterns = [
    path('', views.parking_dashboard, name='index'),
    path('dashboard/', views.parking_dashboard, name='dashboard'),
    path('api/telemetry/', views.parking_telemetry_api, name='api_telemetry'),
    path('api/toggle-slot/<int:slot_id>/', views.toggle_slot_api, name='api_toggle_slot'),
]
