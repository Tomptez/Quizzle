from rest_framework import serializers
from .models import Quiz, Question, Answer

  
class AnswerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Answer
        fields = "__all__"
        
class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = "__all__"

class AdminQuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = "__all__"

class ParticipantAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'text', 'position']

class ParticipantQuestionSerializer(serializers.ModelSerializer):
    answers = ParticipantAnswerSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = ['id', 'text', 'position', 'timelimit', 'answers']

class ParticipantQuizSerializer(serializers.ModelSerializer):
    questions = ParticipantQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ['id', 'name', 'timelimit_active', 'default_timelimit', 'public_id', 'questions']
  