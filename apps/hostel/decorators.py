from functools import wraps
from django.shortcuts import render, redirect
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib import messages
from apps.accounts.models import User

def hostel_access_required(view_func):
    """
    Strict backend authorization decorator ensuring only authorized hostel residents
    or campus administrators can access hostel endpoints.
    Denies Day Scholars, Faculty, and unauthenticated users with 403 Forbidden.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        is_api = (
            request.headers.get('x-requested-with') == 'XMLHttpRequest' or
            request.path.startswith('/api/') or
            request.path.startswith('/hostel/api/') or
            'application/json' in request.headers.get('Accept', '')
        )

        if not request.user.is_authenticated:
            if is_api:
                return JsonResponse({'error': 'Unauthorized', 'detail': 'Authentication required'}, status=401)
            return redirect('accounts:login')

        user = request.user

        # Administrators always have operational oversight
        if user.is_superuser or user.role in [User.Role.SUPER_ADMIN, User.Role.COLLEGE_ADMIN]:
            return view_func(request, *args, **kwargs)

        # Faculty members are strictly barred from student residential quarters
        if user.role == User.Role.FACULTY:
            if is_api:
                return JsonResponse({
                    'error': 'Forbidden',
                    'detail': 'Hostel facilities are restricted to authorized hostel students.'
                }, status=403)
            return render(request, 'hostel/access_denied.html', {
                'reason': 'Faculty accounts do not have access to student residential hostel facilities.'
            }, status=403)

        # Students must have active hostel accommodation
        if user.role in [User.Role.STUDENT, User.Role.CLUB_MEMBER]:
            student_profile = getattr(user, 'student_profile', None)
            if not student_profile:
                if is_api:
                    return JsonResponse({'error': 'Forbidden', 'detail': 'Student profile not found.'}, status=403)
                return render(request, 'hostel/access_denied.html', {
                    'reason': 'Student profile not found. Please contact administration.'
                }, status=403)

            # Check accommodation type
            if student_profile.accommodation_type != 'hostel':
                if is_api:
                    return JsonResponse({
                        'error': 'Forbidden',
                        'detail': 'Hostel facilities are available only to authorized hostel students.'
                    }, status=403)
                return render(request, 'hostel/access_denied.html', {
                    'reason': 'You are registered as a Day Scholar. Hostel facilities are restricted to authorized hostel students.'
                }, status=403)

            # Check hostel category alignment if a specific hostel is targeted
            target_hostel_code = kwargs.get('hostel_code') or request.GET.get('hostel')
            if target_hostel_code and student_profile.hostel_category:
                from .models import Hostel
                target_hostel = Hostel.objects.filter(code__iexact=target_hostel_code).first()
                if target_hostel and target_hostel.category != student_profile.hostel_category:
                    if is_api:
                        return JsonResponse({
                            'error': 'Forbidden',
                            'detail': f'Access denied: You cannot access {target_hostel.name} facilities.'
                        }, status=403)
                    return render(request, 'hostel/access_denied.html', {
                        'reason': f'Access restricted: Resident of {student_profile.get_hostel_category_display()} cannot access {target_hostel.name}.'
                    }, status=403)

            return view_func(request, *args, **kwargs)

        # All other roles (Transport, Canteen, etc.)
        if is_api:
            return JsonResponse({
                'error': 'Forbidden',
                'detail': 'You do not have permission to access hostel facilities.'
            }, status=403)
        return render(request, 'hostel/access_denied.html', {
            'reason': 'You do not have permission to access hostel facilities.'
        }, status=403)

    return _wrapped_view
