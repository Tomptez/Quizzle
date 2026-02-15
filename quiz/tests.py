from django.test import TestCase, Client
from django.urls import reverse
import json
from .models import Quiz, Question, Answer, QuizAttempt, UserAnswer
from django.utils import timezone


class QuizViewTests(TestCase):
    """Tests for quiz views and API endpoints"""
    
    def setUp(self):
        """data-setup"""
        self.client = Client()
        
        self.quiz = Quiz.objects.create(
            name="Test Quiz",
            public_id="pub-123",
            admin_id="admin-123",
            timelimit_active=False,
            default_timelimit=20
        )
        
        self.question = Question.objects.create(
            quiz=self.quiz,
            text="What is 2+2?",
            position=1
        )
        
        self.answer1 = Answer.objects.create(
            question=self.question,
            text="4",
            position=1,
            correct=True
        )
        
        self.answer2 = Answer.objects.create(
            question=self.question,
            text="5",
            position=2,
            correct=False
        )
        
        self.question2 = Question.objects.create(
            quiz=self.quiz,
            text="What is 3+3?",
            position=2
        )
        self.answer3 = Answer.objects.create(
            question=self.question2,
            text="6",
            position=1,
            correct=True
        )
    
    # Page Views
    def test_index_view(self):
        """Test index page loads"""
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
    
    def test_quiz_view_with_valid_id(self):
        """Test quiz page loads with valid ID"""
        response = self.client.get(reverse('quiz', args=[self.quiz.public_id]))
        self.assertEqual(response.status_code, 200)
    
    def test_admin_quiz_view_with_valid_id(self):
        """Test admin quiz page loads with valid ID"""
        response = self.client.get(reverse('adminQuiz', args=[self.quiz.admin_id]))
        self.assertEqual(response.status_code, 200)
    
    def test_new_quiz_creates_quiz(self):
        """Test newQuiz creates a new quiz"""
        response = self.client.get(reverse('newQuiz'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Quiz.objects.count(), 2)
    
    # Adding questions and answers
    def test_add_question(self):
        """Test adding a question"""
        question_count = Question.objects.filter(quiz__admin_id=self.quiz.admin_id).count()
        
        data = {
            "admin_id": self.quiz.admin_id,
        }
        
        response = self.client.post(
            reverse('addQuestion'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Question.objects.filter(quiz__admin_id=self.quiz.admin_id).count() == question_count + 1)
    
    def test_add_answer(self):
        """Test adding an answer"""
        data = {
            "question_id": self.question.id,
            "text": "6",
            "correct": False
        }
        
        response = self.client.post(
            reverse('addAnswer'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Answer.objects.filter(text="6").exists())
    
    # Deleting stuff
    def test_delete_question(self):
        """Test deleting a question"""
        data = {
            "question_id": self.question.id,
            "admin_id": self.quiz.admin_id
        }
        
        response = self.client.post(
            reverse('deleteQuestion'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Question.objects.filter(id=self.question.id).exists())
    
    def test_delete_answer(self):
        """Test deleting an answer"""
        data = {"answer_id": self.answer2.id}
        
        response = self.client.post(
            reverse('deleteAnswer'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Answer.objects.filter(id=self.answer2.id).exists())
    
    # Updating stuff through the API
    def test_update_quiz_name(self):
        """Test updating quiz name"""
        data = {
            "admin_id": self.quiz.admin_id,
            "quiz_name": "New Name"
        }
        
        response = self.client.post(
            reverse('updateQuizName'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        self.quiz.refresh_from_db()
        self.assertEqual(self.quiz.name, "New Name")
    
    def test_update_question_text(self):
        """Test updating question text"""
        data = {
            "question_id": self.question.id,
            "question_text": "New text?"
        }
        
        response = self.client.post(
            reverse('updateQuestionText'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        self.question.refresh_from_db()
        self.assertEqual(self.question.text, "New text?")
    
    def test_update_answer_text(self):
        """Test updating answer text"""
        data = {
            "answer_id": self.answer1.id,
            "answer_text": "New answer"
        }
        
        response = self.client.post(
            reverse('updateAnswerText'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        self.answer1.refresh_from_db()
        self.assertEqual(self.answer1.text, "New answer")
    
    def test_update_correct_answer(self):
        """Test changing which answer is correct"""
        data = {"answer_id": self.answer2.id}
        
        response = self.client.post(
            reverse('updateCorrectAnswer'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        self.answer2.refresh_from_db()
        self.answer1.refresh_from_db()
        self.assertTrue(self.answer2.correct)
        self.assertFalse(self.answer1.correct)
    
    # Test for position swaps
    def test_swap_question_positions(self):
        """Test swapping question positions"""
        pos1 = self.question.position
        pos2 = self.question2.position
        
        data = {
            "question_id_1": self.question.id,
            "question_id_2": self.question2.id,
            "admin_id": self.quiz.admin_id
        }
        
        response = self.client.post(
            reverse('swapQuestionPositions'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        self.question.refresh_from_db()
        self.question2.refresh_from_db()
        self.assertEqual(self.question.position, pos2)
        self.assertEqual(self.question2.position, pos1)
    
    # Time Limits
    def test_update_quiz_time_limit_active(self):
        """Test toggling quiz time limit active state"""
        data = {
            "admin_id": self.quiz.admin_id,
            "timelimit_active": True
        }
        
        response = self.client.post(
            reverse('updateQuizTimeLimit'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        self.quiz.refresh_from_db()
        self.assertTrue(self.quiz.timelimit_active)
    
    def test_update_quiz_default_time_limit(self):
        """Test updating quiz default time limit"""
        data = {
            "admin_id": self.quiz.admin_id,
            "default_timelimit": 60
        }
        
        response = self.client.post(
            reverse('updateQuizTimeLimit'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        self.quiz.refresh_from_db()
        self.assertEqual(self.quiz.default_timelimit, 60)
    
    def test_update_question_time_limit(self):
        """Test updating question time limit"""
        data = {
            "question_id": self.question.id,
            "timelimit": 30
        }
        
        response = self.client.post(
            reverse('updateQuestionTimeLimit'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        self.question.refresh_from_db()
        self.assertEqual(self.question.timelimit, 30)

    # Quiz submission and results
    def test_submit_quiz(self):
        """Test submitting a quiz with answers"""
        attempt = QuizAttempt.objects.create(quiz=self.quiz, participant_id="test-participant")
        
        data = {
            "attempt_id": attempt.id,
            "answers": [
                {
                    "question_id": self.question.id,
                    "answer_id": self.answer2.id
                },
                {
                    "question_id": self.question2.id,
                    "answer_id": self.answer3.id
                }
            ]
        }
        
        response = self.client.post(
            reverse('submit_quiz', args=[self.quiz.public_id]),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        attempt.refresh_from_db()
        self.assertEqual(attempt.correct_count, 1)
        self.assertIsNotNone(attempt.completed_at)
    
    def test_quiz_results_view(self):
        """Test quiz results page displays correctly"""
        attempt = QuizAttempt.objects.create(
            quiz=self.quiz,
            participant_id="test-participant",
            correct_count=1
        )
        
        response = self.client.get(
            reverse('quiz_results', args=[attempt.id])
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['correct_count'], 1)
        self.assertEqual(response.context['total'], 2)
    
    def test_save_answer(self):
        """Test saving a single answer during quiz"""
        attempt = QuizAttempt.objects.create(quiz=self.quiz, participant_id="test-participant")
        
        data = {
            "attempt_id": attempt.id,
            "question_id": self.question.id,
            "answer_id": self.answer1.id
        }
        
        response = self.client.post(
            reverse('save_answer'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        user_answer = UserAnswer.objects.get(attempt=attempt, question=self.question)
        self.assertEqual(user_answer.selected_answer, self.answer1)
    
    def test_save_answer_overwrites_previous(self):
        """Test that saving a new answer overwrites the previous one"""
        attempt = QuizAttempt.objects.create(quiz=self.quiz, participant_id="test-participant")
        UserAnswer.objects.create(attempt=attempt, question=self.question, selected_answer=self.answer1)
        
        data = {
            "attempt_id": attempt.id,
            "question_id": self.question.id,
            "answer_id": self.answer2.id
        }
        
        response = self.client.post(
            reverse('save_answer'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(UserAnswer.objects.filter(attempt=attempt, question=self.question).count(), 1)
        user_answer = UserAnswer.objects.get(attempt=attempt, question=self.question)
        self.assertEqual(user_answer.selected_answer, self.answer2)
        
    # Test to only allow POST requests on API endpoints
    def test_api_endpoints_require_post(self):
        """Test that API endpoints only accept POST requests"""
        
        # Endpoints without required arguments
        endpoints_no_args = [
            'addQuestion',
            'addAnswer',
            'deleteQuestion',
            'deleteAnswer',
            'swapQuestionPositions',
            'updateCorrectAnswer',
            'updateQuizName',
            'updateQuestionText',
            'updateAnswerText',
            'updateQuizTimeLimit',
            'updateQuestionTimeLimit',
            'save_answer',
            'save_participant_name'
        ]
        
        # Endpoints that require URL arguments
        endpoints_with_args = [
            ('submit_quiz', [self.quiz.public_id]),
        ]
        
        # endpoints without arguments
        for endpoint in endpoints_no_args:
            with self.subTest(endpoint=endpoint):
                response = self.client.get(reverse(endpoint))
                self.assertEqual(
                    response.status_code, 405,
                    f"{endpoint} should return 405 for GET request"
                )
        
        # endpoints with arguments
        for endpoint, args in endpoints_with_args:
            with self.subTest(endpoint=endpoint):
                response = self.client.get(reverse(endpoint, args=args))
                self.assertEqual(
                    response.status_code, 405,
                    f"{endpoint} should return 405 for GET request"
            )
    def test_save_participant_name(self):
        """Test saving participant name"""
        attempt = QuizAttempt.objects.create(quiz=self.quiz, participant_id="test-participant")
        
        data = {
            "attempt_id": attempt.id,
            "participant_name": "John Doe"
        }
        
        response = self.client.post(
            reverse('save_participant_name'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        attempt.refresh_from_db()
        self.assertEqual(attempt.quizzer_name, "John Doe")

    def test_scoreboard_view(self):
        """Test scoreboard displays completed attempts"""
        
        # Create a completed attempt
        QuizAttempt.objects.create(
            quiz=self.quiz,
            participant_id="p1",
            quizzer_name="Alice",
            correct_count=2,
            completed_at=timezone.now()
        )
        
        response = self.client.get(
            reverse('scoreboard', args=[self.quiz.public_id])
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['attempts']), 1)
        self.assertEqual(response.context['attempts'][0].quizzer_name, "Alice")
        self.assertEqual(response.context['attempts'][0].correct_count, 2)
        self.assertEqual(response.context['total_questions'], 2)
