from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import *

admin.site.register(User)
admin.site.register(Subject)
admin.site.register(YouTubeVideo)
admin.site.register(Note)
admin.site.register(Quiz)
admin.site.register(PreviousYearPaper)  
admin.site.register(Question)
admin.site.register(QuizAttempt)