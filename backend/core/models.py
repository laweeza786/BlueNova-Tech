from django.db import models
from django.conf import settings

class Profile(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending Review'),
        ('approved', 'Cohort Approved'),
        ('rejected', 'Application Rejected'),
    )
    TRACK_CHOICES = (
        ('Software Engineering', 'Software Engineering'),
        ('UI/UX Design', 'UI/UX Design'),
        ('Data Analytics', 'Data Analytics'),
    )
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    track = models.CharField(max_length=50, choices=TRACK_CHOICES, blank=True)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', default='profile_pictures/default-avatar.png')
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    skills = models.TextField(blank=True, help_text='Comma separated list of skills')
    academic_background = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.user.username}'s Profile"


class UploadedFile(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='uploads/')
    file_name = models.CharField(max_length=255)
    file_size = models.IntegerField(help_text='File size in bytes')
    file_type = models.CharField(max_length=50, help_text='File extension')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file_name


class Notification(models.Model):
    LEVEL_CHOICES = (
        ('info', 'Information'),
        ('success', 'Success alert'),
        ('warning', 'Warning alert'),
        ('danger', 'Error alert'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    level = models.CharField(max_length=15, choices=LEVEL_CHOICES, default='info')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.title}"


class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages')
    subject = models.CharField(max_length=200, default='Direct ERP Message')
    body = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"From {self.sender.username} to {self.receiver.username} - {self.subject}"


class ActivityLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='logs')
    action = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField()
    user_agent = models.CharField(max_length=500, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        username = self.user.username if self.user else "Anonymous"
        return f"{username} - {self.action} at {self.timestamp}"


class Feedback(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='feedbacks')
    subject = models.CharField(max_length=200)
    message = models.TextField()
    rating = models.IntegerField(help_text='Rating from 1 to 5 stars')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} feedback - {self.subject}"


class Setting(models.Model):
    THEME_CHOICES = (
        ('light', 'Light Mode'),
        ('dark', 'Dark Mode'),
    )
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='settings')
    theme = models.CharField(max_length=10, choices=THEME_CHOICES, default='dark')
    email_notifications = models.BooleanField(default=True)
    activity_digest = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username}'s Settings"


class History(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='milestones')
    milestone_name = models.CharField(max_length=200)
    description = models.TextField()
    achieved_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} achieved {self.milestone_name}"


class Report(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    file_path = models.CharField(max_length=255)
    report_type = models.CharField(max_length=50)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reports')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class InternshipApplication(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=50)
    college = models.CharField(max_length=255)
    branch = models.CharField(max_length=150)
    semester = models.CharField(max_length=50)
    city = models.CharField(max_length=100)
    resume = models.FileField(upload_to='resumes/')
    cover_letter = models.TextField(blank=True, null=True)
    course = models.CharField(max_length=150)
    batch = models.CharField(max_length=100)
    mode = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    submission_date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='applications')

    def __str__(self):
        return f"{self.full_name} - {self.course}"


class LMSCourse(models.Model):
    name = models.CharField(max_length=200)
    tagline = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    duration = models.CharField(max_length=50, default='12 Weeks')
    difficulty = models.CharField(max_length=50, default='Intermediate')
    banner_url = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return self.name


class Enrollment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(LMSCourse, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'course')

    def __str__(self):
        return f"{self.user.username} enrolled in {self.course.name}"


class LMSModule(models.Model):
    course = models.ForeignKey(LMSCourse, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    order = models.IntegerField(default=1)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.course.name} - {self.title}"


class Lecture(models.Model):
    module = models.ForeignKey(LMSModule, on_delete=models.CASCADE, related_name='lectures')
    title = models.CharField(max_length=200)
    video_url = models.CharField(max_length=500, help_text='MP4 link, YouTube/Vimeo embed, or local path')
    youtube_id = models.CharField(max_length=100, blank=True, help_text='YouTube Video ID (e.g. QX3M80G5S2U) for API tracking')
    description = models.TextField(blank=True)
    duration = models.CharField(max_length=50, default='15:00')
    order = models.IntegerField(default=1)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.module.title} - {self.title}"


class LectureProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lms_progress')
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE, related_name='progress')
    watch_percentage = models.FloatField(default=0.0)
    completed = models.BooleanField(default=False)
    resume_timestamp = models.FloatField(default=0.0, help_text='Seconds position')
    time_spent = models.IntegerField(default=0, help_text='Seconds spent')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'lecture')

    def __str__(self):
        return f"{self.user.username} - {self.lecture.title} ({self.watch_percentage}%)"


class LectureResource(models.Model):
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE, related_name='resources')
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='lms_resources/', blank=True, null=True)
    resource_type = models.CharField(max_length=50, default='PDF')

    def __str__(self):
        return self.title


class StudentNote(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lms_notes')
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE, related_name='notes')
    content = models.TextField()
    timestamp = models.FloatField(default=0.0, help_text='Video playback stamp in seconds')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Note on {self.lecture.title}"


class Bookmark(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lms_bookmarks')
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE, related_name='bookmarks')
    title = models.CharField(max_length=200, blank=True)
    timestamp = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} bookmarked {self.lecture.title}"


class Assignment(models.Model):
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.title


class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='assignment_submissions')
    file = models.FileField(upload_to='assignment_submissions/', blank=True, null=True)
    github_link = models.CharField(max_length=300, blank=True)
    project_url = models.CharField(max_length=300, blank=True)
    status = models.CharField(max_length=50, default='pending')
    grade = models.CharField(max_length=50, blank=True)
    feedback = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.assignment.title}"


class Quiz(models.Model):
    module = models.ForeignKey(LMSModule, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=200)

    def __str__(self):
        return self.title


class QuizQuestion(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=50, default='MCQ')  # MCQ, TF, CODE
    options_json = models.TextField(help_text='JSON array string of choices')
    correct_answer = models.CharField(max_length=255)

    def __str__(self):
        return self.question_text[:50]


class QuizAnswer(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quiz_scores')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='answers')
    score = models.FloatField(default=0.0)
    passed = models.BooleanField(default=False)
    taken_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} took {self.quiz.title} ({self.score}%)"


class Certificate(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='certificates')
    course = models.ForeignKey(LMSCourse, on_delete=models.CASCADE, related_name='certificates')
    verification_id = models.CharField(max_length=100, unique=True)
    completion_date = models.DateField(auto_now_add=True)
    download_file = models.FileField(upload_to='certificates/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.course.name} Certificate"
