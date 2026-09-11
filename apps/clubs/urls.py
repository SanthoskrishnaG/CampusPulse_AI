from django.urls import path
from . import views

app_name = 'clubs'

urlpatterns = [
    path('', views.club_list, name='list'),
    path('dashboard/', views.club_dashboard, name='dashboard'),
    path('<str:code>/', views.club_detail, name='detail'),
    path('<str:code>/join/', views.join_club, name='join'),
]
