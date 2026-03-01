from django.db import models
from django.utils import timezone
from .utils import generate_public_id, generate_admin_id


class Quiz(models.Model):
    name = models.CharField(default="Name of the quiz", max_length=300)
    timelimit_active = models.BooleanField(default=False)
    default_timelimit = models.IntegerField(default=20)
    public_id = models.CharField(unique=True, null=False, max_length=6, default=generate_public_id)
    admin_id = models.CharField(unique=True, null=False, max_length=16, default=generate_admin_id)
    guided_current_question = models.IntegerField(default=None, null=True, blank=True)
    created_at = models.DateField(default=timezone.now)
    
class Question(models.Model):
    quiz = models.ForeignKey(Quiz, related_name="questions", on_delete=models.CASCADE)
    text = models.CharField(default="Your Question", unique=False, max_length=300)
    position = models.IntegerField()
    timelimit = models.IntegerField(default=None, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if self.position is None:
            self.position = self.quiz.questions.count() + 1
        
        if self.timelimit is None:
            self.timelimit = self.quiz.default_timelimit
        super().save(*args, **kwargs)
    
    class Meta:
        unique_together = [('quiz', 'position')]
        ordering = ['position']

class Answer(models.Model):
    question = models.ForeignKey(Question, related_name="answers", on_delete=models.CASCADE)
    text = models.CharField(default="", unique=False, max_length=300)
    position = models.IntegerField(default=1)
    correct = models.BooleanField(default=False)

class QuizAttempt(models.Model):
    quiz = models.ForeignKey(Quiz, related_name="attempts", on_delete=models.CASCADE)
    participant_id = models.CharField(max_length=100)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    correct_count = models.IntegerField(default=0)
    quizzer_name = models.CharField(max_length=300, default="anonymous")
    
    class Meta:
        ordering = ['-started_at']

class UserAnswer(models.Model):
    attempt = models.ForeignKey(QuizAttempt, related_name="answers", on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer = models.ForeignKey(Answer, null=True, blank=True, on_delete=models.SET_NULL)
    answered_at = models.DateTimeField(auto_now_add=True)
