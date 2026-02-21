from django.shortcuts import render, redirect, get_object_or_404
import secrets
import logging
import json
from .serializers import QuizSerializer, QuestionSerializer
from django.utils import timezone
from django.http import JsonResponse
from django.db import models
from django.views.decorators.http import require_http_methods

from .models import Quiz, Answer, Question, QuizAttempt, UserAnswer

def index(request):
    return render(request, 'quiz/index.html', {})

def quiz(request, public_quizid):
    context = {}
    quiz = get_object_or_404(Quiz, public_id=public_quizid)
    
    attempt = QuizAttempt.objects.create(quiz=quiz, participant_id=secrets.token_urlsafe(12))
    
    quiz_serialized = QuizSerializer(quiz)
    context = {
        'quiz': json.dumps(quiz_serialized.data),
        'attempt_id': attempt.id,
        'public_quizid': public_quizid
    }
    
    return render(request, 'quiz/quiz.html', context)

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

def adminQuiz(request, admin_quizid):
    context = {}
    try:
        print(f"Looking for id {admin_quizid}")
        quiz = get_object_or_404(Quiz, admin_id=admin_quizid)
        quiz_serialized = QuizSerializer(quiz)
        context["quiz"] = json.dumps(quiz_serialized.data)
        context["public_id"] = quiz.public_id
        context["admin_id"] = quiz.admin_id
        logging.info(quiz)
        return render(request, 'quiz/quiz_settings.html', context)
    except Exception as e:
        logging.exception("Failed to get quiz for admin view")
        return JsonResponse({"status": "error", "message": str(e)}, status=400)

def calculate_score(attempt_id):
    try:
        attempt = get_object_or_404(QuizAttempt, id=attempt_id)
        
        user_answers = UserAnswer.objects.filter(attempt=attempt)
        correct_count = 0
        
        for user_answer in user_answers:
            if user_answer.selected_answer and user_answer.selected_answer.correct:
                correct_count += 1
        
        attempt.correct_count = correct_count
        attempt.completed_at = timezone.now()
        attempt.save()
        
    except Exception as e:
        logging.exception("Failed to calculate score")

@require_http_methods(["POST"])
def submit_quiz(request, public_quizid):
    try:
        data = json.loads(request.body)
        quiz = get_object_or_404(Quiz, public_id=public_quizid)
        attempt = get_object_or_404(QuizAttempt, id=data['attempt_id'], quiz=quiz)
        
        for answer_data in data['answers']:
            question_id = answer_data['question_id']
            answer_id = answer_data['answer_id']
            
            try:
                question = get_object_or_404(Question, id=question_id, quiz=quiz)
                selected_answer = get_object_or_404(Answer, id=answer_id, question=question)
                UserAnswer.objects.create(attempt=attempt, question=question, selected_answer=selected_answer)
            except:
                logging.exception("Couldn't submit quiz")
        
        calculate_score(attempt.id)
        
        return JsonResponse({
            'status': 'success',
            'redirect_url': f'/results/{attempt.id}/'
        })
    except Exception as e:
        logging.exception("Failed to submit quiz")
        return JsonResponse({'status': 'error', 'message': 'Error submitting quiz'}, status=400)

def quiz_results(request, attempt_id):
    attempt = get_object_or_404(QuizAttempt, id=attempt_id)
    quiz = attempt.quiz
    total_questions = quiz.questions.count()
    
    context = {
        'quiz': quiz,
        'correct_count': attempt.correct_count,
        'total': total_questions,
        'participant_id': attempt.participant_id
    }
    return render(request, 'quiz/quiz_results.html', context)

def newQuiz(request):
    quiz = Quiz()
    quiz.save()
    first_question = Question()
    first_question.quiz = quiz
    first_question.save()
    default_answer = Answer(correct=True)
    default_answer.question = first_question
    default_answer.save()
    print(f"newQuiz(): Created new quiz with admin ID {quiz.admin_id}")
    return redirect(f"quiz/admin/{quiz.admin_id}")

@require_http_methods(["POST"])
def addQuestion(request):
    print("addQuestion()")
    data = json.loads(request.body)
    quiz = Quiz.objects.get(admin_id=data.get("admin_id"))
    question = Question(quiz=quiz)
    question.save()
    answer = Answer(question=question, correct=True)
    answer.save()
    return JsonResponse({"status": "success", "question": QuestionSerializer(question).data})

@require_http_methods(["POST"])
def addAnswer(request):
    print("addAnswer")
    data = json.loads(request.body)
    question_id = data.get("question_id")
    text = data.get("text")
    correct = data.get("correct")
    print(data)
    try:
        question = Question.objects.get(id=question_id)
        if correct:
            Answer.objects.filter(question=question).update(correct=False)
        answer = Answer(question=question, text=text, correct=correct)
        answer.save()
        print("Answer saved")
        return JsonResponse({"status": "success", "answer_id": answer.id})
    except Exception as e:
        logging.exception("Failed to add answer")
        return JsonResponse({"status": "error"}, status=400)

@require_http_methods(["POST"])
def deleteQuestion(request):
    print("deleteQuestion")
    data = json.loads(request.body)
    question_id = data.get("question_id")
    admin_id = data.get("admin_id")
    
    try:
        quiz = Quiz.objects.get(admin_id=admin_id)
        question = Question.objects.get(id=question_id, quiz=quiz)
        deleted_position = question.position
        question.delete()
        Question.objects.filter(quiz=quiz, position__gt=deleted_position).update(position=models.F('position') - 1)
        return JsonResponse({"status": "success"})
    except Exception as e:
        logging.exception("Failed to delete question")
        return JsonResponse({"status": "error"}, status=400)

@require_http_methods(["POST"])
def deleteAnswer(request):
    data = json.loads(request.body)
    answer_id = data.get("answer_id")
    try:
        answer = Answer.objects.get(id=answer_id)
        answer.delete()
        return JsonResponse({"status": "success"})
    except Exception as e:
        logging.exception("Failed to delete answer")
        return JsonResponse({"status": "error"}, status=400)

@require_http_methods(["POST"])
def swapQuestionPositions(request):
    print("swapQuestionPositions")
    data = json.loads(request.body)
    question_id_1 = data.get("question_id_1")
    question_id_2 = data.get("question_id_2")
    admin_id = data.get("admin_id")
    
    try:
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
    except Exception as e:
        logging.exception("Failed to swap positions")
        return JsonResponse({"status": "error"}, status=400)
    
@require_http_methods(["POST"])
def updateCorrectAnswer(request):
    data = json.loads(request.body)
    answer_id = data.get("answer_id")
    try:
        answer = Answer.objects.get(id=answer_id)
        Answer.objects.filter(question=answer.question).update(correct=False)
        answer.correct = True
        answer.save()
        return JsonResponse({"status": "success"})
    except:
        return JsonResponse({"status": "error"}, status=400)

@require_http_methods(["POST"])
def updateQuizName(request):
    data = json.loads(request.body)
    admin_id = data.get("admin_id")
    quiz_name = data.get("quiz_name")
    try:
        quiz = Quiz.objects.get(admin_id=admin_id)
        quiz.name = quiz_name
        quiz.save()
        return JsonResponse({"status": "success"})
    except Exception as e:
        logging.exception("Failed to update quiz name")
        return JsonResponse({"status": "error"}, status=400)

@require_http_methods(["POST"])
def updateQuestionText(request):
    data = json.loads(request.body)
    question_id = data.get("question_id")
    question_text = data.get("question_text")
    try:
        question = Question.objects.get(id=question_id)
        question.text = question_text
        question.save()
        return JsonResponse({"status": "success"})
    except Exception as e:
        logging.exception("Failed to update question text")
        return JsonResponse({"status": "error"}, status=400)

@require_http_methods(["POST"])
def updateAnswerText(request):
    data = json.loads(request.body)
    answer_id = data.get("answer_id")
    answer_text = data.get("answer_text")
    try:
        answer = Answer.objects.get(id=answer_id)
        answer.text = answer_text
        answer.save()
        return JsonResponse({"status": "success"})
    except Exception as e:
        logging.exception("Failed to update answer text")
        return JsonResponse({"status": "error"}, status=400)

@require_http_methods(["POST"])
def updateQuizTimeLimit(request):
    data = json.loads(request.body)
    admin_id = data.get("admin_id")
    timelimit_active = data.get("timelimit_active")
    default_timelimit = data.get("default_timelimit")
    print("Update quiz time limit:", data)
    try:
        quiz = Quiz.objects.get(admin_id=admin_id)
        if timelimit_active is not None:
            quiz.timelimit_active = timelimit_active
        if default_timelimit is not None:
            quiz.default_timelimit = default_timelimit
        quiz.save()
        return JsonResponse({"status": "success"})
    except Exception as e:
        logging.exception("Failed to update quiz time limit")
        return JsonResponse({"status": "error"}, status=400)

@require_http_methods(["POST"])
def updateQuestionTimeLimit(request):
    data = json.loads(request.body)
    question_id = data.get("question_id")
    timelimit = data.get("timelimit")
    print("Update question time limit:", data)
    try:
        question = Question.objects.get(id=question_id)
        question.timelimit = timelimit
        question.save()
        return JsonResponse({"status": "success"})
    except Exception as e:
        logging.exception("Failed to update question time limit")
        return JsonResponse({"status": "error"}, status=400)

@require_http_methods(["POST"])
def save_answer(request):
    try:
        data = json.loads(request.body)
        attempt_id = data.get('attempt_id')
        question_id = data.get('question_id')
        answer_id = data.get('answer_id')
        
        attempt = QuizAttempt.objects.get(id=attempt_id)
        question = Question.objects.get(id=question_id)
        
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
    
def scoreboard(request, public_id):
    quiz = get_object_or_404(Quiz, public_id=public_id)
    attempts = QuizAttempt.objects.filter(
        quiz=quiz,
        completed_at__isnull=False
    ).order_by('-correct_count')
    
    context = {
        'quiz': quiz,
        'attempts': attempts,
        'admin_id': quiz.admin_id,
        'total_questions': quiz.questions.count(),
    }
    return render(request, 'quiz/scoreboard.html', context)

def presenter_view(request, admin_id):
    quiz = get_object_or_404(Quiz, admin_id=admin_id)
    quiz.save()
    quiz_serialized = QuizSerializer(quiz)
    context = {
        'quiz': json.dumps(quiz_serialized.data),
        'admin_id': admin_id,
        'public_id': quiz.public_id,
    }
    return render(request, 'quiz/quiz_presenter.html', context)
