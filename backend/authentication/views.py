from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from .models import User
from core.models import Profile, Setting, History, ActivityLog

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def log_action(user, action, request):
    ActivityLog.objects.create(
        user=user,
        action=action,
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )

@csrf_protect
def login_view(request):
    if request.user.is_authenticated:
        if request.user.role == 'admin':
            return redirect('admin_dashboard')
        return redirect('dashboard')

    if request.method == 'POST':
        username_val = request.POST.get('username', '').strip().lower()
        password_val = request.POST.get('password', '')
        
        user = authenticate(request, username=username_val, password=password_val)
        if user is not None:
            auth_login(request, user)
            log_action(user, "User logged in", request)
            
            # Persist custom theme setting in session
            try:
                setting = Setting.objects.get(user=user)
                request.session['theme'] = setting.theme
            except Setting.DoesNotExist:
                Setting.objects.create(user=user)
                request.session['theme'] = 'dark'
                
            if user.role == 'admin':
                return JsonResponse({'success': True, 'redirect': 'admin_dashboard'})
            return JsonResponse({'success': True, 'redirect': 'dashboard'})
        else:
            return JsonResponse({'success': False, 'message': 'Invalid username or password.'}, status=400)

    return render(request, 'login.html')


@csrf_protect
def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip().lower()
        email = request.POST.get('email', '').strip()
        fullname = request.POST.get('fullname', '').strip()
        track = request.POST.get('track', '')
        academic = request.POST.get('academic', '').strip()
        bio = request.POST.get('bio', '').strip()
        password = request.POST.get('password', '')
        
        if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
            return JsonResponse({'success': False, 'message': 'Username or email already exists.'}, status=400)
            
        # Standard Intern user creation (admin is prohibited through frontend signup)
        user = User.objects.create_user(username=username, email=email, password=password, role='user')
        
        # Build Profile & Settings
        Profile.objects.create(
            user=user,
            full_name=fullname,
            track=track,
            academic_background=academic,
            bio=bio,
            status='pending'
        )
        Setting.objects.create(user=user, theme='dark')
        
        # Create initial history log
        History.objects.create(
            user=user,
            milestone_name="Application Submitted",
            description="Your internship request has been successfully filed in the recruitment panel."
        )
        
        log_action(user, "User signed up", request)
        return JsonResponse({'success': True, 'message': 'Signup successful! Redirecting...'})

    return render(request, 'signup.html')


@login_required
def logout_view(request):
    log_action(request.user, "User logged out", request)
    auth_logout(request)
    return redirect('login')


@csrf_protect
def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        user_exists = User.objects.filter(email=email).exists()
        if user_exists:
            return JsonResponse({'success': True, 'message': 'Password recovery instructions sent to your email.'})
        return JsonResponse({'success': False, 'message': 'Email address not found in system.'}, status=400)
    return render(request, 'forgot-password.html')


@csrf_protect
def reset_password_view(request):
    if request.method == 'POST':
        # Simulate reset password since it's a mock workflow in frontend
        # In real system, this would accept token/uidb64, but since it's ERP flow we process it
        return JsonResponse({'success': True, 'message': 'Password reset successful!'})
    return render(request, 'reset-password.html')
