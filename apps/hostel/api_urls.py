from django.urls import path
from . import views

urlpatterns = [
    path('', views.api_hostel_root, name='hostel_api_root'),
    path('facilities/', views.api_hostel_facilities, name='hostel_api_facilities'),
    path('rooms/', views.api_hostel_rooms, name='hostel_api_rooms'),
    path('routes/', views.api_hostel_routes, name='hostel_api_routes'),
    path('complaints/', views.api_hostel_complaints, name='hostel_api_complaints'),
    path('maintenance/', views.api_hostel_maintenance, name='hostel_api_maintenance'),
    path('<str:hostel_code>/', views.api_hostel_details, name='hostel_api_details'),
    path('<str:hostel_code>/route/', views.api_hostel_route, name='hostel_api_route'),
]
