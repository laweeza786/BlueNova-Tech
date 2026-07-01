from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

def admin_required(view_func):
    """
    Decorator for views that checks that the user is logged in and is an administrator,
    redirecting to the 404 page if they don't have access.
    """
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.role == 'admin':
            return view_func(request, *args, **kwargs)
        # Redirect standard users to 404 or dashboard
        return redirect('page_404')
    return _wrapped_view

def intern_required(view_func):
    """
    Decorator for views that checks that the user is logged in and is an intern,
    redirecting to the 404 page if they don't have access.
    """
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.role == 'user':
            return view_func(request, *args, **kwargs)
        # Redirect admins to admin dashboard
        return redirect('admin_dashboard')
    return _wrapped_view
