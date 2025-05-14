from django.contrib import admin
from .models import User, Topic, Question, Answer, Vote, Notification

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('django_user', 'calculate_score')
    filter_horizontal = ('following', 'topics_of_interest')

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name', 'description')

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'timestamp', 'visible')
    list_filter = ('timestamp', 'topics')
    search_fields = ('title', 'description')
    filter_horizontal = ('topics',)

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'user', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('description',)

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_positive_vote', 'content_object', 'timestamp')
    list_filter = ('is_positive_vote', 'timestamp')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('receiver', 'text', 'read', 'created_at')
    list_filter = ('read', 'created_at')
    search_fields = ('text', 'receiver__username')