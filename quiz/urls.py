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
    path('newquiz', views.newQuiz, name='newQuiz'),
    path('quiz/<str:public_quizid>/', views.quiz, name="quiz"),
    path('take/<str:public_quizid>/submit/', views.submit_quiz, name='submit_quiz'),
    path('results/<int:attempt_id>/', views.quiz_results, name='quiz_results'),
    path('scoreboard/<str:public_id>/', views.scoreboard, name='scoreboard'),
    path('quiz/presenter/<str:admin_id>/', views.presenter_view, name='presenter_view'),
    path('quiz/admin/<str:admin_quizid>/', views.adminQuiz, name="adminQuiz"),
    path('quiz/api/add-answer', views.addAnswer, name="addAnswer"),
    path('quiz/api/delete-answer', views.deleteAnswer, name="deleteAnswer"),
    path('quiz/api/add-question', views.addQuestion, name="addQuestion"),
    path('quiz/api/delete-question', views.deleteQuestion, name="deleteQuestion"),
    path('quiz/api/change-question-order', views.swapQuestionPositions, name="swapQuestionPositions"),
    path('quiz/api/update-correct', views.updateCorrectAnswer, name="updateCorrectAnswer"),
    path('quiz/api/update-quiz-name', views.updateQuizName, name="updateQuizName"),
    path('quiz/api/update-question-text', views.updateQuestionText, name="updateQuestionText"),
    path('quiz/api/update-answer-text', views.updateAnswerText, name="updateAnswerText"),
    path('quiz/api/update-quiz-time-limit', views.updateQuizTimeLimit, name="updateQuizTimeLimit"),
    path('quiz/api/update-question-time-limit', views.updateQuestionTimeLimit, name="updateQuestionTimeLimit"),
    path('quiz/api/save-answer', views.save_answer, name='save_answer'),
    path('quiz/api/save-participant-name', views.save_participant_name, name='save_participant_name'),
    path('quiz/api/advance-guided-question', views.advance_guided_question, name='advance_guided_question'),
    ]
