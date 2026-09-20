from django.urls import path
from . import api_views

urlpatterns = [
    # Inference Endpoints
    path('academic-risk/predict/', api_views.api_academic_risk_predict, name='api_academic_risk_predict'),
    path('canteen/demand/', api_views.api_canteen_demand_forecast, name='api_canteen_demand_forecast'),
    path('canteen/waste/predict/', api_views.api_food_waste_predict, name='api_food_waste_predict'),
    path('hostel/mess/demand/', api_views.api_hostel_mess_demand, name='api_hostel_mess_demand'),
    path('complaints/classify/', api_views.api_complaint_classify, name='api_complaint_classify'),
    path('complaints/check-duplicate/', api_views.api_complaint_check_duplicate, name='api_complaint_check_duplicate'),
    path('energy/detect/', api_views.api_energy_detect_anomaly, name='api_energy_detect_anomaly'),
    path('transport/eta/<int:bus_id>/', api_views.api_transport_eta, name='api_transport_eta'),
    path('parking/predict/<str:lot_code>/', api_views.api_parking_occupancy, name='api_parking_occupancy'),

    # Feedback & Monitoring
    path('feedback/submit/', api_views.api_submit_feedback, name='api_submit_feedback'),
    path('monitoring/metrics/', api_views.api_monitoring_metrics, name='api_monitoring_metrics'),
]
