from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notification_list, name='list'),
    path('api/unread-count/', views.unread_count_api, name='api_unread_count'),
    path('api/list/', views.notification_list_api, name='api_list'),
    path('<int:pk>/read/', views.mark_notification_read, name='mark_read'),
    path('mark-all-read/', views.mark_all_notifications_read, name='mark_all_read'),
]
