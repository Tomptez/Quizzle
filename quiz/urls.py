from django.urls import path, re_path
from . import views
from django.views.generic import RedirectView

"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

urlpatterns = [
    re_path(r'^(.*)favicon\.ico$', RedirectView.as_view(url='/static/favicon.ico')),
    path('', views.index, name='index'),
    path('newquiz', views.new_quiz, name='new_quiz'),
    path('quiz/<str:public_quizid>/', views.quiz, name="quiz"),
    path('take/<str:public_quizid>/submit/', views.submit_quiz, name='submit_quiz'),
    path('results/<int:attempt_id>/', views.quiz_results, name='quiz_results'),
    path('scoreboard/<str:public_id>/', views.scoreboard, name='scoreboard'),
    path('quiz/presenter/<str:admin_id>/', views.presenter_view, name='presenter_view'),
    path('quiz/admin/<str:admin_quizid>/', views.admin_quiz, name='admin_quiz'),
    path('quiz/api/add-answer', views.add_answer, name='add_answer'),
    path('quiz/api/delete-answer', views.delete_answer, name='delete_answer'),
    path('quiz/api/add-question', views.add_question, name='add_question'),
    path('quiz/api/delete-question', views.delete_question, name='delete_question'),
    path('quiz/api/change-question-order', views.swap_question_positions, name='swap_question_positions'),
    path('quiz/api/update-correct', views.update_correct_answer, name='update_correct_answer'),
    path('quiz/api/update-quiz-name', views.update_quiz_name, name='update_quiz_name'),
    path('quiz/api/update-question-text', views.update_question_text, name='update_question_text'),
    path('quiz/api/update-answer-text', views.update_answer_text, name='update_answer_text'),
    path('quiz/api/update-quiz-time-limit', views.update_quiz_timelimit, name='update_quiz_timelimit'),
    path('quiz/api/update-question-time-limit', views.update_question_timelimit, name='update_question_timelimit'),
    path('quiz/api/save-answer', views.save_answer, name='save_answer'),
    path('quiz/api/save-participant-name', views.save_participant_name, name='save_participant_name'),
    path('quiz/api/advance-guided-question', views.advance_guided_question, name='advance_guided_question'),
    ]
