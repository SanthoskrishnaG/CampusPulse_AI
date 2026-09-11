from django.urls import path
from . import views

app_name = 'ai_assistant'

urlpatterns = [
    path('', views.assistant_page, name='chat'),
    path('api/query/', views.assistant_query_api, name='api_query'),
]
