from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied

def role_required(*allowed_roles):
    """
    Decorator to restrict view access to specific RBAC roles.
    Superusers always pass.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            
            if request.user.is_superuser or request.user.role == 'SUPER_ADMIN':
                return view_func(request, *args, **kwargs)
                
            if request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
                
            messages.error(request, "You do not have permission to access that administrative resource.")
            return redirect('accounts:role_redirect')
        return _wrapped_view
    return decorator
