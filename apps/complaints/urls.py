from django.urls import path
from . import views

app_name = 'complaints'

urlpatterns = [
    path('', views.complaint_list, name='list'),
    path('submit/', views.submit_complaint, name='submit'),
    path('dashboard/', views.complaint_dashboard, name='dashboard'),
    path('<int:pk>/', views.complaint_detail, name='detail'),
    path('<int:pk>/update-status/', views.update_complaint_status, name='update_status'),
]
