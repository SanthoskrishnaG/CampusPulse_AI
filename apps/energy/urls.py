from django.urls import path
from . import views

app_name = 'energy'

urlpatterns = [
    path('dashboard/', views.energy_dashboard, name='dashboard'),
    path('api/scan/', views.trigger_energy_scan, name='api_scan'),
]
