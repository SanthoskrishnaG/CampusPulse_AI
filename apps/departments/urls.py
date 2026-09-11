from django.urls import path
from . import views

app_name = 'departments'

urlpatterns = [
    path('', views.department_list, name='list'),
    path('dashboard/', views.department_dashboard, name='dashboard'),
    path('<str:code>/', views.department_detail, name='detail'),
]
