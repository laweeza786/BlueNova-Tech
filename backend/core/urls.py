from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/applications/', views.admin_applications_view, name='admin_applications'),
    path('admin-dashboard/applications/action/<int:app_id>/<str:action_type>/', views.application_action_view, name='application_action'),
    path('admin-dashboard/applications/resume/<int:app_id>/', views.download_application_resume_view, name='download_application_resume'),
    
    # Profile Workspace
    path('profile/', views.profile_view, name='profile'),
    path('profile/<int:user_id>/', views.profile_view, name='profile_detail'),
    path('edit-profile/', views.edit_profile_view, name='edit_profile'),
    
    # Document Workspace
    path('upload-files/', views.upload_file, name='upload_files'),
    path('delete-file/<int:file_id>/', views.delete_file, name='delete_file'),
    
    # User CRUD
    path('user-management/', views.user_management, name='user_management'),
    
    # Correspondence
    path('messages/', views.messages_view, name='messages'),
    
    # Milestones & Alerts
    path('history/', views.history_view, name='history'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('delete-notification/<int:notif_id>/', views.delete_notification, name='delete_notification'),
    
    # Audit & Setup
    path('activity-logs/', views.activity_logs_view, name='activity_logs'),
    path('data-management/', views.data_management_view, name='data_management'),
    path('reset-database/', views.reset_database_view, name='reset_database'),
    
    # Support & Reviews
    path('help-center/', views.help_center_view, name='help_center'),
    path('feedback/', views.feedback_view, name='feedback'),
    
    # Reports
    path('reports/', views.reports_view, name='reports'),
    path('reports/csv/', views.export_csv_view, name='export_csv'),
    path('reports/pdf/', views.export_pdf_view, name='export_pdf'),
    
    # Global search and analytics
    path('search/', views.search_view, name='search'),
    path('analytics/', views.analytics_view, name='analytics'),
    path('settings/', views.settings_view, name='settings'),
    path('profile/upload-picture/', views.upload_profile_picture, name='upload_profile_picture'),
    path('profile/remove-picture/', views.remove_profile_picture, name='remove_profile_picture'),
    
    # Lecture LMS Workspace
    path('learning/', views.lms_dashboard, name='lms_dashboard'),
    path('learning/enroll/<int:course_id>/', views.lms_enroll, name='lms_enroll'),
    path('learning/lecture/<int:lecture_id>/', views.lms_lecture, name='lms_lecture'),
    path('learning/lecture/<int:lecture_id>/progress/', views.lms_update_progress, name='lms_update_progress'),
    path('learning/lecture/<int:lecture_id>/note/save/', views.lms_save_note, name='lms_save_note'),
    path('learning/lecture/<int:lecture_id>/note/delete/<int:note_id>/', views.lms_delete_note, name='lms_delete_note'),
    path('learning/lecture/<int:lecture_id>/note/export/md/', views.lms_export_note_markdown, name='lms_export_note_markdown'),
    path('learning/lecture/<int:lecture_id>/note/export/pdf/', views.lms_export_note_pdf, name='lms_export_note_pdf'),
    path('learning/lecture/<int:lecture_id>/bookmark/', views.lms_toggle_bookmark, name='lms_toggle_bookmark'),
    path('learning/bookmarks/', views.lms_bookmarks, name='lms_bookmarks'),
    path('learning/quiz/<int:quiz_id>/', views.lms_quiz, name='lms_quiz'),
    path('learning/assignment/submit/<int:assignment_id>/', views.lms_submit_assignment, name='lms_submit_assignment'),
    path('learning/certificate/<int:cert_id>/download/', views.lms_download_certificate, name='lms_download_certificate'),
    path('learning/admin/', views.lms_admin_panel, name='lms_admin_panel'),
]
