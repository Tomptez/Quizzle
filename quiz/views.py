from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
import secrets
import logging
import json

from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from .models import Quiz, Answer, Question, QuizAttempt, UserAnswer
from .serializers import AdminQuizSerializer, ParticipantQuizSerializer

def index(request):
    return render(request, 'quiz/index.html', {})

def quiz(request, public_quizid):
    quiz = get_object_or_404(Quiz, public_id=public_quizid)
    quiz_serialized = ParticipantQuizSerializer(quiz)
    
    session_key = f'quiz_attempt_{public_quizid}'
    attempt_id = request.session.get(session_key)
    if attempt_id:
        attempt = QuizAttempt.objects.filter(id=attempt_id, quiz=quiz, completed_at__isnull=True).first()
    else:
        attempt = None
    if not attempt:
        attempt = QuizAttempt.objects.create(quiz=quiz, participant_id=secrets.token_urlsafe(12))
        request.session[session_key] = attempt.id
    
    is_guided = quiz.guided_current_question is not None
    
    context = {
        'quiz': json.dumps(quiz_serialized.data),
        'attempt_id': attempt.id,
        'public_quizid': public_quizid,
        'is_guided': json.dumps(is_guided),
        'guided_start_question': quiz.guided_current_question if is_guided else -1,
    }
    
    return render(request, 'quiz/quiz.html', context)

def admin_quiz(request, admin_quizid):
    quiz = get_object_or_404(Quiz, admin_id=admin_quizid)
    quiz_serialized = AdminQuizSerializer(quiz)
    context = {
        "quiz": json.dumps(quiz_serialized.data),
        "public_id": quiz.public_id,
        "admin_id": quiz.admin_id,
    }
    return render(request, 'quiz/quiz_settings.html', context)

def calculate_score(attempt_id):
    try:
        attempt = QuizAttempt.objects.get(id=attempt_id)
        
        user_answers = UserAnswer.objects.filter(attempt=attempt).select_related('selected_answer')
        correct_count = 0
        
        for user_answer in user_answers:
            if user_answer.selected_answer and user_answer.selected_answer.correct:
                correct_count += 1
        
        attempt.correct_count = correct_count
        attempt.completed_at = timezone.now()
        attempt.save()
        
    except Exception:
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
                UserAnswer.objects.update_or_create(
                    attempt=attempt, question=question,
                    defaults={'selected_answer': selected_answer}
                )
            except Exception:
                logging.exception("Couldn't submit quiz")
        
        calculate_score(attempt.id)
        
        return JsonResponse({
            'status': 'success',
            'redirect_url': reverse('quiz_results', args=[attempt.id])
        })
    except Exception:
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

@require_http_methods(["POST"])
def new_quiz(request):
    quiz = Quiz()
    quiz.save()
    first_question = Question()
    first_question.quiz = quiz
    first_question.save()
    default_answer = Answer(correct=True)
    default_answer.question = first_question
    default_answer.save()
    logging.debug(f"new_quiz(): Created quiz {quiz.admin_id}")
    return redirect('admin_quiz', admin_quizid=quiz.admin_id)

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
    if quiz.guided_current_question is None:
        quiz.guided_current_question = -1
        quiz.save()
    quiz_serialized = AdminQuizSerializer(quiz)
    context = {
        'quiz': json.dumps(quiz_serialized.data),
        'admin_id': admin_id,
        'public_id': quiz.public_id,
    }
    return render(request, 'quiz/quiz_presenter.html', context)
