from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('questions/<int:question_id>/', views.question_detail, name='question_detail'),
    path('question/<int:question_id>/', views.question_detail, name='question_detail'),
    path('vote/<int:content_type_id>/<int:object_id>/<int:is_positive>/', views.vote, name='vote'),
    path('question/new/', views.create_question, name='create_question'),
    path('search/', views.search_questions, name='search_questions'),
    path('notifications/', views.notifications_list, name='notifications_list'),
    path('notifications/mark-read/<int:notification_id>/', views.mark_notification_as_read, name='mark_notification_as_read'),
    path('notifications/mark-all-read/', views.mark_all_as_read, name='mark_all_as_read'),
]
