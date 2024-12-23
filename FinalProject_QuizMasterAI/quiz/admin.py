from django.contrib import admin
from .models import User, Topic, Quiz, Question, Answer, UserTopicProgress

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    search_fields = ('name', 'description')

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('user', 'topic', 'score', 'created_at')
    list_filter = ('topic', 'created_at')

admin.site.register(User)
admin.site.register(UserTopicProgress)
admin.site.register(Question)
admin.site.register(Answer)