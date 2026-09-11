from django.urls import path
from . import views

app_name = 'canteen'

urlpatterns = [
    path('dashboard/', views.canteen_dashboard, name='dashboard'),
    path('record-sales/', views.record_meal_sales, name='record_sales'),
]
