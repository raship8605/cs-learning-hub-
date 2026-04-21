from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    role = models.CharField(max_length=10, default='student')
    profile_pic = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    college_name = models.CharField(max_length=200, blank=True)
    enrollment_no = models.CharField(max_length=50, blank=True)
    
    def __str__(self):
        return self.username

class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class YouTubeVideo(models.Model):
    title = models.CharField(max_length=200)
    youtube_id = models.CharField(max_length=50)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    views = models.IntegerField(default=0)
    
    def __str__(self):
        return self.title

class Note(models.Model):
    title = models.CharField(max_length=200)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    file = models.FileField(upload_to='notes/')
    downloads = models.IntegerField(default=0)
    
    def __str__(self):
        return self.title

class Quiz(models.Model):
    title = models.CharField(max_length=200)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    duration_minutes = models.IntegerField(default=30)
    total_marks = models.IntegerField(default=100)
    passing_marks = models.IntegerField(default=40)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    option_a = models.CharField(max_length=500)
    option_b = models.CharField(max_length=500)
    option_c = models.CharField(max_length=500)
    option_d = models.CharField(max_length=500)
    correct_answer = models.CharField(max_length=1)
    
    def __str__(self):
        return self.question_text[:50]

class QuizAttempt(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    total_marks = models.IntegerField(default=0)
    percentage = models.FloatField(default=0)
    passed = models.BooleanField(default=False)
    attempted_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.student.username} - {self.quiz.title}"

class PreviousYearPaper(models.Model):
    title = models.CharField(max_length=200)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    year = models.IntegerField()
    semester = models.CharField(max_length=20, choices=[
        ('1','Semester 1'),('2','Semester 2'),('3','Semester 3'),
        ('4','Semester 4'),('5','Semester 5'),('6','Semester 6'),
        ('7','Semester 7'),('8','Semester 8')
    ])
    file = models.FileField(upload_to='papers/')
    downloads = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.title} - {self.year}"

class UserActivity(models.Model):
    ACTIVITY_TYPES = (
        ('video_watch', 'Video Watched'),
        ('note_download', 'Note Downloaded'),
        ('quiz_taken', 'Quiz Taken'),
        ('paper_download', 'Paper Downloaded'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    content_type = models.CharField(max_length=50)
    content_id = models.IntegerField()
    content_title = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.activity_type}"

class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    content_type = models.CharField(max_length=20)
    content_id = models.IntegerField()
    content_title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'content_type', 'content_id']
    
    def __str__(self):
        return f"{self.user.username} - {self.content_title}"