import csv
import io
import os
import json
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.core.serializers.json import DjangoJSONEncoder
from authentication.views import log_action
from .models import Profile, UploadedFile, Notification, Message, ActivityLog, Feedback, Setting, History, Report, InternshipApplication, LMSCourse, LMSModule, Lecture, LectureProgress, LectureResource, StudentNote, Bookmark, Assignment, AssignmentSubmission, Quiz, QuizQuestion, QuizAnswer, Certificate, Enrollment
from .decorators import admin_required, intern_required

User = get_user_model()

def get_erp_context(request):
    if not request.user.is_authenticated:
        return {}
    
    # Query all users
    users_list = []
    for u in User.objects.all():
        try:
            p = u.profile
            track = p.track
            status = p.status
            full_name = p.full_name
            phone = p.phone
            bio = p.bio
            academic_background = p.academic_background
            skills = p.skills
            avatar = p.profile_picture.url if p.profile_picture else "/media/profile_pictures/default-avatar.png"
        except Profile.DoesNotExist:
            track = ""
            status = "approved" if u.role == 'admin' else "pending"
            full_name = u.username
            phone = ""
            bio = ""
            academic_background = ""
            skills = ""
            avatar = "/media/profile_pictures/default-avatar.png"
            
        users_list.append({
            'id': u.id,
            'username': u.username,
            'email': u.email,
            'role': u.role,
            'token': f"session-token-{u.username}",
            'track': track,
            'status': status,
            'full_name': full_name,
            'phone': phone,
            'bio': bio,
            'academic_background': academic_background,
            'skills': skills,
            'avatar': avatar,
            'resume': ""
        })
        
    # Query files
    files_list = []
    files_query = UploadedFile.objects.all() if request.user.role == 'admin' else UploadedFile.objects.filter(user=request.user)
    for f in files_query:
        files_list.append({
            'id': f.id,
            'user_id': f.user.id,
            'file_name': f.file_name,
            'file_size': f.file_size,
            'file_type': f.file_type,
            'uploaded_at': f.uploaded_at.isoformat(),
            'file_url': f.file.url,
            'uploaded_by': f.user.profile.full_name if hasattr(f.user, 'profile') and f.user.profile.full_name else f.user.username
        })
        
    # Query notifications
    notif_list = []
    notif_query = Notification.objects.all() if request.user.role == 'admin' else Notification.objects.filter(user=request.user)
    for n in notif_query:
        notif_list.append({
            'id': n.id,
            'user_id': n.user.id,
            'title': n.title,
            'message': n.message,
            'level': n.level,
            'is_read': n.is_read,
            'created_at': n.created_at.isoformat()
        })
        
    # Query messages
    msg_list = []
    msg_query = Message.objects.all()
    for m in msg_query:
        msg_list.append({
            'id': m.id,
            'sender_id': m.sender.id,
            'receiver_id': m.receiver.id,
            'subject': m.subject,
            'body': m.body,
            'is_read': m.is_read,
            'created_at': m.created_at.isoformat()
        })
        
    # Query logs
    logs_list = []
    logs_query = ActivityLog.objects.all() if request.user.role == 'admin' else ActivityLog.objects.filter(user=request.user)
    for l in logs_query:
        logs_list.append({
            'id': l.id,
            'user_id': l.user.id if l.user else None,
            'action': l.action,
            'ip_address': l.ip_address,
            'user_agent': l.user_agent,
            'timestamp': l.timestamp.isoformat()
        })
        
    # Query milestones history
    hist_list = []
    hist_query = History.objects.all() if request.user.role == 'admin' else History.objects.filter(user=request.user)
    for h in hist_query:
        hist_list.append({
            'id': h.id,
            'user_id': h.user.id,
            'milestone_name': h.milestone_name,
            'description': h.description,
            'achieved_at': h.achieved_at.isoformat()
        })

    return {
        'json_users': json.dumps(users_list, cls=DjangoJSONEncoder),
        'json_files': json.dumps(files_list, cls=DjangoJSONEncoder),
        'json_notifications': json.dumps(notif_list, cls=DjangoJSONEncoder),
        'json_messages': json.dumps(msg_list, cls=DjangoJSONEncoder),
        'json_logs': json.dumps(logs_list, cls=DjangoJSONEncoder),
        'json_history': json.dumps(hist_list, cls=DjangoJSONEncoder),
        'session_token': f"session-token-{request.user.username}"
    }


@login_required
def dashboard(request):
    if request.user.role == 'admin':
        return redirect('admin_dashboard')
        
    profile = get_object_or_404(Profile, user=request.user)
    files = UploadedFile.objects.filter(user=request.user).order_by('-uploaded_at')
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    logs = ActivityLog.objects.filter(user=request.user).order_by('-timestamp')[:5]
    
    context = {
        'profile': profile,
        'files_count': files.count(),
        'notif_count': notifications.filter(is_read=False).count(),
        'recent_logs': logs,
    }
    context.update(get_erp_context(request))
    return render(request, 'dashboard.html', context)


@login_required
@admin_required
def admin_dashboard(request):
    users = User.objects.filter(role='user').select_related('profile')
    files_count = UploadedFile.objects.count()
    logs_count = ActivityLog.objects.count()
    
    pending_users = users.filter(profile__status='pending')
    
    # Cohort demographics for charts
    se_count = users.filter(profile__track='Software Engineering').count()
    ui_count = users.filter(profile__track='UI/UX Design').count()
    da_count = users.filter(profile__track='Data Analytics').count()
    
    context = {
        'total_interns': users.count(),
        'pending_count': pending_users.count(),
        'uploads_count': files_count,
        'logs_count': logs_count,
        'recent_users': users.order_by('-date_joined')[:5],
        'se_count': se_count,
        'ui_count': ui_count,
        'da_count': da_count,
    }
    context.update(get_erp_context(request))
    return render(request, 'admin-dashboard.html', context)


@login_required
@admin_required
def user_management(request):
    users = User.objects.filter(role='user').select_related('profile').order_by('-id')
    context = {'users': users}
    context.update(get_erp_context(request))
    return render(request, 'user-management.html', context)


@login_required
@csrf_protect
def upload_file(request):
    if request.method == 'POST':
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return JsonResponse({'success': False, 'message': 'No file uploaded.'}, status=400)
            
        ext = os.path.splitext(uploaded_file.name)[1].lower().replace('.', '')
        allowed_types = ['pdf', 'docx', 'zip', 'png', 'jpg', 'jpeg']
        if ext not in allowed_types:
            return JsonResponse({'success': False, 'message': f'Extension .{ext} is not allowed.'}, status=400)
            
        if uploaded_file.size > 10485760:
            return JsonResponse({'success': False, 'message': 'File is too large. Limit is 10MB.'}, status=400)
            
        new_file = UploadedFile.objects.create(
            user=request.user,
            file=uploaded_file,
            file_name=uploaded_file.name,
            file_size=uploaded_file.size,
            file_type=ext
        )
        
        log_action(request.user, f"Uploaded document {uploaded_file.name}", request)
        return JsonResponse({
            'success': True,
            'message': f'File {uploaded_file.name} uploaded successfully.',
            'file': {
                'id': new_file.id,
                'user_id': new_file.user.id,
                'file_name': new_file.file_name,
                'file_size': new_file.file_size,
                'file_type': new_file.file_type,
                'uploaded_at': new_file.uploaded_at.isoformat(),
                'file_url': new_file.file.url,
                'uploaded_by': new_file.user.profile.full_name if hasattr(new_file.user, 'profile') and new_file.user.profile.full_name else new_file.user.username
            }
        })
        
    context = {}
    context.update(get_erp_context(request))
    return render(request, 'upload-files.html', context)


@login_required
def delete_file(request, file_id):
    file_obj = get_object_or_404(UploadedFile, id=file_id)
    if file_obj.user == request.user or request.user.role == 'admin':
        file_name = file_obj.file_name
        file_obj.file.delete()
        file_obj.delete()
        log_action(request.user, f"Deleted document {file_name}", request)
        return JsonResponse({'success': True, 'message': 'File deleted successfully.'})
    return JsonResponse({'success': False, 'message': 'Permission Denied.'}, status=403)


@login_required
def messages_view(request):
    if request.user.role == 'admin':
        contacts = User.objects.filter(role='user').select_related('profile')
    else:
        contacts = User.objects.filter(role='admin')
    
    context = {'contacts': contacts}
    context.update(get_erp_context(request))
    return render(request, 'messages.html', context)


@login_required
def profile_view(request, user_id=None):
    if user_id and request.user.role == 'admin':
        profile_user = get_object_or_404(User, id=user_id)
    else:
        profile_user = request.user
        
    profile = get_object_or_404(Profile, user=profile_user)
    context = {'profile': profile}
    context.update(get_erp_context(request))
    return render(request, 'profile.html', context)


@login_required
@csrf_protect
def edit_profile_view(request):
    profile = get_object_or_404(Profile, user=request.user)
    if request.method == 'POST':
        profile.full_name = request.POST.get('fullname', '')
        profile.phone = request.POST.get('phone', '')
        profile.bio = request.POST.get('bio', '')
        profile.skills = request.POST.get('skills', '')
        profile.academic_background = request.POST.get('academic', '')
        if 'track' in request.POST:
            profile.track = request.POST.get('track', '')
            
        profile.save()
        messages.success(request, "Profile updated successfully.")
        log_action(request.user, "Updated profile metrics", request)
        return JsonResponse({'success': True, 'message': 'Profile updated successfully.'})
        
    context = {'profile': profile}
    context.update(get_erp_context(request))
    return render(request, 'edit-profile.html', context)


@login_required
def notifications_view(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    notifications.update(is_read=True)
    context = {'notifications': notifications}
    context.update(get_erp_context(request))
    return render(request, 'notifications.html', context)


@login_required
def delete_notification(request, notif_id):
    notif = get_object_or_404(Notification, id=notif_id, user=request.user)
    notif.delete()
    return JsonResponse({'success': True, 'message': 'Alert cleared.'})


@login_required
@admin_required
def activity_logs_view(request):
    logs = ActivityLog.objects.select_related('user').order_by('-timestamp')
    context = {'logs': logs}
    context.update(get_erp_context(request))
    return render(request, 'activity-logs.html', context)


@login_required
@admin_required
def data_management_view(request):
    context = {}
    context.update(get_erp_context(request))
    return render(request, 'data-management.html', context)


@login_required
@admin_required
@csrf_protect
def reset_database_view(request):
    if request.method == 'POST':
        UploadedFile.objects.all().delete()
        Notification.objects.all().delete()
        Message.objects.all().delete()
        Feedback.objects.all().delete()
        History.objects.all().delete()
        User.objects.filter(role='user').delete()
        
        log_action(request.user, "System database successfully reset", request)
        return JsonResponse({'success': True, 'message': 'Factory reset executed successfully.'})
    return redirect('data_management')


@login_required
def reports_view(request):
    context = {}
    context.update(get_erp_context(request))
    return render(request, 'reports.html', context)


@login_required
def export_csv_view(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="bluenova_candidates_report.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['ID', 'Username', 'Email', 'Full Name', 'Track', 'Academic Background', 'Status'])
    
    users = User.objects.filter(role='user').select_related('profile')
    for u in users:
        p = u.profile
        writer.writerow([u.id, u.username, u.email, p.full_name, p.track, p.academic_background, p.status])
        
    return response


@login_required
def export_pdf_view(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="bluenova_milestones_report.pdf"'
    
    pdf_buffer = io.BytesIO()
    pdf_buffer.write(b"%PDF-1.4\n")
    pdf_buffer.write(b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")
    pdf_buffer.write(b"2 0 obj\n<< /Type /Pages /Kids [ 3 0 R ] /Count 1 >>\nendobj\n")
    pdf_buffer.write(b"3 0 obj\n<< /Type /Page /Parent 2 0 R /Resources << >> /Contents 4 0 R >>\nendobj\n")
    pdf_buffer.write(b"4 0 obj\n<< /Length 120 >>\nstream\n")
    pdf_buffer.write(b"BT\n/F1 12 Tf\n20 700 Td\n(BlueNova Technologies - Milestones Report) Tj\n")
    pdf_buffer.write(b"0 -20 Td\n(Verified Credentials & Accomplishments) Tj\nET\n")
    pdf_buffer.write(b"endstream\nendobj\n")
    pdf_buffer.write(b"xref\n0 5\n0000000000 65535 f\n0000000009 00000 n\n0000000062 00000 n\n0000000119 00000 n\n0000000192 00000 n\n")
    pdf_buffer.write(b"trailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n362\n%%EOF\n")
    
    response.write(pdf_buffer.getvalue())
    return response


@login_required
def analytics_view(request):
    context = {}
    context.update(get_erp_context(request))
    return render(request, 'analytics.html', context)


@login_required
def search_view(request):
    q = request.GET.get('q', '').strip()
    users_matches = []
    files_matches = []
    
    if q:
        users_matches = User.objects.filter(role='user', username__icontains=q) | User.objects.filter(role='user', profile__full_name__icontains=q)
        files_matches = UploadedFile.objects.filter(file_name__icontains=q)
        
    context = {
        'query': q,
        'users': users_matches,
        'files': files_matches
    }
    context.update(get_erp_context(request))
    return render(request, 'search.html', context)


@login_required
def history_view(request):
    milestones = History.objects.filter(user=request.user).order_by('-achieved_at')
    context = {'milestones': milestones}
    context.update(get_erp_context(request))
    return render(request, 'history.html', context)


@login_required
@csrf_protect
def feedback_view(request):
    if request.method == 'POST':
        subject = request.POST.get('subject', '')
        message = request.POST.get('message', '')
        rating = int(request.POST.get('rating', 5))
        
        Feedback.objects.create(
            user=request.user,
            subject=subject,
            message=message,
            rating=rating
        )
        log_action(request.user, f"Submitted feedback: {subject}", request)
        return JsonResponse({'success': True, 'message': 'Thank you for your feedback!'})
        
    context = {}
    context.update(get_erp_context(request))
    return render(request, 'feedback.html', context)


@login_required
@csrf_protect
def help_center_view(request):
    if request.method == 'POST':
        log_action(request.user, "Logged help center request", request)
        return JsonResponse({'success': True, 'message': 'Ticket submitted to recruitment support team.'})
    context = {}
    context.update(get_erp_context(request))
    return render(request, 'help-center.html', context)


@login_required
@csrf_protect
def settings_view(request):
    setting, created = Setting.objects.get_or_create(user=request.user)
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        full_name = request.POST.get('fullname')
        phone = request.POST.get('phone')
        bio = request.POST.get('bio')
        academic = request.POST.get('academic')
        skills = request.POST.get('skills')
        track = request.POST.get('track')
        
        # Notification & Theme
        theme = request.POST.get('theme', 'dark')
        email_notifications = request.POST.get('email_notifications') == 'true' or request.POST.get('email_notifications') == 'on'
        activity_digest = request.POST.get('activity_digest') == 'true' or request.POST.get('activity_digest') == 'on'
        
        # Password Change
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if old_password or new_password or confirm_password:
            if not request.user.check_password(old_password):
                return JsonResponse({'success': False, 'message': 'Incorrect current password.'}, status=400)
            if new_password != confirm_password:
                return JsonResponse({'success': False, 'message': 'New passwords do not match.'}, status=400)
            if len(new_password) < 8:
                return JsonResponse({'success': False, 'message': 'New password must be at least 8 characters long.'}, status=400)
            
            request.user.set_password(new_password)
            request.user.save()
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, request.user)
            
        if username:
            if User.objects.filter(username=username).exclude(id=request.user.id).exists():
                return JsonResponse({'success': False, 'message': 'Username is already taken.'}, status=400)
            request.user.username = username
        if email:
            if User.objects.filter(email=email).exclude(id=request.user.id).exists():
                return JsonResponse({'success': False, 'message': 'Email is already registered.'}, status=400)
            request.user.email = email
        request.user.save()
        
        if full_name is not None: profile.full_name = full_name
        if phone is not None: profile.phone = phone
        if bio is not None: profile.bio = bio
        if academic is not None: profile.academic_background = academic
        if skills is not None: profile.skills = skills
        if track is not None: profile.track = track
        profile.save()
        
        setting.theme = theme
        setting.email_notifications = email_notifications
        setting.activity_digest = activity_digest
        setting.save()
        
        request.session['theme'] = theme
        
        log_action(request.user, "Updated account & preferences settings", request)
        return JsonResponse({'success': True, 'message': 'Settings saved successfully!'})
        
    context = {
        'profile': profile,
        'setting': setting
    }
    context.update(get_erp_context(request))
    return render(request, 'settings.html', context)


@login_required
@csrf_protect
def upload_profile_picture(request):
    if request.method == 'POST':
        profile = get_object_or_404(Profile, user=request.user)
        image = request.FILES.get('profile_picture')
        
        if not image:
            return JsonResponse({'success': False, 'message': 'No image uploaded.'}, status=400)
            
        ext = os.path.splitext(image.name)[1].lower().replace('.', '')
        allowed_types = ['png', 'jpg', 'jpeg', 'webp']
        if ext not in allowed_types:
            return JsonResponse({'success': False, 'message': f'Extension .{ext} is not allowed. Upload PNG, JPG, JPEG, or WEBP.'}, status=400)
            
        if image.size > 5242880:  # 5MB
            return JsonResponse({'success': False, 'message': 'File size is too large. Limit is 5MB.'}, status=400)
            
        # Delete old profile picture if it is not default
        if profile.profile_picture and profile.profile_picture.name != 'profile_pictures/default-avatar.png':
            profile.profile_picture.delete(save=False)
            
        profile.profile_picture = image
        profile.save()
        
        log_action(request.user, "Updated profile picture", request)
        return JsonResponse({
            'success': True,
            'message': 'Profile picture updated successfully.',
            'profile_picture_url': profile.profile_picture.url
        })
    return JsonResponse({'success': False, 'message': 'POST request required.'}, status=405)


@login_required
@csrf_protect
def remove_profile_picture(request):
    if request.method == 'POST':
        profile = get_object_or_404(Profile, user=request.user)
        
        # Delete old profile picture if it is not default
        if profile.profile_picture and profile.profile_picture.name != 'profile_pictures/default-avatar.png':
            profile.profile_picture.delete(save=False)
            
        profile.profile_picture = 'profile_pictures/default-avatar.png'
        profile.save()
        
        log_action(request.user, "Removed profile picture", request)
        return JsonResponse({
            'success': True,
            'message': 'Profile picture removed.',
            'profile_picture_url': profile.profile_picture.url
        })
    return JsonResponse({'success': False, 'message': 'POST request required.'}, status=405)


def page_404(request, exception=None):
    return render(request, '404.html', status=404)


# Dynamic Course Data Store
COURSES_DATA = {
    'web-development': {
        'name': 'Web Development',
        'tagline': 'Master frontend architectures and client side design workflows.',
        'duration': '12 Weeks',
        'difficulty': 'Intermediate',
        'type': 'Development Track',
        'mode': 'Hybrid',
        'banner': 'https://images.unsplash.com/photo-1547658719-da2b51169166?auto=format&fit=crop&w=1200&q=80',
        'overview': 'Learn to build robust user interfaces and progressive web apps using modern grids and next-generation frameworks. Optimize assets, code responsive layouts, write clean semantic markup, and deploy micro-frontends with high performance.',
        'curriculum': ['Semantic HTML & DOM layouts', 'CSS flexbox/grid layout design', 'Asynchronous JS fetching', 'React.js hooks and state management', 'Next.js static site rendering', 'Production Deployment & Vercel builds'],
        'skills': ['HTML5', 'CSS3', 'JavaScript', 'React', 'Next.js', 'Bootstrap', 'Git'],
        'roadmap': [
            {'week': 'Week 1-2', 'topic': 'Semantic DOM Layouts & Grids'},
            {'week': 'Week 3-4', 'topic': 'DOM JS Scripting & API requests'},
            {'week': 'Week 5-6', 'topic': 'React hooks & state management'},
            {'week': 'Week 7-8', 'topic': 'Next.js routing & build frameworks'},
            {'week': 'Week 9-12', 'topic': 'Final Capstone Project and launch'}
        ],
        'projects': [
            {'name': 'Enterprise Portfolio Platform', 'desc': 'Sleek responsive workspace platform.'},
            {'name': 'Ticketing Dashboard Portal', 'desc': 'A fast service status tracker UI.'}
        ],
        'mentor': {
            'name': 'Sarah Jenkins',
            'role': 'Lead UI Architect',
            'exp': '8+ Years Exp',
            'spec': 'React Interfaces',
            'photo': 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=200&q=80'
        },
        'career': ['Frontend Developer', 'UI Engineer', 'Web Architect'],
        'faqs': [
            {'q': 'What tools will I learn?', 'a': 'You will master VS Code, React DevTools, Git, and Chrome Performance tools.'}
        ]
    },
    'mobile-app-development': {
        'name': 'Mobile App Development',
        'tagline': 'Build premium cross-platform iOS and Android apps.',
        'duration': '12 Weeks',
        'difficulty': 'Intermediate',
        'type': 'Mobile Track',
        'mode': 'Online',
        'banner': 'https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?auto=format&fit=crop&w=1200&q=80',
        'overview': 'Engineered cross-platform mobile apps for Android and iOS devices using Flutter. Learn offline storage syncing, local caching, device push alerts, biometrics, and secure app store distributions.',
        'curriculum': ['Dart programming rules', 'Flutter widgets orchestration', 'State management (Bloc/Provider)', 'Offline databases (SQLite local)', 'Device camera/biometrics API', 'App Store and Google Play builds'],
        'skills': ['Dart', 'Flutter', 'Swift', 'Kotlin', 'SQLite', 'Firebase', 'APIs'],
        'roadmap': [
            {'week': 'Week 1-2', 'topic': 'Dart Syntax & Functional Loops'},
            {'week': 'Week 3-4', 'topic': 'UI layout components & lists'},
            {'week': 'Week 5-6', 'topic': 'State flow & local caching'},
            {'week': 'Week 7-8', 'topic': 'Push triggers & hardware hooks'},
            {'week': 'Week 9-12', 'topic': 'Play store deployment & tests'}
        ],
        'projects': [
            {'name': 'Secure Vault Messenger', 'desc': 'End-to-end encrypted local storage messenger app.'},
            {'name': 'Courier Delivery Tracking App', 'desc': 'A tracking system using dynamic mapping services.'}
        ],
        'mentor': {
            'name': 'Michael Chang',
            'role': 'Lead Flutter Engineer',
            'exp': '7+ Years Exp',
            'spec': 'Mobile Platform Architecture',
            'photo': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=200&q=80'
        },
        'career': ['Mobile App Developer', 'Flutter Engineer', 'iOS/Android Consultant'],
        'faqs': [
            {'q': 'Do I need a Mac?', 'a': 'A Mac is helpful to compile for iOS, but windows environments are fully supported for Android.'}
        ]
    },
    'python-development': {
        'name': 'Python Development',
        'tagline': 'Master data processing, background script queuing, and scripting pipelines.',
        'duration': '12 Weeks',
        'difficulty': 'Beginner-to-Intermediate',
        'type': 'Scripting Track',
        'mode': 'Hybrid',
        'banner': 'https://images.unsplash.com/photo-1515879218367-8466d910aaa4?auto=format&fit=crop&w=1200&q=80',
        'overview': 'Orchestrate structured scrapers, multi-process task queues, dynamic scrapers, database adapters, and automated script pipelines.',
        'curriculum': ['Python syntax & OOP structures', 'Scrapy & BS4 data pipelines', 'Pandas/NumPy numerical parsing', 'Asynchronous programming (asyncio)', 'Database connectors & bulk loads', 'Task executors (Celery/Redis)'],
        'skills': ['Python', 'SQL', 'FastAPI', 'Pandas', 'NumPy', 'Celery', 'Git'],
        'roadmap': [
            {'week': 'Week 1-2', 'topic': 'OOP Fundamentals & Lists'},
            {'week': 'Week 3-4', 'topic': 'Data Extraction & Scraping'},
            {'week': 'Week 5-6', 'topic': 'Pandas data frame arrays'},
            {'week': 'Week 7-8', 'topic': 'Async queues & background processing'},
            {'week': 'Week 9-12', 'topic': 'Data pipelines deployment'}
        ],
        'projects': [
            {'name': 'Distributed Scraper Network', 'desc': 'A multi-threaded scraper cluster.'},
            {'name': 'Log Analysis Broker', 'desc': 'Parses live server logs and aggregates errors.'}
        ],
        'mentor': {
            'name': 'David Ross',
            'role': 'Automation Specialist',
            'exp': '9+ Years Exp',
            'spec': 'Python Backend Orchestration',
            'photo': 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=200&q=80'
        },
        'career': ['Python Developer', 'Automation Engineer', 'Data Ingestion Specialist'],
        'faqs': [
            {'q': 'Is database logic covered?', 'a': 'Yes, you will work extensively with SQLite, PostgreSQL, and Redis cache.'}
        ]
    },
    'django-development': {
        'name': 'Django Development',
        'tagline': 'Build secure, database-backed corporate ERPs and REST web services.',
        'duration': '12 Weeks',
        'difficulty': 'Intermediate',
        'type': 'Backend Track',
        'mode': 'Hybrid',
        'banner': 'https://images.unsplash.com/photo-1498050108023-c5249f4df085?auto=format&fit=crop&w=1200&q=80',
        'overview': 'Understand secure authentication backends, models mapping, Django ORM, secure form verification, REST API structures, and microservices links.',
        'curriculum': ['Django core system layout', 'ORM model maps & migrations', 'Class Based Views & Forms validation', 'Django REST framework (DRF) serializations', 'Session and Token auth filters', 'Server administration & deployment'],
        'skills': ['Python', 'Django', 'SQLite', 'DRF', 'PostgreSQL', 'Docker', 'REST API'],
        'roadmap': [
            {'week': 'Week 1-2', 'topic': 'Django ORM Schema architecture'},
            {'week': 'Week 3-4', 'topic': 'Session context & Middleware'},
            {'week': 'Week 5-6', 'topic': 'DRF APIs & Serializers'},
            {'week': 'Week 7-8', 'topic': 'OAuth token auth & Security headers'},
            {'week': 'Week 9-12', 'topic': 'Production setups & migrations'}
        ],
        'projects': [
            {'name': 'Internship ERP Management Portal', 'desc': 'An advanced ERP system for cohorts.'},
            {'name': 'Corporate e-Commerce API Engine', 'desc': 'Scalable API system supporting secure payments.'}
        ],
        'mentor': {
            'name': 'Elena Rostova',
            'role': 'Senior Backend Engineer',
            'exp': '6+ Years Exp',
            'spec': 'Django Security & Scaling',
            'photo': 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?auto=format&fit=crop&w=200&q=80'
        },
        'career': ['Django Developer', 'Backend Software Engineer', 'API Architect'],
        'faqs': [
            {'q': 'Does this cover security parameters?', 'a': 'Yes, including XSS filters, CSRF validations, and SQL injection protections.'}
        ]
    },
    'mern-stack': {
        'name': 'MERN Stack Development',
        'tagline': 'Master MongoDB, Express.js, React, and Node.js backend systems.',
        'duration': '12 Weeks',
        'difficulty': 'Intermediate',
        'type': 'Full Stack Track',
        'mode': 'Hybrid',
        'banner': 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?auto=format&fit=crop&w=1200&q=80',
        'overview': 'Learn Node.js routing architectures, Express middlewares, React components, state engines, and MongoDB databases collections.',
        'curriculum': ['MongoDB schemas validation', 'Express routing and auth logs', 'React context frameworks', 'Node server scaling architectures', 'JWT tokens session rules', 'Docker integration & hosting'],
        'skills': ['MongoDB', 'Express.js', 'React.js', 'Node.js', 'Mongoose', 'REST API', 'Git'],
        'roadmap': [
            {'week': 'Week 1-2', 'topic': 'NodeJS servers & routing workflows'},
            {'week': 'Week 3-4', 'topic': 'MongoDB databases collections and indexing'},
            {'week': 'Week 5-6', 'topic': 'Express middlewares & JWT security'},
            {'week': 'Week 7-8', 'topic': 'React interfaces integration'},
            {'week': 'Week 9-12', 'topic': 'Fullstack ERP projects launch'}
        ],
        'projects': [
            {'name': 'Collaborative Scrum Board', 'desc': 'Real-time kanban board using WebSockets.'},
            {'name': 'Corporate Inventory Platform', 'desc': 'A system managing warehouse stock workflows.'}
        ],
        'mentor': {
            'name': 'Liam Fletcher',
            'role': 'Fullstack Lead Designer',
            'exp': '8+ Years Exp',
            'spec': 'MERN Architectures & Scaling',
            'photo': 'https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?auto=format&fit=crop&w=200&q=80'
        },
        'career': ['MERN Developer', 'Fullstack Software Engineer', 'Node.js Consultant'],
        'faqs': [
            {'q': 'Is WebSocket coverage included?', 'a': 'Yes, real-time message streams using Socket.io are covered.'}
        ]
    },
    'java-development': {
        'name': 'Java Development',
        'tagline': 'Master OOP architecture, multithreading, and Spring Boot web engines.',
        'duration': '12 Weeks',
        'difficulty': 'Intermediate',
        'type': 'Enterprise Track',
        'mode': 'Hybrid',
        'banner': 'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=1200&q=80',
        'overview': 'Build robust, thread-safe programs and scalable Spring Boot systems utilizing Hibernate schemas mapping and PostgreSQL caches.',
        'curriculum': ['Java OOP & memory pipelines', 'Multithreading and locks', 'Spring Boot models orchestration', 'Hibernate JPA repositories', 'Spring Security OAuth controls', 'Microservices design setups'],
        'skills': ['Java', 'Spring Boot', 'Hibernate', 'PostgreSQL', 'Maven', 'Docker', 'REST API'],
        'roadmap': [
            {'week': 'Week 1-2', 'topic': 'JVM memory allocation & garbage collections'},
            {'week': 'Week 3-4', 'topic': 'Concurrent executors & threads'},
            {'week': 'Week 5-6', 'topic': 'Spring boot structure mapping'},
            {'week': 'Week 7-8', 'topic': 'JPA data adapters and tables'},
            {'week': 'Week 9-12', 'topic': 'Spring microservices deployments'}
        ],
        'projects': [
            {'name': 'Billing Microservice Broker', 'desc': 'High throughput transaction processor system.'},
            {'name': 'Corporate CRM Hub', 'desc': 'Customer relationship logs and workflow engine.'}
        ],
        'mentor': {
            'name': 'Aleksei Volkov',
            'role': 'Lead Enterprise Architect',
            'exp': '10+ Years Exp',
            'spec': 'Spring Boot Architecture',
            'photo': 'https://images.unsplash.com/photo-1542909168-82c3e7fdca5c?auto=format&fit=crop&w=200&q=80'
        },
        'career': ['Java Developer', 'Enterprise Software Engineer', 'Spring Boot Specialist'],
        'faqs': [
            {'q': 'Are data structures covered?', 'a': 'Yes, advanced algorithms and collection pipelines are optimized.'}
        ]
    },
    'ui-ux-design': {
        'name': 'UI/UX Design',
        'tagline': 'Create stunning interfaces, user flows, and interactive mockups.',
        'duration': '12 Weeks',
        'difficulty': 'Beginner-to-Intermediate',
        'type': 'Creative Track',
        'mode': 'Hybrid',
        'banner': 'https://images.unsplash.com/photo-1561070791-26c113006238?auto=format&fit=crop&w=1200&q=80',
        'overview': 'Design user wireframes, custom system layouts, responsive interfaces, user journey maps, and high-fidelity clickable prototype grids inside Figma.',
        'curriculum': ['User research and journey outlines', 'Figma layouts grids & auto layout', 'Design system token guides', 'Hi-fi prototyping & interactive states', 'Accessibility Guidelines (WCAG)', 'Hand-off design developer workflows'],
        'skills': ['Figma', 'UI Design', 'UX Research', 'Prototyping', 'Design Systems', 'Wireframing'],
        'roadmap': [
            {'week': 'Week 1-2', 'topic': 'User flows & research maps'},
            {'week': 'Week 3-4', 'topic': 'Figma layout systems & colors'},
            {'week': 'Week 5-6', 'topic': 'Auto-layout & components setup'},
            {'week': 'Week 7-8', 'topic': 'Interactive prototypes and user tests'},
            {'week': 'Week 9-12', 'topic': 'Figma developer handoff & guides'}
        ],
        'projects': [
            {'name': 'BlueNova ERP Mockup App', 'desc': 'Complete responsive design system mapping.'},
            {'name': 'Fintech Mobile App Prototype', 'desc': 'A payment app layout designed for quick flows.'}
        ],
        'mentor': {
            'name': 'Aria Sterling',
            'role': 'Product Designer',
            'exp': '6+ Years Exp',
            'spec': 'Design Systems & Figma Workflows',
            'photo': 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=200&q=80'
        },
        'career': ['UI Developer', 'UX Researcher', 'Product Interface Designer'],
        'faqs': [
            {'q': 'Do I need coding experience?', 'a': 'No coding is required. This track is focused 100% on design tools.'}
        ]
    },
    'data-science': {
        'name': 'Data Science',
        'tagline': 'Master data visualization pipelines, regression models, and statistical analysis.',
        'duration': '12 Weeks',
        'difficulty': 'Intermediate',
        'type': 'Analytical Track',
        'mode': 'Hybrid',
        'banner': 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=1200&q=80',
        'overview': 'Construct clean ETL pipelines, statistical tables parsing, numerical metrics arrays, scatter graphs plotting, and regressions mapping.',
        'curriculum': ['Python scientific stacks', 'Pandas array transformations', 'Matplotlib and Seaborn graphs', 'Statistical modeling systems', 'SQL databases aggregation workflows', 'Big Data Spark configurations'],
        'skills': ['Python', 'Pandas', 'Matplotlib', 'SQL', 'Seaborn', 'Scikit-Learn', 'Git'],
        'roadmap': [
            {'week': 'Week 1-2', 'topic': 'Python Math syntax arrays'},
            {'week': 'Week 3-4', 'topic': 'Pandas cleaning workflows'},
            {'week': 'Week 5-6', 'topic': 'Plotting datasets visually'},
            {'week': 'Week 7-8', 'topic': 'Regression algorithms & clusters'},
            {'week': 'Week 9-12', 'topic': 'ETL pipeline capstone deployment'}
        ],
        'projects': [
            {'name': 'Global Climate Grapher App', 'desc': 'Parses 50 years of temperature data and visualizes charts.'},
            {'name': 'Customer Cohort Predictor', 'desc': 'A prediction algorithm categorizing cohort churn rates.'}
        ],
        'mentor': {
            'name': 'Ryan Vance',
            'role': 'Senior Data Scientist',
            'exp': '7+ Years Exp',
            'spec': 'Statistical Pipelines & SQL',
            'photo': 'https://images.unsplash.com/photo-1492562080023-ab3db95bfbce?auto=format&fit=crop&w=200&q=80'
        },
        'career': ['Data Analyst', 'Data Engineer', 'Visualization Consultant'],
        'faqs': [
            {'q': 'Is math intensive?', 'a': 'Basic statistics and probability are required. We review these in weeks 1 and 2.'}
        ]
    },
    'artificial-intelligence': {
        'name': 'Artificial Intelligence',
        'tagline': 'Implement neural network layouts, deep learning grids, and NLP pipelines.',
        'duration': '12 Weeks',
        'difficulty': 'Advanced',
        'type': 'Research Track',
        'mode': 'Online',
        'banner': 'https://images.unsplash.com/photo-1677442136019-21780efad99a?auto=format&fit=crop&w=1200&q=80',
        'overview': 'Learn deep learning algorithms, CNN node architectures, transformers model structures, NLP tokenizations, and custom vector search engines.',
        'curriculum': ['Neural network calculations', 'PyTorch network models setup', 'Transformers & token mappings', 'Vector databases indexing', 'GPU parallel training loops', 'Model optimization & ONNX runtimes'],
        'skills': ['PyTorch', 'TensorFlow', 'Vector DB', 'Transformers', 'Python', 'ONNX', 'HuggingFace'],
        'roadmap': [
            {'week': 'Week 1-2', 'topic': 'Linear Algebra & Neurons calculations'},
            {'week': 'Week 3-4', 'topic': 'Backpropagation & Gradient descent'},
            {'week': 'Week 5-6', 'topic': 'NLP word models & embeddings'},
            {'week': 'Week 7-8', 'topic': 'Vector searches and dynamic lookups'},
            {'week': 'Week 9-12', 'topic': 'Training chatbot nodes capstone'}
        ],
        'projects': [
            {'name': 'DocSearch AI Bot', 'desc': 'A bot indexing PDFs and answering queries.'},
            {'name': 'Live Object Counter Agent', 'desc': 'Real-time object detector on web camera feeds.'}
        ],
        'mentor': {
            'name': 'Dr. Alan Vance',
            'role': 'AI Research Director',
            'exp': '12+ Years Exp',
            'spec': 'Deep Learning Systems',
            'photo': 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?auto=format&fit=crop&w=200&q=80'
        },
        'career': ['AI Software Engineer', 'NLP Developer', 'Deep Learning Specialist'],
        'faqs': [
            {'q': 'Which library is focused?', 'a': 'We use PyTorch for model architectures and training loops.'}
        ]
    },
    'machine-learning': {
        'name': 'Machine Learning',
        'tagline': 'Deploy regression classifiers, decision tree grids, and predictive clusters.',
        'duration': '12 Weeks',
        'difficulty': 'Intermediate-to-Advanced',
        'type': 'Practical Track',
        'mode': 'Hybrid',
        'banner': 'https://images.unsplash.com/photo-1527474305487-b87b222841cc?auto=format&fit=crop&w=1200&q=80',
        'overview': 'Develop classification scripts, predictive clusters mapping, logistic grids algorithms, hyperparameter tunings, and model evaluation metrics.',
        'curriculum': ['Supervised learning equations', 'Scikit-learn model parameters', 'Decision tree calculations', 'Cluster categorizations (K-Means)', 'Hyperparameter tuning models', 'Scoring methods (F1-Score, AUC)'],
        'skills': ['Python', 'Scikit-Learn', 'Pandas', 'NumPy', 'Matplotlib', 'Model Tuning', 'Git'],
        'roadmap': [
            {'week': 'Week 1-2', 'topic': 'Linear Regression equations'},
            {'week': 'Week 3-4', 'topic': 'Decision trees & RandomForest classifiers'},
            {'week': 'Week 5-6', 'topic': 'Clustering and categorization grids'},
            {'week': 'Week 7-8', 'topic': 'Cross-validation parameters tuning'},
            {'week': 'Week 9-12', 'topic': 'Predictive ML pipeline capstone'}
        ],
        'projects': [
            {'name': 'Real Estate Price Agent', 'desc': 'A predictor evaluating pricing metrics.'},
            {'name': 'Credit Card Fraud Detector', 'desc': 'An outlier analyzer matching transaction logs.'}
        ],
        'mentor': {
            'name': 'Nadia Petrov',
            'role': 'Lead ML Engineer',
            'exp': '8+ Years Exp',
            'spec': 'Classification Pipelines',
            'photo': 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=200&q=80'
        },
        'career': ['ML Engineer', 'Model Tuner', 'Data Analytics Consultant'],
        'faqs': [
            {'q': 'Is Python mandatory?', 'a': 'Yes, advanced Python scripts form the core of this course.'}
        ]
    },
    'cloud-computing': {
        'name': 'Cloud Computing',
        'tagline': 'Master AWS components mapping, cloud security structures, and serverless loops.',
        'duration': '12 Weeks',
        'difficulty': 'Intermediate',
        'type': 'Infrastructure Track',
        'mode': 'Hybrid',
        'banner': 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=1200&q=80',
        'overview': 'Design serverless micro-functions, IAM security credentials clusters, cloud networks layouts, load balancing arrays, and secure backups setups on Amazon Web Services.',
        'curriculum': ['AWS EC2 instance models mapping', 'IAM role setups & credentials', 'VPC network grids & gateways', 'Serverless execution configurations', 'CloudWatch logger setups', 'Infrastructure as Code scripts'],
        'skills': ['AWS', 'Cloud Security', 'IAM', 'Terraform', 'Serverless', 'Linux', 'VPC'],
        'roadmap': [
            {'week': 'Week 1-2', 'topic': 'Linux shell loops & VM controls'},
            {'week': 'Week 3-4', 'topic': 'IAM roles and network gateways setup'},
            {'week': 'Week 5-6', 'topic': 'Load balancing & scaling configs'},
            {'week': 'Week 7-8', 'topic': 'AWS Lambda triggers & S3 triggers'},
            {'week': 'Week 9-12', 'topic': 'Terraform files deployment'}
        ],
        'projects': [
            {'name': 'Elastic Load Balanced System', 'desc': 'Automated scaling network layout.'},
            {'name': 'Auto-backup Media Vault', 'desc': 'A serverless pipeline transforming and storage vault.'}
        ],
        'mentor': {
            'name': 'Steve Rogers',
            'role': 'Cloud Architect',
            'exp': '9+ Years Exp',
            'spec': 'AWS Systems & IaC',
            'photo': 'https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?auto=format&fit=crop&w=200&q=80'
        },
        'career': ['Cloud Engineer', 'AWS Architect', 'Systems Administrator'],
        'faqs': [
            {'q': 'Is AWS free tier enough?', 'a': 'Yes, we design all practical runs to fit within the AWS free tier.'}
        ]
    },
    'cyber-security': {
        'name': 'Cyber Security',
        'tagline': 'Master penetration scanning tools, security mapping protocols, and threat scans.',
        'duration': '12 Weeks',
        'difficulty': 'Intermediate',
        'type': 'Security Track',
        'mode': 'Hybrid',
        'banner': 'https://images.unsplash.com/photo-1563986768609-322da13575f3?auto=format&fit=crop&w=1200&q=80',
        'overview': 'Perform network packet captures scanning, vulnerability maps assessment, threat audits calculations, and server authentication hardening setups.',
        'curriculum': ['Networking layers audits & scans', 'OWASP Top 10 vulnerabilities maps', 'Wireshark captures parsing', 'Nmap network sweeps configurations', 'Encryption & keys certifications', 'Firewalls rules configurations'],
        'skills': ['Wireshark', 'Nmap', 'Security Audit', 'Firewalls', 'Metasploit', 'Linux', 'OWASP'],
        'roadmap': [
            {'week': 'Week 1-2', 'topic': 'TCPIP protocols & audits mapping'},
            {'week': 'Week 3-4', 'topic': 'OWASP vulnerabilities testing'},
            {'week': 'Week 5-6', 'topic': 'Metasploit scan scripts execution'},
            {'week': 'Week 7-8', 'topic': 'Active monitoring and log sweeps'},
            {'week': 'Week 9-12', 'topic': 'Penetration audit check capstone'}
        ],
        'projects': [
            {'name': 'Vulnerability Analyzer Sweep', 'desc': 'A network vulnerability scanner report tool.'},
            {'name': 'Secure Access Control Gateway', 'desc': 'A customized SSH filter blocker script.'}
        ],
        'mentor': {
            'name': 'Diana Prince',
            'role': 'SecOps Engineer',
            'exp': '8+ Years Exp',
            'spec': 'Securing Network Hardware Layers',
            'photo': 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=200&q=80'
        },
        'career': ['Cyber Security Analyst', 'Penetration Tester', 'SecOps Engineer'],
        'faqs': [
            {'q': 'Is programming needed?', 'a': 'Basic shell scripting is covered. Previous code logic experience helps but is not mandatory.'}
        ]
    },
    'devops': {
        'name': 'DevOps',
        'tagline': 'Deploy microservices clusters, auto-scaling deployment pipelines, and CI checks.',
        'duration': '12 Weeks',
        'difficulty': 'Intermediate-to-Advanced',
        'type': 'Systems Track',
        'mode': 'Hybrid',
        'banner': 'https://images.unsplash.com/photo-1618401471353-b98aedd07871?auto=format&fit=crop&w=1200&q=80',
        'overview': 'Configure Docker containers, Kubernetes routing configurations, GitHub Actions pipelines mapping, and automated server monitoring workflows.',
        'curriculum': ['Docker files architectures design', 'Kubernetes clusters deployment', 'CI/CD pipeline hooks', 'Monitoring tools (Prometheus)', 'Linux system automation scripts', 'IaC file configurations setup'],
        'skills': ['Docker', 'Kubernetes', 'CI/CD', 'GitHub Actions', 'Prometheus', 'Linux', 'IaC'],
        'roadmap': [
            {'week': 'Week 1-2', 'topic': 'Linux sysadmin tasks automation'},
            {'week': 'Week 3-4', 'topic': 'Docker multi-container layouts mapping'},
            {'week': 'Week 5-6', 'topic': 'CI Actions pipelines compilation'},
            {'week': 'Week 7-8', 'topic': 'Kubernetes pod routing setups'},
            {'week': 'Week 9-12', 'topic': 'Full automated deployments Capstone'}
        ],
        'projects': [
            {'name': 'Distributed Web Cluster', 'desc': 'Kubernetes multi-pod workspace layout.'},
            {'name': 'Auto CI Testing Agent', 'desc': 'Pipeline auditing backend lint checks automatically.'}
        ],
        'mentor': {
            'name': 'Bruce Banner',
            'role': 'DevOps Architect',
            'exp': '10+ Years Exp',
            'spec': 'Kubernetes Orchestration & Scale',
            'photo': 'https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?auto=format&fit=crop&w=200&q=80'
        },
        'career': ['DevOps Engineer', 'Release Manager', 'Platform Architect'],
        'faqs': [
            {'q': 'Are servers expensive?', 'a': 'We configure containers locally using Docker. Deployment tests use free tiers.'}
        ]
    },
    'iot': {
        'name': 'IoT & Smart Systems',
        'tagline': 'Master hardware controller loops, MQTT telemetry arrays, and board setups.',
        'duration': '12 Weeks',
        'difficulty': 'Beginner-to-Intermediate',
        'type': 'Hardware Track',
        'mode': 'Hybrid',
        'banner': 'https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1200&q=80',
        'overview': 'Design hardware telemetry sensors grids, board scripting loops, MQTT brokers interfaces, and database charts dashboards.',
        'curriculum': ['Raspberry Pi setups & shell tasks', 'GPIO pin scripts controls', 'MQTT packet broker protocols', 'Telemetry arrays saving databases', 'Alert notifications structures', 'Board firmware setup rules'],
        'skills': ['Raspberry Pi', 'Python', 'MQTT', 'GPIO', 'SQL', 'C++', 'Electronics'],
        'roadmap': [
            {'week': 'Week 1-2', 'topic': 'Firmware flash loops & Pi setups'},
            {'week': 'Week 3-4', 'topic': 'GPIO pin triggers scripting'},
            {'week': 'Week 5-6', 'topic': 'MQTT telemetry publish checks'},
            {'week': 'Week 7-8', 'topic': 'Database alerts pipelines setup'},
            {'week': 'Week 9-12', 'topic': 'Telemetry board capstone projects'}
        ],
        'projects': [
            {'name': 'Telemetry Room Sweep', 'desc': 'A room sensor array reporting heat metrics.'},
            {'name': 'Secure Gate Access Monitor', 'desc': 'Pi monitor script taking images and reporting log access.'}
        ],
        'mentor': {
            'name': 'Barry Allen',
            'role': 'Hardware Systems Specialist',
            'exp': '8+ Years Exp',
            'spec': 'Telemetry Systems Design',
            'photo': 'https://images.unsplash.com/photo-1542909168-82c3e7fdca5c?auto=format&fit=crop&w=200&q=80'
        },
        'career': ['IoT Systems Engineer', 'Embedded Developer', 'Hardware Consultant'],
        'faqs': [
            {'q': 'Are hardware kits provided?', 'a': 'Yes, we provide dynamic hardware board simulators for all online modules.'}
        ]
    },
    'digital-marketing': {
        'name': 'Digital Marketing',
        'tagline': 'Master SEO analytics, campaign performance tracking, and metric dashboards.',
        'duration': '12 Weeks',
        'difficulty': 'Beginner',
        'type': 'Marketing Track',
        'mode': 'Hybrid',
        'banner': 'https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=1200&q=80',
        'overview': 'Orchestrate SEO checks campaigns, performance metrics dashboards, dynamic user conversion graphs, ad platforms mappings, and content metrics audits.',
        'curriculum': ['SEO crawl maps & checks', 'Google Analytics setup rules', 'Keyword metrics calculations', 'Ad campaign tracking systems', 'Customer retention audits', 'Visual aggregate reports creation'],
        'skills': ['SEO', 'Analytics', 'Keyword Search', 'Google Ads', 'Mailchimp', 'Writing', 'HTML'],
        'roadmap': [
            {'week': 'Week 1-2', 'topic': 'SEO parameters & crawl indexes'},
            {'week': 'Week 3-4', 'topic': 'Google Analytics tracking setup'},
            {'week': 'Week 5-6', 'topic': 'Ad campaign structures configurations'},
            {'week': 'Week 7-8', 'topic': 'Conversion filters calculation'},
            {'week': 'Week 9-12', 'topic': 'Marketing metrics dashboard capstone'}
        ],
        'projects': [
            {'name': 'E-commerce SEO Audit Plan', 'desc': 'A comprehensive performance crawl report.'},
            {'name': 'Cohort Retention Dashboard', 'desc': 'A tool tracing email campaign conversion metrics.'}
        ],
        'mentor': {
            'name': 'Iris West',
            'role': 'Growth Director',
            'exp': '7+ Years Exp',
            'spec': 'SEO Analytics & Conversions',
            'photo': 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?auto=format&fit=crop&w=200&q=80'
        },
        'career': ['SEO Specialist', 'Growth Manager', 'Analytics Consultant'],
        'faqs': [
            {'q': 'Does this cover coding?', 'a': 'Only basic HTML markup tuning is covered for technical SEO purposes.'}
        ]
    }
}


def course_detail_view(request, course_slug):
    course = COURSES_DATA.get(course_slug)
    if not course:
        return render(request, '404.html', status=404)
    
    # Generate related courses (exclude current one, show 3)
    related = []
    for slug, data in COURSES_DATA.items():
        if slug != course_slug:
            related.append({
                'slug': slug,
                'name': data['name'],
                'tagline': data['tagline'],
                'banner': data['banner'],
                'duration': data['duration']
            })
            if len(related) == 3:
                break
                
    context = {
        'course': course,
        'course_slug': course_slug,
        'related_courses': related
    }
    context.update(get_erp_context(request))
    return render(request, 'course_detail.html', context)


@csrf_protect
def apply_view(request):
    selected_course = request.GET.get('course', '').strip()
    
    # Map slug to proper name if possible
    course_name_map = {slug: data['name'] for slug, data in COURSES_DATA.items()}
    prefilled_course = course_name_map.get(selected_course, '')
    
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        phone = request.POST.get('phone', '').strip()
        college = request.POST.get('college', '').strip()
        branch = request.POST.get('branch', '').strip()
        semester = request.POST.get('semester', '').strip()
        city = request.POST.get('city', '').strip()
        cover_letter = request.POST.get('cover_letter', '').strip()
        course = request.POST.get('course', prefilled_course or 'Web Development').strip()
        batch = request.POST.get('batch', 'July 2026 Cohort').strip()
        mode = request.POST.get('mode', 'Hybrid').strip()
        resume = request.FILES.get('resume')
        
        if not (full_name and email and phone and college and branch and semester and city and resume):
            return JsonResponse({'success': False, 'message': 'All required fields must be completed.'}, status=400)
            
        ext = os.path.splitext(resume.name)[1].lower().replace('.', '')
        if ext not in ['pdf', 'doc', 'docx']:
            return JsonResponse({'success': False, 'message': f'File extension .{ext} is not allowed. Upload PDF or Word files.'}, status=400)
            
        if resume.size > 10485760:  # 10MB
            return JsonResponse({'success': False, 'message': 'Resume file is too large. Limit is 10MB.'}, status=400)
            
        # 1. Create User & Profile dynamically if they do not exist
        user = None
        user_created = False
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Generate username from email
            username_base = email.split('@')[0]
            username = username_base
            idx = 1
            while User.objects.filter(username=username).exists():
                username = f"{username_base}{idx}"
                idx += 1
                
            user = User.objects.create_user(username=username, email=email, password='password', role='user')
            user_created = True
            
            # Map course to nearest TRACK_CHOICES
            track = 'Software Engineering'
            if 'Design' in course or 'UX' in course:
                track = 'UI/UX Design'
            elif 'Science' in course or 'Learning' in course or 'Intelligence' in course or 'Data' in course:
                track = 'Data Analytics'
                
            Profile.objects.create(
                user=user,
                full_name=full_name,
                phone=phone,
                track=track,
                academic_background=f"{college} - {branch} (Sem {semester})",
                bio="Internship request submitted from the public details apply panel.",
                resume=resume,
                status='pending'
            )
            Setting.objects.create(user=user, theme='dark')
            
            History.objects.create(
                user=user,
                milestone_name="Application Process Begun",
                description=f"Your request for the {course} internship has been successfully filed."
            )
            
        # 2. Save InternshipApplication
        app = InternshipApplication.objects.create(
            full_name=full_name,
            email=email,
            phone=phone,
            college=college,
            branch=branch,
            semester=semester,
            city=city,
            resume=resume,
            cover_letter=cover_letter,
            course=course,
            batch=batch,
            mode=mode,
            status='pending',
            user=user
        )
        
        msg = f"Your application for {course} was filed successfully!"
        if user_created:
            msg += f" A student portal account was auto-generated. Username: {user.username}, Password: password. Please log in to monitor review progress."
            
        return JsonResponse({'success': True, 'message': msg})
        
    context = {
        'courses': [data['name'] for data in COURSES_DATA.values()],
        'prefilled_course': prefilled_course
    }
    context.update(get_erp_context(request))
    return render(request, 'apply.html', context)


@login_required
@admin_required
def admin_applications_view(request):
    apps = InternshipApplication.objects.all().order_by('-submission_date')
    
    # Handle Search
    search = request.GET.get('search', '').strip()
    if search:
        apps = apps.filter(full_name__icontains=search) | apps.filter(email__icontains=search) | apps.filter(college__icontains=search)
        
    # Handle Filter
    course_filter = request.GET.get('course', '').strip()
    if course_filter:
        apps = apps.filter(course=course_filter)
        
    # Handle CSV Export
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="internship_applications.csv"'
        writer = csv.writer(response)
        writer.writerow(['ID', 'Name', 'Email', 'Phone', 'Course', 'College', 'Branch', 'Semester', 'Batch', 'Mode', 'Status', 'Date'])
        for a in apps:
            writer.writerow([a.id, a.full_name, a.email, a.phone, a.course, a.college, a.branch, a.semester, a.batch, a.mode, a.status, a.submission_date.strftime('%Y-%m-%d')])
        return response
        
    # Handle PDF Export
    if request.GET.get('export') == 'pdf':
        from reportlab.pdfgen import canvas
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        p.drawString(100, 800, "BlueNova Technologies - Internship Applications List")
        y = 750
        for idx, a in enumerate(apps):
            p.drawString(50, y, f"{idx+1}. {a.full_name} ({a.email}) - {a.course} [{a.status.upper()}]")
            y -= 25
            if y < 50:
                p.showPage()
                y = 800
        p.showPage()
        p.save()
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="internship_applications.pdf"'
        return response
        
    context = {
        'applications_list': apps,
        'courses': [data['name'] for data in COURSES_DATA.values()],
        'search': search,
        'selected_course': course_filter
    }
    context.update(get_erp_context(request))
    return render(request, 'admin_applications.html', context)


@login_required
@admin_required
@csrf_protect
def application_action_view(request, app_id, action_type):
    app = get_object_or_404(InternshipApplication, id=app_id)
    if action_type == 'approve':
        app.status = 'approved'
        app.save()
        if app.user and hasattr(app.user, 'profile'):
            app.user.profile.status = 'approved'
            app.user.profile.save()
            History.objects.create(
                user=app.user,
                milestone_name="Application Approved",
                description=f"Congratulations! Your application for {app.course} has been approved."
            )
            # Create a notification
            Notification.objects.create(
                user=app.user,
                title="Application Approved",
                message=f"Your request for the {app.course} cohort has been approved! Welcome aboard.",
                level="success"
            )
        messages.success(request, f"Application of {app.full_name} has been approved.")
    elif action_type == 'reject':
        app.status = 'rejected'
        app.save()
        if app.user and hasattr(app.user, 'profile'):
            app.user.profile.status = 'rejected'
            app.user.profile.save()
            History.objects.create(
                user=app.user,
                milestone_name="Application Rejected",
                description=f"Your application for {app.course} was processed and rejected."
            )
            # Create a notification
            Notification.objects.create(
                user=app.user,
                title="Application Rejected",
                message=f"We regret to inform you that your request for the {app.course} cohort was not selected.",
                level="danger"
            )
        messages.warning(request, f"Application of {app.full_name} has been rejected.")
        
    return redirect('admin_applications')


@login_required
def download_application_resume_view(request, app_id):
    app = get_object_or_404(InternshipApplication, id=app_id)
    # Checks role logic
    if request.user.role != 'admin' and app.user != request.user:
        return HttpResponse("Unauthorized access.", status=403)
        
    if not app.resume:
        return HttpResponse("No resume file available.", status=404)
        
    response = HttpResponse(app.resume, content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{os.path.basename(app.resume.name)}"'
    return response


# Helper to format seconds to HH:MM:SS
def format_seconds(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


# Automatic Seeding Helper for LMS
def seed_lms_data_if_empty():
    if LMSCourse.objects.count() > 0:
        return
        
    course1 = LMSCourse.objects.create(
        name='Python Full Stack Development',
        tagline='Master Python scripting, OOP design, and Django database schemas.',
        description='A complete guide to becoming a professional python backend engineer. Learn virtualenv tools, loops, class designs, and REST api views.',
        duration='12 Weeks',
        difficulty='Intermediate',
        banner_url='https://images.unsplash.com/photo-1515879218367-8466d910aaa4?auto=format&fit=crop&w=1200&q=80'
    )
    
    m1 = LMSModule.objects.create(course=course1, title='Module 1: Introduction to Scripting', order=1)
    m2 = LMSModule.objects.create(course=course1, title='Module 2: Lists, Dicts, and Functions', order=2)
    m3 = LMSModule.objects.create(course=course1, title='Module 3: Object Oriented Design (OOP)', order=3)
    m4 = LMSModule.objects.create(course=course1, title='Module 4: Django backend databases', order=4)
    
    l1 = Lecture.objects.create(
        module=m1,
        title='1. Python Installation & Setup',
        video_url='https://www.youtube.com/embed/rfscVS0vtbw',
        youtube_id='rfscVS0vtbw',
        description='Learn how to install Python on Windows, macOS, and Linux systems. Set up a virtual environment and configure VS Code editor.',
        duration='00:10',
        order=1
    )
    l2 = Lecture.objects.create(
        module=m1,
        title='2. Declaring Variables & Types',
        video_url='https://www.youtube.com/embed/kqtD5dpn9C8',
        youtube_id='kqtD5dpn9C8',
        description='Explore numbers, strings, booleans, and arithmetic operators inside Python.',
        duration='00:12',
        order=2
    )
    l3 = Lecture.objects.create(
        module=m2,
        title='3. Lists & Dictionaries loops',
        video_url='https://www.youtube.com/embed/khKv-8q7YmY',
        youtube_id='khKv-8q7YmY',
        description='Understand indexing, mutable properties, loops iteration, and items key-value structures.',
        duration='00:18',
        order=3
    )
    l4 = Lecture.objects.create(
        module=m4,
        title='4. Django MVC Setup',
        video_url='https://www.youtube.com/embed/9Oezn1rKhnA',
        youtube_id='9Oezn1rKhnA',
        description='Install Django packages, run local servers, and understand templates rendering views.',
        duration='00:20',
        order=4
    )
    
    LectureResource.objects.create(lecture=l1, title='Installation Guide Cheat Sheet', resource_type='PDF')
    LectureResource.objects.create(lecture=l2, title='Variables Code Samples', resource_type='ZIP')
    Assignment.objects.create(lecture=l2, title='Assignment 1: Variables Conversion Script', description='Write a python script that prompts user inputs, converts strings to numbers, and prints formatted output.', due_date=None)
    
    quiz1 = Quiz.objects.create(module=m1, title='Python Basics Assessment')
    QuizQuestion.objects.create(
        quiz=quiz1,
        question_text='Which of the following functions displays variable types in Python?',
        question_type='MCQ',
        options_json=json.dumps(['type()', 'print()', 'input()', 'len()']),
        correct_answer='type()'
    )
    QuizQuestion.objects.create(
        quiz=quiz1,
        question_text='Is Python a compiled language?',
        question_type='TF',
        options_json=json.dumps(['True', 'False']),
        correct_answer='False'
    )
    
    # Second course
    course2 = LMSCourse.objects.create(
        name='React Frontend Development',
        tagline='Build stunning single page apps using React Hooks, Router, and Context.',
        description='Learn modular frontend development. Master state triggers, component templates, and external API requests integrations.',
        duration='8 Weeks',
        difficulty='Beginner',
        banner_url='https://images.unsplash.com/photo-1633356122544-f134324a6cee?auto=format&fit=crop&w=1200&q=80'
    )
    rm1 = LMSModule.objects.create(course=course2, title='Module 1: Components and State', order=1)
    Lecture.objects.create(
        module=rm1,
        title='1. React Components & Props',
        video_url='https://www.youtube.com/embed/w7ejDZ8SWv8',
        youtube_id='w7ejDZ8SWv8',
        description='Deconstruct standard React functional components structures and properties passing.',
        duration='00:15',
        order=1
    )


@login_required
def lms_dashboard(request):
    seed_lms_data_if_empty()
    
    # Auto-enroll user in Python course if they have 0 enrollments
    if Enrollment.objects.filter(user=request.user).count() == 0:
        first_course = LMSCourse.objects.first()
        if first_course:
            Enrollment.objects.create(user=request.user, course=first_course)
            
    # Fetch all courses
    courses = LMSCourse.objects.all()
    
    enrolled_courses = []
    available_courses = []
    
    for c in courses:
        enrolled = Enrollment.objects.filter(user=request.user, course=c).first()
        
        lectures = Lecture.objects.filter(module__course=c)
        total_lectures = lectures.count()
        
        completed_count = LectureProgress.objects.filter(
            user=request.user,
            lecture__module__course=c,
            completed=True
        ).count()
        
        progress_pct = 0.0
        if total_lectures > 0:
            progress_pct = round((completed_count / total_lectures) * 100.0, 1)
            
        last_progress = LectureProgress.objects.filter(
            user=request.user,
            lecture__module__course=c
        ).order_by('-updated_at').first()
        
        continue_lecture = None
        if last_progress:
            continue_lecture = last_progress.lecture
        elif total_lectures > 0:
            continue_lecture = lectures.order_by('module__order', 'order').first()
            
        cert = Certificate.objects.filter(user=request.user, course=c).first()
        
        course_data = {
            'course': c,
            'progress_pct': progress_pct,
            'continue_lecture': continue_lecture,
            'total_lectures': total_lectures,
            'completed_lectures': completed_count,
            'remaining_lectures': total_lectures - completed_count,
            'last_accessed': enrolled.last_accessed if enrolled else None,
            'certificate': cert
        }
        
        if enrolled:
            enrolled_courses.append(course_data)
        else:
            available_courses.append(course_data)
            
    recent_notes = StudentNote.objects.filter(user=request.user).order_by('-updated_at')[:5]
    user_certs = Certificate.objects.filter(user=request.user)
    
    context = {
        'enrolled_courses': enrolled_courses,
        'available_courses': available_courses,
        'recent_notes': recent_notes,
        'certificates_earned': user_certs
    }
    context.update(get_erp_context(request))
    return render(request, 'lms_dashboard.html', context)


@login_required
@csrf_protect
def lms_enroll(request, course_id):
    if request.method == 'POST':
        course = get_object_or_404(LMSCourse, id=course_id)
        Enrollment.objects.get_or_create(user=request.user, course=course)
        messages.success(request, f"Successfully enrolled in {course.name}!")
    return redirect('lms_dashboard')


@login_required
def lms_lecture(request, lecture_id):
    lecture = get_object_or_404(Lecture, id=lecture_id)
    course = lecture.module.course
    
    # Access Control check: verify enrollment
    enrolled = Enrollment.objects.filter(user=request.user, course=course).first()
    if not enrolled:
        messages.error(request, f"You must be enrolled to view lectures inside {course.name}.")
        return redirect('lms_dashboard')
        
    # Update enrollment last accessed timestamp
    enrolled.save()
    
    # Fetch modules & lectures structure
    modules = LMSModule.objects.filter(course=course).prefetch_related('lectures')
    
    # Find or create lecture progress
    progress, created = LectureProgress.objects.get_or_create(user=request.user, lecture=lecture)
    if not created:
        # Increment visits
        pass
        
    # Load notes & bookmarks
    notes = StudentNote.objects.filter(user=request.user, lecture=lecture).order_by('-created_at')
    bookmarked = Bookmark.objects.filter(user=request.user, lecture=lecture).exists()
    
    # Calculate previous and next lectures for workspace navigation
    all_lectures = list(Lecture.objects.filter(module__course=course).order_by('module__order', 'order'))
    current_idx = -1
    for idx, l in enumerate(all_lectures):
        if l.id == lecture.id:
            current_idx = idx
            break
            
    prev_lecture = all_lectures[current_idx - 1] if current_idx > 0 else None
    next_lecture = all_lectures[current_idx + 1] if current_idx < len(all_lectures) - 1 else None
    
    # Calculate progress % for dashboard sidebar
    completed_count = LectureProgress.objects.filter(
        user=request.user,
        lecture__module__course=course,
        completed=True
    ).count()
    total_lectures = len(all_lectures)
    progress_pct = round((completed_count / total_lectures) * 100.0, 1) if total_lectures > 0 else 0.0
    
    quizzes = Quiz.objects.filter(module=lecture.module)
    assignments = Assignment.objects.filter(lecture=lecture)
    
    assignment_data = []
    for ass in assignments:
        submission = AssignmentSubmission.objects.filter(user=request.user, assignment=ass).first()
        assignment_data.append({
            'assignment': ass,
            'submission': submission
        })
        
    context = {
        'lecture': lecture,
        'course': course,
        'modules': modules,
        'progress': progress,
        'notes_list': notes,
        'bookmarked': bookmarked,
        'prev_lecture': prev_lecture,
        'next_lecture': next_lecture,
        'progress_pct': progress_pct,
        'quizzes': quizzes,
        'assignments_data': assignment_data,
        'resources': lecture.resources.all()
    }
    context.update(get_erp_context(request))
    return render(request, 'lms_lecture.html', context)


@login_required
@csrf_protect
def lms_update_progress(request, lecture_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'POST method required.'}, status=405)
        
    lecture = get_object_or_404(Lecture, id=lecture_id)
    progress, _ = LectureProgress.objects.get_or_create(user=request.user, lecture=lecture)
    
    try:
        data = json.loads(request.body)
        watch_pct = float(data.get('watch_percentage', progress.watch_percentage))
        resume_sec = float(data.get('resume_timestamp', progress.resume_timestamp))
        time_spent_incr = int(data.get('time_spent', 0))
        force_complete = data.get('force_complete', False)
        
        progress.watch_percentage = max(progress.watch_percentage, watch_pct)
        progress.resume_timestamp = resume_sec
        progress.time_spent += time_spent_incr
        
        if progress.watch_percentage >= 90.0 or force_complete:
            progress.completed = True
            progress.watch_percentage = 100.0
            
        progress.save()
        
        # Check course completion to auto-issue certificate
        course = lecture.module.course
        total_lectures = Lecture.objects.filter(module__course=course).count()
        completed_lectures = LectureProgress.objects.filter(
            user=request.user,
            lecture__module__course=course,
            completed=True
        ).count()
        
        issued_cert = False
        if total_lectures > 0 and completed_lectures == total_lectures:
            cert, created = Certificate.objects.get_or_create(
                user=request.user,
                course=course,
                defaults={'verification_id': f"BNT-2026-{request.user.id}-{course.id}"}
            )
            issued_cert = created
            
        return JsonResponse({
            'success': True,
            'completed': progress.completed,
            'issued_cert': issued_cert,
            'watch_percentage': progress.watch_percentage
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


@login_required
@csrf_protect
def lms_save_note(request, lecture_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'POST method required.'}, status=405)
        
    lecture = get_object_or_404(Lecture, id=lecture_id)
    
    try:
        data = json.loads(request.body)
        note_id = data.get('id')
        content = data.get('content', '').strip()
        timestamp = float(data.get('timestamp', 0.0))
        
        if not content:
            return JsonResponse({'success': False, 'message': 'Note content cannot be empty.'}, status=400)
            
        if note_id:
            note = get_object_or_404(StudentNote, id=note_id, user=request.user)
            note.content = content
            note.save()
        else:
            note = StudentNote.objects.create(
                user=request.user,
                lecture=lecture,
                content=content,
                timestamp=timestamp
            )
            
        return JsonResponse({
            'success': True,
            'note_id': note.id,
            'timestamp_str': format_seconds(note.timestamp),
            'timestamp_val': note.timestamp
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


@login_required
@csrf_protect
def lms_delete_note(request, lecture_id, note_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'POST method required.'}, status=405)
        
    note = get_object_or_404(StudentNote, id=note_id, user=request.user, lecture_id=lecture_id)
    note.delete()
    return JsonResponse({'success': True})


@login_required
def lms_export_note_markdown(request, lecture_id):
    lecture = get_object_or_404(Lecture, id=lecture_id)
    notes = StudentNote.objects.filter(user=request.user, lecture=lecture).order_by('timestamp')
    
    content = f"# Notes for Lecture: {lecture.title}\n"
    content += f"Course: {lecture.module.course.name} • Module: {lecture.module.title}\n"
    content += "========================================================================\n\n"
    
    import re
    for n in notes:
        time_str = format_seconds(n.timestamp)
        clean_text = re.sub('<[^<]+?>', '', n.content)
        content += f"### Timestamp: {time_str}\n{clean_text}\n\n---\n\n"
        
    response = HttpResponse(content, content_type='text/markdown')
    response['Content-Disposition'] = f'attachment; filename="LMS_Notes_Lecture_{lecture.id}.md"'
    return response


@login_required
def lms_export_note_pdf(request, lecture_id):
    lecture = get_object_or_404(Lecture, id=lecture_id)
    notes = StudentNote.objects.filter(user=request.user, lecture=lecture).order_by('timestamp')
    
    from reportlab.pdfgen import canvas
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    
    p.setFont("Helvetica-Bold", 20)
    p.drawString(50, 800, f"Lecture Notes: {lecture.title}")
    p.setFont("Helvetica", 11)
    p.drawString(50, 780, f"Course: {lecture.module.course.name}")
    p.line(50, 770, 550, 770)
    
    y = 740
    import re
    for n in notes:
        if y < 100:
            p.showPage()
            y = 780
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, y, f"Timestamp: {format_seconds(n.timestamp)}")
        y -= 20
        
        p.setFont("Helvetica", 10)
        clean_text = re.sub('<[^<]+?>', '', n.content)
        lines = clean_text.split('\n')
        for line in lines:
            if y < 100:
                p.showPage()
                y = 780
            p.drawString(60, y, line[:90])
            y -= 15
        y -= 15
        
    p.showPage()
    p.save()
    
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="LMS_Notes_Lecture_{lecture.id}.pdf"'
    return response


@login_required
@csrf_protect
def lms_toggle_bookmark(request, lecture_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'POST method required.'}, status=405)
        
    lecture = get_object_or_404(Lecture, id=lecture_id)
    bookmark_query = Bookmark.objects.filter(user=request.user, lecture=lecture)
    
    if bookmark_query.exists():
        bookmark_query.delete()
        bookmarked = False
        msg = f"Bookmark removed for {lecture.title}"
    else:
        try:
            data = json.loads(request.body)
            sec = float(data.get('timestamp', 0.0))
        except Exception:
            sec = 0.0
            
        Bookmark.objects.create(
            user=request.user,
            lecture=lecture,
            title=f"Bookmark at {format_seconds(sec)}",
            timestamp=sec
        )
        bookmarked = True
        msg = f"Bookmark saved at {format_seconds(sec)}!"
        
    return JsonResponse({
        'success': True,
        'bookmarked': bookmarked,
        'message': msg
    })


@login_required
def lms_bookmarks(request):
    bookmarks = Bookmark.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'bookmarks_list': bookmarks
    }
    context.update(get_erp_context(request))
    return render(request, 'lms_bookmarks.html', context)


@login_required
@csrf_protect
def lms_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.questions.all()
    
    if request.method == 'POST':
        score = 0
        total_questions = questions.count()
        
        for q in questions:
            user_ans = request.POST.get(f"question_{q.id}", '').strip().lower()
            correct_ans = q.correct_answer.strip().lower()
            if user_ans == correct_ans:
                score += 1
                
        percentage = 0.0
        if total_questions > 0:
            percentage = round((score / total_questions) * 100.0, 1)
            
        passed = percentage >= 70.0
        
        QuizAnswer.objects.create(
            user=request.user,
            quiz=quiz,
            score=percentage,
            passed=passed
        )
        
        messages.success(request, f"Quiz submitted! Score: {percentage}% ({'PASSED' if passed else 'FAILED'})")
        return redirect('lms_lecture', lecture_id=quiz.module.lectures.first().id)
        
    context = {
        'quiz': quiz,
        'questions_list': []
    }
    for q in questions:
        context['questions_list'].append({
            'id': q.id,
            'text': q.question_text,
            'type': q.question_type,
            'options': json.loads(q.options_json) if q.options_json else []
        })
        
    context.update(get_erp_context(request))
    return render(request, 'lms_quiz.html', context)


@login_required
@csrf_protect
def lms_submit_assignment(request, assignment_id):
    if request.method != 'POST':
        return HttpResponse("POST request required.", status=405)
        
    assignment = get_object_or_404(Assignment, id=assignment_id)
    github_link = request.POST.get('github_link', '').strip()
    project_url = request.POST.get('project_url', '').strip()
    file = request.FILES.get('submission_file')
    
    if not (github_link or project_url or file):
        messages.error(request, "Please provide either a GitHub repository link, project URL, or file upload.")
        return redirect('lms_lecture', lecture_id=assignment.lecture.id)
        
    sub, _ = AssignmentSubmission.objects.get_or_create(user=request.user, assignment=assignment)
    sub.github_link = github_link
    sub.project_url = project_url
    if file:
        sub.file = file
    sub.status = 'submitted'
    sub.save()
    
    messages.success(request, "Assignment submitted successfully!")
    return redirect('lms_lecture', lecture_id=assignment.lecture.id)


@login_required
def lms_download_certificate(request, cert_id):
    cert = get_object_or_404(Certificate, id=cert_id, user=request.user)
    
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter, landscape
    
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=landscape(letter))
    
    p.setStrokeColorRGB(0.38, 0.40, 0.94)
    p.setLineWidth(6)
    p.rect(30, 30, 732, 552)
    
    p.setStrokeColorRGB(0.66, 0.33, 0.97)
    p.setLineWidth(2)
    p.rect(40, 40, 712, 532)
    
    p.setFont("Helvetica-Bold", 36)
    p.setFillColorRGB(0.06, 0.09, 0.19)
    p.drawCentredString(396, 450, "CERTIFICATE OF COMPLETION")
    
    p.setFont("Helvetica", 14)
    p.drawCentredString(396, 410, "This is proudly presented to")
    
    p.setFont("Helvetica-Bold", 28)
    p.setFillColorRGB(0.38, 0.40, 0.94)
    student_name = request.user.profile.full_name if hasattr(request.user, 'profile') and request.user.profile.full_name else request.user.username
    p.drawCentredString(396, 350, student_name.upper())
    
    p.setFont("Helvetica", 14)
    p.setFillColorRGB(0.06, 0.09, 0.19)
    p.drawCentredString(396, 290, "for successfully completing the core training curriculum and projects of the")
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(396, 260, f"{cert.course.name.upper()}")
    
    p.setStrokeColorRGB(0.7, 0.7, 0.7)
    p.setLineWidth(1)
    p.line(200, 220, 592, 220)
    
    p.setFont("Helvetica", 11)
    p.setFillColorRGB(0.4, 0.4, 0.4)
    p.drawString(100, 150, f"Completion Date: {cert.completion_date.strftime('%Y-%m-%d')}")
    p.drawRightString(692, 150, f"Verification ID: {cert.verification_id}")
    
    p.drawCentredString(396, 120, "BlueNova Technologies Cohort Coordinator")
    p.line(296, 140, 496, 140)
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="BlueNova_Certificate_{cert.verification_id}.pdf"'
    return response


@login_required
@admin_required
def lms_admin_panel(request):
    courses = LMSCourse.objects.all()
    modules = LMSModule.objects.all()
    lectures = Lecture.objects.all()
    progress_metrics = LectureProgress.objects.all().order_by('-updated_at')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'create_course':
            name = request.POST.get('name', '').strip()
            tagline = request.POST.get('tagline', '').strip()
            desc = request.POST.get('description', '').strip()
            banner = request.POST.get('banner_url', '').strip() or 'https://images.unsplash.com/photo-1515879218367-8466d910aaa4?auto=format&fit=crop&w=400&q=80'
            if name:
                LMSCourse.objects.create(name=name, tagline=tagline, description=desc, banner_url=banner)
                messages.success(request, f"Course '{name}' created successfully!")
        elif action == 'create_module':
            course_id = request.POST.get('course_id')
            title = request.POST.get('title', '').strip()
            order = int(request.POST.get('order', 1))
            if course_id and title:
                course = get_object_or_404(LMSCourse, id=course_id)
                LMSModule.objects.create(course=course, title=title, order=order)
                messages.success(request, f"Module '{title}' created successfully!")
        elif action == 'create_lecture':
            module_id = request.POST.get('module_id')
            title = request.POST.get('title', '').strip()
            video = request.POST.get('video_url', '').strip() or 'https://www.w3schools.com/html/mov_bbb.mp4'
            desc = request.POST.get('description', '').strip()
            dur = request.POST.get('duration', '').strip() or '15:00'
            order = int(request.POST.get('order', 1))
            if module_id and title:
                module = get_object_or_404(LMSModule, id=module_id)
                Lecture.objects.create(module=module, title=title, video_url=video, description=desc, duration=dur, order=order)
                messages.success(request, f"Lecture '{title}' added successfully!")
                
        return redirect('lms_admin_panel')
        
    context = {
        'courses_list': courses,
        'modules_list': modules,
        'lectures_list': lectures,
        'progress_list': progress_metrics
    }
    context.update(get_erp_context(request))
    return render(request, 'lms_admin.html', context)
