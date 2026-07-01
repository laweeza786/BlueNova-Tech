from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from core.models import Profile, Setting
import json
import html

User = get_user_model()

class ERPTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create Admin user
        self.admin = User.objects.create_superuser(
            username='admin_test',
            email='admin_test@bluenova.com',
            password='testpassword',
            role='admin'
        )
        Profile.objects.create(user=self.admin, full_name='Admin Test', track='Software Engineering', status='approved')
        Setting.objects.create(user=self.admin, theme='dark')
        
        # Create standard Intern user
        self.intern = User.objects.create_user(
            username='intern_test',
            email='intern_test@bluenova.com',
            password='testpassword',
            role='user'
        )
        Profile.objects.create(user=self.intern, full_name='Intern Test', track='Software Engineering', status='pending')
        Setting.objects.create(user=self.intern, theme='dark')

    def test_login_success(self):
        response = self.client.post(reverse('login'), {
            'username': 'intern_test',
            'password': 'testpassword'
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])

    def test_login_fail(self):
        response = self.client.post(reverse('login'), {
            'username': 'intern_test',
            'password': 'wrongpassword'
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()['success'])

    def test_admin_only_view_denied_to_intern(self):
        # Log in as Intern
        self.client.login(username='intern_test', password='testpassword')
        response = self.client.get(reverse('admin_dashboard'))
        # Should redirect to 404 page (or dashboard depending on decorator logic)
        self.assertEqual(response.status_code, 302)

    def test_admin_view_allowed_to_admin(self):
        # Log in as Admin
        self.client.login(username='admin_test', password='testpassword')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_course_detail_resolves_valid_slug(self):
        response = self.client.get(reverse('course_detail', args=['web-development']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Web Development')

    def test_course_detail_404_invalid_slug(self):
        response = self.client.get(reverse('course_detail', args=['non-existent-course-slug']))
        self.assertEqual(response.status_code, 404)

    def test_internship_application_form_get(self):
        response = self.client.get(reverse('apply') + '?course=django-development')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Django Development')

    def test_internship_application_form_submit(self):
        # Create a mock resume file
        import io
        mock_file = io.BytesIO(b"dummy resume PDF content")
        mock_file.name = "john_doe_resume.pdf"

        # Submit POST application
        response = self.client.post(reverse('apply'), {
            'full_name': 'John Applicant',
            'email': 'new_applicant@example.com',
            'phone': '1234567890',
            'college': 'Harvard University',
            'branch': 'Computer Science',
            'semester': '6',
            'city': 'Boston',
            'course': 'Python Development',
            'batch': 'July 2026 Cohort',
            'mode': 'Hybrid',
            'resume': mock_file
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        
        # Verify model object creation in SQLite database
        from core.models import InternshipApplication
        self.assertTrue(InternshipApplication.objects.filter(email='new_applicant@example.com').exists())

    def test_admin_applications_auth_required(self):
        # Anonymous user gets redirected to login
        response = self.client.get(reverse('admin_applications'))
        self.assertEqual(response.status_code, 302)

    def test_lms_dashboard_auth_required(self):
        response = self.client.get(reverse('lms_dashboard'))
        self.assertEqual(response.status_code, 302)

    def test_lms_dashboard_loads_for_logged_in_user(self):
        self.client.login(username='intern_test', password='testpassword')
        response = self.client.get(reverse('lms_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Python Full Stack Development')

    def test_lms_lecture_page_loads(self):
        self.client.login(username='intern_test', password='testpassword')
        # Trigger dashboard load once to ensure database seeding
        self.client.get(reverse('lms_dashboard'))
        
        from core.models import Lecture
        lec = Lecture.objects.first()
        self.assertIsNotNone(lec)
        
        response = self.client.get(reverse('lms_lecture', args=[lec.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, html.escape(lec.title))

    def test_lms_update_progress_endpoint(self):
        self.client.login(username='intern_test', password='testpassword')
        self.client.get(reverse('lms_dashboard'))
        
        from core.models import Lecture, LectureProgress
        lec = Lecture.objects.first()
        
        response = self.client.post(
            reverse('lms_update_progress', args=[lec.id]),
            data=json.dumps({'watch_percentage': 50.0, 'resume_timestamp': 100.0, 'time_spent': 5}),
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        
        progress = LectureProgress.objects.get(user=self.intern, lecture=lec)
        self.assertEqual(progress.watch_percentage, 50.0)
        self.assertEqual(progress.resume_timestamp, 100.0)

    def test_lms_auto_save_notes_endpoint(self):
        self.client.login(username='intern_test', password='testpassword')
        self.client.get(reverse('lms_dashboard'))
        
        from core.models import Lecture, StudentNote
        lec = Lecture.objects.first()
        
        response = self.client.post(
            reverse('lms_save_note', args=[lec.id]),
            data=json.dumps({'content': 'This is a test note', 'timestamp': 30.0}),
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        
        note = StudentNote.objects.get(user=self.intern, lecture=lec)
        self.assertEqual(note.content, 'This is a test note')
        self.assertEqual(note.timestamp, 30.0)

    def test_lms_export_notes_endpoints(self):
        self.client.login(username='intern_test', password='testpassword')
        self.client.get(reverse('lms_dashboard'))
        from core.models import Lecture
        lec = Lecture.objects.first()
        
        # Test markdown export
        md_response = self.client.get(reverse('lms_export_note_markdown', args=[lec.id]))
        self.assertEqual(md_response.status_code, 200)
        self.assertEqual(md_response['Content-Type'], 'text/markdown')
        
        # Test PDF export
        pdf_response = self.client.get(reverse('lms_export_note_pdf', args=[lec.id]))
        self.assertEqual(pdf_response.status_code, 200)
        self.assertEqual(pdf_response['Content-Type'], 'application/pdf')

    def test_lms_enrollment_restrictions(self):
        # Create a new user with no enrollments
        new_user = User.objects.create_user(username='new_student', password='testpassword')
        Profile.objects.create(user=new_user)
        
        # Log in the user
        self.client.login(username='new_student', password='testpassword')
        
        # Seed courses
        self.client.get(reverse('lms_dashboard'))
        
        from core.models import Lecture, Enrollment
        lec = Lecture.objects.first()
        course = lec.module.course
        
        # Remove any automatic enrollment created during dashboard load for testing purposes
        Enrollment.objects.filter(user=new_user, course=course).delete()
        
        # Requesting lecture page should redirect back to dashboard due to lack of enrollment
        response = self.client.get(reverse('lms_lecture', args=[lec.id]))
        self.assertEqual(response.status_code, 302)
