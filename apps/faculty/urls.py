from django.urls import path
from . import views

app_name = 'faculty'

urlpatterns = [
    path('', views.faculty_list, name='list'),
    path('dashboard/', views.faculty_dashboard, name='dashboard'),
    path('<int:pk>/', views.faculty_detail, name='detail'),
]
