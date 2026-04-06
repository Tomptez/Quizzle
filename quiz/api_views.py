import json
import logging

from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.db.models import F
from django.views.decorators.http import require_http_methods
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response

from .models import Quiz, Answer, Question, QuizAttempt, UserAnswer
from .serializers import AnswerSerializer, QuestionSerializer


class QuestionViewSet(mixins.CreateModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet
                      ):
    
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    
    # Don't allow PUT, only PATCH + GET not needed -> questions are only retrieved through QuizSerializer.
    http_method_names = ["post", "patch", "delete"]

    def create(self, request):
        quiz = get_object_or_404(Quiz, admin_id=request.data.get("admin_id"))
        question = Question(quiz=quiz)
        question.save()
        answer = Answer(question=question, correct=True)
        answer.save()
        return Response(
            {"status": "success", "question": QuestionSerializer(question).data},
            status=status.HTTP_201_CREATED,
        )

    def perform_destroy(self, instance):
        quiz = instance.quiz
        deleted_position = instance.position
        instance.delete()
        Question.objects.filter(quiz=quiz, position__gt=deleted_position).update(
            position=F("position") - 1
        )


class AnswerViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
    http_method_names = ["post", "patch", "delete"]


@require_http_methods(["POST"])
def save_participant_name(request):
    try:
        data = json.loads(request.body)
        attempt_id = data.get('attempt_id')
        participant_name = data.get('participant_name', 'anonymous')

        attempt = get_object_or_404(QuizAttempt, id=attempt_id)
        attempt.quizzer_name = participant_name
        attempt.save()

        return JsonResponse({"status": "success"})
    except Exception as e:
        logging.exception("Failed to save participant name")
        return JsonResponse({"status": "error", "message": str(e)}, status=400)


@require_http_methods(["POST"])
def swap_question_positions(request):
    try:
        data = json.loads(request.body)
        question_id_1 = data.get("question_id_1")
        question_id_2 = data.get("question_id_2")
        admin_id = data.get("admin_id")
        quiz = Quiz.objects.get(admin_id=admin_id)
        q1 = Question.objects.get(id=question_id_1, quiz=quiz)
        q2 = Question.objects.get(id=question_id_2, quiz=quiz)

        temp_pos = -1
        q1_position = q1.position
        q1.position = temp_pos
        q1.save()

        q2.position, q1.position = q1_position, q2.position
        q2.save()
        q1.save()

        return JsonResponse({"status": "success"})
    except Exception:
        logging.exception("Failed to swap positions")
        return JsonResponse({"status": "error"}, status=400)


@require_http_methods(["POST"])
def update_quiz_name(request):
    try:
        data = json.loads(request.body)
        admin_id = data.get("admin_id")
        quiz_name = data.get("quiz_name")
        quiz = Quiz.objects.get(admin_id=admin_id)
        quiz.name = quiz_name
        quiz.save()
        return JsonResponse({"status": "success"})
    except Exception:
        logging.exception("Failed to update quiz name")
        return JsonResponse({"status": "error"}, status=400)


@require_http_methods(["POST"])
def update_quiz_timelimit(request):
    try:
        data = json.loads(request.body)
        admin_id = data.get("admin_id")
        timelimit_active = data.get("timelimit_active")
        default_timelimit = data.get("default_timelimit")
        logging.debug(f"update_quiz_timelimit: {data}")
        quiz = Quiz.objects.get(admin_id=admin_id)
        if timelimit_active is not None:
            quiz.timelimit_active = timelimit_active
        if default_timelimit is not None:
            quiz.default_timelimit = default_timelimit
        quiz.save()
        return JsonResponse({"status": "success"})
    except Exception:
        logging.exception("Failed to update quiz time limit")
        return JsonResponse({"status": "error"}, status=400)


@require_http_methods(["POST"])
def save_answer(request):
    try:
        data = json.loads(request.body)
        attempt_id = data.get('attempt_id')
        question_id = data.get('question_id')
        answer_id = data.get('answer_id')

        attempt = QuizAttempt.objects.get(id=attempt_id)
        if attempt.completed_at is not None:
            return JsonResponse({"status": "error", "message": "Quiz already submitted"}, status=400)
        question = Question.objects.get(id=question_id, quiz=attempt.quiz)

        # Delete previous answer if already exists
        UserAnswer.objects.filter(attempt=attempt, question=question).delete()

        if answer_id:
            selected_answer = Answer.objects.get(id=answer_id, question=question)
            UserAnswer.objects.create(
                attempt=attempt,
                question=question,
                selected_answer=selected_answer
            )

        return JsonResponse({"status": "success"})
    except Exception as e:
        logging.exception("Failed to save answer")
        return JsonResponse({"status": "error", "message": str(e)}, status=400)


@require_http_methods(["POST"])
def advance_guided_question(request):
    try:
        data = json.loads(request.body)
        admin_id = data.get("admin_id")
        quiz = get_object_or_404(Quiz, admin_id=admin_id)
        total = quiz.questions.count()

        if quiz.guided_current_question is None:
            return JsonResponse({"status": "error", "message": "No active guided session"}, status=400)

        channel_layer = get_channel_layer()
        if quiz.guided_current_question < total - 1:
            quiz.guided_current_question += 1
            quiz.save()
            async_to_sync(channel_layer.group_send)(
                f"guided_{quiz.public_id}",
                {"type": "guided_event", "data": {"action": "advance", "question_index": quiz.guided_current_question}}
            )
            return JsonResponse({"status": "success", "question_index": quiz.guided_current_question})
        else:
            quiz.guided_current_question = None
            quiz.save()
            async_to_sync(channel_layer.group_send)(
                f"guided_{quiz.public_id}",
                {"type": "guided_event", "data": {"action": "end"}}
            )
            return JsonResponse({"status": "ended"})
    except Exception:
        logging.exception("Failed to advance guided question")
        return JsonResponse({"status": "error"}, status=400)
