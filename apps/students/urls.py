from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    path('', views.student_list, name='list'),
    path('dashboard/', views.student_dashboard, name='dashboard'),
    path('import-csv/', views.import_csv_view, name='import_csv'),
    path('<str:student_id>/', views.student_detail, name='detail'),
]
