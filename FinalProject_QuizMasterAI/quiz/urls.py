from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.user_profile, name='profile'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('topics/', views.topic_list, name='topic_list'),
    path('quiz/start/<int:topic_id>/', views.start_quiz, name='start_quiz'),
    path('quiz/<int:quiz_id>/', views.quiz_question, name='quiz_question'),
    path('quiz/<int:quiz_id>/feedback/<int:question_id>/', views.quiz_feedback, name='quiz_feedback'),
    path('quiz/<int:quiz_id>/results/', views.quiz_results, name='quiz_results'),
]