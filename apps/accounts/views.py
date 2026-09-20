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
        student_profile = getattr(user, 'student_profile', None)
        # If student has not yet completed accommodation setup, route to onboarding wizard
        if student_profile and not student_profile.is_accommodation_configured:
            return redirect('accounts:accommodation_setup')
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
def accommodation_setup_view(request):
    """
    Student-Only Accommodation Setup & Onboarding Wizard.
    Strictly restricted from Faculty users.
    """
    user = request.user
    # Faculty members must never be asked accommodation questions
    if user.role == User.Role.FACULTY:
        messages.info(request, "Faculty accounts are not eligible for student residential accommodations.")
        return redirect('faculty:dashboard')

    if user.role not in [User.Role.STUDENT, User.Role.CLUB_MEMBER] and not user.is_superuser:
        return redirect('accounts:role_redirect')

    student_profile = getattr(user, 'student_profile', None)
    if not student_profile:
        messages.warning(request, "Student record not associated with this account.")
        return redirect('students:dashboard')

    from apps.hostel.models import Hostel

    if request.method == 'POST':
        accom_type = request.POST.get('accommodation_type')
        if accom_type == 'day_scholar':
            student_profile.accommodation_type = 'day_scholar'
            student_profile.hostel_category = None
            student_profile.assigned_hostel = None
            student_profile.room_number = ''
            student_profile.is_accommodation_configured = True
            student_profile.save()
            messages.success(request, "Campus profile updated: Registered as Day Scholar. Access to academic facilities is active.")
            return redirect('students:dashboard')
        elif accom_type == 'hostel':
            category = request.POST.get('hostel_category')
            hostel_id = request.POST.get('assigned_hostel')
            room_number = request.POST.get('room_number', '').strip()

            if not category or not hostel_id:
                messages.error(request, "Please select both your hostel category and specific assigned building.")
            else:
                hostel = Hostel.objects.filter(id=hostel_id, category=category).first()
                if not hostel:
                    messages.error(request, "Invalid hostel selection for the chosen category.")
                else:
                    student_profile.accommodation_type = 'hostel'
                    student_profile.hostel_category = category
                    student_profile.assigned_hostel = hostel
                    student_profile.room_number = room_number or f"{hostel.code}-101"
                    student_profile.is_accommodation_configured = True
                    student_profile.save()
                    messages.success(request, f"Welcome to {hostel.name}! Your room ({student_profile.room_number}) and Hostel Facilities are now unlocked.")
                    return redirect('students:dashboard')

    boys_hostels = Hostel.objects.filter(category=Hostel.Category.BOYS, is_active=True)
    girls_hostels = Hostel.objects.filter(category=Hostel.Category.GIRLS, is_active=True)

    return render(request, 'accounts/accommodation_setup.html', {
        'student': student_profile,
        'boys_hostels': boys_hostels,
        'girls_hostels': girls_hostels,
    })

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
