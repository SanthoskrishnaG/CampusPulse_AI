from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('dashboard/', views.command_center_dashboard, name='dashboard'),
    path('model-registry/', views.model_registry_view, name='model_registry'),
    path('model-registry/retrain/<str:model_name>/', views.trigger_model_retrain_api, name='retrain_model'),
]
