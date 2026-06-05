from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    path('choose-role/', views.choose_role, name='choose_role'),
    path('teacher-dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    path('create-quiz/', views.create_quiz, name='create_quiz'),
    path('add-question/<str:quiz_code>/', views.add_question, name='add_question'),
    path('view-quizzes/', views.view_quizzes, name='view_quizzes'),
    path('quiz-results/<str:quiz_code>/', views.quiz_results, name='quiz_results'),
    path("quiz-results/<quiz_code>/", views.quiz_results, name="quiz_results"),
    path("enter-code/", views.enter_quiz_code, name="enter_quiz_code"),
    path("attempt-quiz/<quiz_code>/", views.attempt_quiz, name="attempt_quiz"),
    path("attempted-quizzes/", views.view_attempted_quizzes, name="view_attempted_quizzes"),
    path("quiz-results-pdf/<quiz_code>/", views.download_quiz_results_pdf, name="quiz_results_pdf"),







]
