from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Avg, Q
from django.http import HttpResponse, HttpResponseRedirect
from .models import *
from .forms import *
from .models import UserActivity
# Home Page
def index(request):
    subjects = Subject.objects.all()[:6]
    featured_videos = YouTubeVideo.objects.all().order_by('-views')[:6]
    recent_quizzes = Quiz.objects.filter(is_active=True)[:4]
    
    context = {
        'subjects': subjects,
        'featured_videos': featured_videos,
        'recent_quizzes': recent_quizzes,
    }
    return render(request, 'index.html', context)

# User Registration
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to CS Learning Hub.')
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

# User Login
def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'accounts/login.html')

# User Logout
def user_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('index')

# Dashboard
@login_required
def dashboard(request):
    # Statistics
    stats = {
        'videos_watched': UserActivity.objects.filter(user=request.user, activity_type='video_watch').count(),
        'notes_downloaded': UserActivity.objects.filter(user=request.user, activity_type='note_download').count(),
        'quizzes_taken': QuizAttempt.objects.filter(student=request.user).count(),
        'avg_score': QuizAttempt.objects.filter(student=request.user).aggregate(avg=Avg('percentage'))['avg'] or 0,
    }
    
    recent_activities = UserActivity.objects.filter(user=request.user).order_by('-timestamp')[:10]
    
    context = {
        'stats': stats,
        'recent_activities': recent_activities,
        'user': request.user,
    }
    return render(request, 'dashboard/student_dashboard.html', context)

# User Profile
@login_required
def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'accounts/profile.html', {'form': form, 'user': request.user})

# Video List
@login_required
def video_list(request):
    subject_id = request.GET.get('subject')
    search_query = request.GET.get('search')
    
    videos = YouTubeVideo.objects.all()
    
    if subject_id:
        videos = videos.filter(subject_id=subject_id)
    if search_query:
        videos = videos.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query))
    
    subjects = Subject.objects.all()
    context = {
        'videos': videos,
        'subjects': subjects,
        'selected_subject': subject_id,
    }
    return render(request, 'videos/video_list.html', context)

# Video Detail
@login_required
def video_detail(request, video_id):
    video = get_object_or_404(YouTubeVideo, id=video_id)
    video.views += 1
    video.save()
    
    # Log activity
    UserActivity.objects.get_or_create(
        user=request.user,
        activity_type='video_watch',
        content_type='video',
        content_id=video.id,
        defaults={'content_title': video.title}
    )
    
    related_videos = YouTubeVideo.objects.filter(subject=video.subject).exclude(id=video.id)[:4]
    
    context = {
        'video': video,
        'related_videos': related_videos,
    }
    return render(request, 'videos/video_detail.html', context)

# Notes List
@login_required
def notes_list(request):
    subject_id = request.GET.get('subject')
    search_query = request.GET.get('search')
    
    notes = Note.objects.all()
    
    if subject_id:
        notes = notes.filter(subject_id=subject_id)
    if search_query:
        notes = notes.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query))
    
    subjects = Subject.objects.all()
    
    context = {
        'notes': notes,
        'subjects': subjects,
        'selected_subject': subject_id,
    }
    return render(request, 'notes/notes_list.html', context)

@login_required
def download_note(request, note_id):
    note = get_object_or_404(Note, id=note_id)
    note.downloads += 1
    note.save()
    
    # Log activity
    UserActivity.objects.get_or_create(
        user=request.user,
        activity_type='note_download',
        content_type='note',
        content_id=note.id,
        defaults={'content_title': note.title}
    )
    
    return redirect(note.file.url)
@login_required
def quiz_list(request):
    quizzes = Quiz.objects.filter(is_active=True)
    subjects = Subject.objects.all()
    
    # Add attempt info for each quiz
    for quiz in quizzes:
        quiz.attempts = QuizAttempt.objects.filter(student=request.user, quiz=quiz)
    
    context = {
        'quizzes': quizzes,
        'subjects': subjects,
    }
    return render(request, 'quizzes/quiz_list.html', context)

# Take Quiz
@login_required
def take_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    # Check if already attempted
    if QuizAttempt.objects.filter(student=request.user, quiz=quiz).exists():
        messages.warning(request, 'You have already taken this quiz!')
        return redirect('quiz_list')
    
    if request.method == 'POST':
        score = 0
        total_marks = 0
        
        for question in quiz.questions.all():
            selected_answer = request.POST.get(f'q{question.id}')
            if selected_answer == question.correct_answer:
                score += 1
            total_marks += 1
        
        percentage = (score / total_marks) * 100 if total_marks > 0 else 0
        passed = percentage >= quiz.passing_marks
        
        attempt = QuizAttempt.objects.create(
            student=request.user,
            quiz=quiz,
            score=score,
            total_marks=total_marks,
            percentage=percentage,
            passed=passed
        )
        
        UserActivity.objects.create(
            user=request.user,
            activity_type='quiz_taken',
            content_type='quiz',
            content_id=quiz.id,
            content_title=quiz.title
        )
        
        messages.success(request, f'Quiz submitted! Your score: {score}/{total_marks}')
        return redirect('quiz_result', attempt_id=attempt.id)
    
    questions = quiz.questions.all()
    context = {
        'quiz': quiz,
        'questions': questions,
    }
    return render(request, 'quizzes/take_quiz.html', context)

# Quiz Result
@login_required
def quiz_result(request, attempt_id):
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, student=request.user)
    return render(request, 'quizzes/quiz_result.html', {'attempt': attempt})

# Papers List
@login_required
def papers_list(request):
    subject_id = request.GET.get('subject')
    papers = PreviousYearPaper.objects.all()
    
    if subject_id:
        papers = papers.filter(subject_id=subject_id)
    
    subjects = Subject.objects.all()
    context = {
        'papers': papers,
        'subjects': subjects,
        'selected_subject': subject_id,
    }
    return render(request, 'papers/papers_list.html', context)

# Download Paper
@login_required
def download_paper(request, paper_id):
    paper = get_object_or_404(PreviousYearPaper, id=paper_id)
    paper.downloads += 1
    paper.save()
    
    UserActivity.objects.get_or_create(
        user=request.user,
        activity_type='paper_download',
        content_type='paper',
        content_id=paper.id,
        defaults={'content_title': paper.title}
    )
    
    return HttpResponseRedirect(paper.file.url)

# My Progress
@login_required
def my_progress(request):
    quiz_attempts = QuizAttempt.objects.filter(student=request.user).order_by('-attempted_at')
    
    # Subject-wise performance
    subject_performance = []
    for subject in Subject.objects.all():
        avg_score = QuizAttempt.objects.filter(
            student=request.user, quiz__subject=subject
        ).aggregate(avg=Avg('percentage'))['avg']
        if avg_score:
            subject_performance.append({
                'name': subject.name,
                'score': round(avg_score, 1)
            })
    
    context = {
        'quiz_attempts': quiz_attempts,
        'total_quizzes': quiz_attempts.count(),
        'average_score': quiz_attempts.aggregate(Avg('percentage'))['percentage__avg'] or 0,
        'subject_performance': subject_performance,
    }
    return render(request, 'progress/my_progress.html', context)