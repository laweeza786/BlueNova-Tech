import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import Profile, Setting, History, Notification, UploadedFile, Message

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with default admin and mock user profiles.'

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding database...")
        
        # 1. Create Admin User
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@bluenova.com',
                password='admin',
                role='admin'
            )
            Profile.objects.create(
                user=admin_user,
                full_name='BlueNova Administrator',
                track='Software Engineering',
                status='approved'
            )
            Setting.objects.create(user=admin_user, theme='dark')
            self.stdout.write(self.style.SUCCESS("Superuser 'admin' created successfully."))
        else:
            self.stdout.write("Admin user already exists.")
            admin_user = User.objects.get(username='admin')

        # 2. Create Intern (John Doe)
        if not User.objects.filter(username='johndoe').exists():
            john = User.objects.create_user(
                username='johndoe',
                email='john.doe@example.com',
                password='password',
                role='user'
            )
            profile = Profile.objects.create(
                user=john,
                full_name='John Doe',
                phone='+1 (555) 019-2834',
                track='Software Engineering',
                bio='Passionate software developer interested in scalable cloud solutions, full stack web apps, and databases. Excited to learn at BlueNova Technologies.',
                academic_background='B.S. in Computer Science, Stanford University',
                skills='Python, Javascript, React, SQL, HTML/CSS',
                status='approved'
            )
            Setting.objects.create(user=john, theme='dark')
            
            # Default alerts
            Notification.objects.create(
                user=john,
                title='Internship Approved',
                message='Congratulations! Your internship application for the Software Engineering track has been approved.',
                level='success'
            )
            Notification.objects.create(
                user=john,
                title='Upcoming Review',
                message='Your first mid-term performance evaluation is scheduled for next Tuesday.',
                level='info'
            )
            
            # Milestone history
            History.objects.create(
                user=john,
                milestone_name='Onboarding Completed',
                description='Successfully set up the ERP account, completed profile info, and uploaded initial documents.'
            )
            History.objects.create(
                user=john,
                milestone_name='Milestone 1 Submitted',
                description='Uploaded project plan and codebase zip files for initial grading review.'
            )
            
            # Message thread
            Message.objects.create(
                sender=john,
                receiver=admin_user,
                subject='Question regarding milestone',
                body='Hello Admin, is it okay if I upload the zip file for task 1 tomorrow morning? Thank you.',
                is_read=True
            )
            Message.objects.create(
                sender=admin_user,
                receiver=john,
                subject='Re: Question regarding milestone',
                body='Sure John. Late uploads are fine as long as they are completed before the weekly review on Friday.'
            )
            
            self.stdout.write(self.style.SUCCESS("Intern 'johndoe' created successfully."))
        else:
            self.stdout.write("Intern johndoe already exists.")

        self.stdout.write(self.style.SUCCESS("Seeding operation completed successfully."))
