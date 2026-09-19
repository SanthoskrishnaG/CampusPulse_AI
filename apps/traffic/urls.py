from django.urls import path
from . import views

app_name = 'traffic'

urlpatterns = [
    path('', views.traffic_dashboard, name='index'),
    path('dashboard/', views.traffic_dashboard, name='dashboard'),
    path('analyze/', views.analyze_traffic_feed, name='analyze'),
]
