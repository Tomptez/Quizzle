from . import views, api_views
from django.views.generic import RedirectView
from django.urls import path, re_path, include
from rest_framework.routers import DefaultRouter


router = DefaultRouter(trailing_slash=False)
router.register("questions", api_views.QuestionViewSet, basename="api-questions")
router.register("answers", api_views.AnswerViewSet, basename="api-answers")

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
    path('quiz/api/update-quiz-name', api_views.update_quiz_name, name='update_quiz_name'),
    path('quiz/api/update-quiz-time-limit', api_views.update_quiz_timelimit, name='update_quiz_timelimit'),
    path('quiz/api/save-answer', api_views.save_answer, name='save_answer'),
    path('quiz/api/save-participant-name', api_views.save_participant_name, name='save_participant_name'),
    path('quiz/api/advance-guided-question', api_views.advance_guided_question, name='advance_guided_question'),
    path('quiz/api/', include(router.urls)),
    ]
