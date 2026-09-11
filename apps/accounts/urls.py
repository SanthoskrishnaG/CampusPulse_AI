from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('redirect/', views.role_redirect_view, name='role_redirect'),
    path('profile/', views.profile_view, name='profile'),
    path('demo-login/<str:role_name>/', views.demo_login, name='demo_login'),
]
