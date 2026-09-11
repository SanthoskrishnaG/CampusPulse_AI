from django.urls import path
from . import views

app_name = 'waste'

urlpatterns = [
    path('dashboard/', views.waste_dashboard, name='dashboard'),
    path('classify/', views.classify_waste_image, name='classify'),
]
