from django.urls import path
from . import views

app_name = 'academics'

urlpatterns = [
    path('courses/', views.course_list, name='courses'),
    path('risk-dashboard/', views.risk_dashboard, name='risk_dashboard'),
    path('api/run-assessment/', views.run_risk_assessment_api, name='api_run_assessment'),
    path('intervention/create/<str:student_id>/', views.create_intervention, name='create_intervention'),
]
