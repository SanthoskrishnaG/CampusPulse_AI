from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('', views.project_list, name='list'),
    path('create/', views.create_project, name='create'),
    path('<int:pk>/', views.project_detail, name='detail'),
]
