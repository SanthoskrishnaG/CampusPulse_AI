from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from .forms import CampusLoginForm, UserProfileForm
from .models import User

def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:role_redirect')

    if request.method == 'POST':
        form = CampusLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # Log audit event
            from apps.common.models import AuditLog
            AuditLog.log_action(user, "USER_LOGIN", f"User {user.username} logged in from {request.META.get('REMOTE_ADDR')}")
            messages.success(request, f"Welcome back, {user.get_full_name() or user.username} ({user.get_role_display()})!")
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('accounts:role_redirect')
        else:
            messages.error(request, "Invalid credentials. Please verify your username and password.")
    else:
        form = CampusLoginForm()

    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    if request.user.is_authenticated:
        from apps.common.models import AuditLog
        AuditLog.log_action(request.user, "USER_LOGOUT", f"User {request.user.username} logged out")
        logout(request)
        messages.info(request, "You have been securely logged out from CampusPulse.")
    return redirect('common:home')

@login_required
def role_redirect_view(request):
    """
    Intelligent role-based redirect routing users to their dedicated dashboard.
    """
    user = request.user
    role = user.role

    if user.is_superuser or role in [User.Role.SUPER_ADMIN, User.Role.COLLEGE_ADMIN]:
        return redirect('analytics:dashboard')
    elif role == User.Role.DEPARTMENT_ADMIN:
        return redirect('departments:dashboard')
    elif role == User.Role.FACULTY:
        return redirect('faculty:dashboard')
    elif role in [User.Role.STUDENT, User.Role.CLUB_MEMBER]:
        return redirect('students:dashboard')
    elif role == User.Role.CLUB_ADMIN:
        return redirect('clubs:dashboard')
    elif role == User.Role.TRANSPORT_MANAGER:
        return redirect('transport:dashboard')
    elif role == User.Role.CANTEEN_MANAGER:
        return redirect('canteen:dashboard')
    elif role in [User.Role.MAINTENANCE_STAFF, User.Role.FACILITY_MANAGER]:
        return redirect('complaints:dashboard')
    elif role == User.Role.SECURITY_STAFF:
        return redirect('traffic:dashboard')
    else:
        return redirect('analytics:dashboard')

@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile was successfully updated.")
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'accounts/profile.html', {'form': form})

def demo_login(request, role_name):
    """
    Demo switcher for viva / examiner demonstrations to quickly test different RBAC perspectives.
    """
    matching_user = User.objects.filter(role=role_name).first()
    if matching_user:
        login(request, matching_user)
        messages.success(request, f"Switched perspective to {matching_user.username} ({matching_user.get_role_display()})")
        return redirect('accounts:role_redirect')
    else:
        messages.warning(request, f"No demo user found with role {role_name}. Please seed demo data.")
        return redirect('accounts:login')
