from django.urls import path
from . import views

urlpatterns = [
    # Home & Auth
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    
    # Videos
    path('videos/', views.video_list, name='video_list'),
    path('video/<int:video_id>/', views.video_detail, name='video_detail'),
    
    # Notes
    path('notes/', views.notes_list, name='notes_list'),
    path('note/download/<int:note_id>/', views.download_note, name='download_note'),
    
    # Quizzes
    path('quizzes/', views.quiz_list, name='quiz_list'),
    path('quiz/<int:quiz_id>/take/', views.take_quiz, name='take_quiz'),
    path('quiz/result/<int:attempt_id>/', views.quiz_result, name='quiz_result'),
    
    # Papers
    path('papers/', views.papers_list, name='papers_list'),
    path('paper/download/<int:paper_id>/', views.download_paper, name='download_paper'),
    
    # Progress
    path('my-progress/', views.my_progress, name='my_progress'),
]