from rest_framework import serializers
from .models import Quiz, Question, Answer

  
class AnswerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Answer
        fields = "__all__"

    def update(self, instance, validated_data):
        if validated_data.get('correct'):
            Answer.objects.filter(question=instance.question).update(correct=False)
        return super().update(instance, validated_data)
        
class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = "__all__"
        read_only_fields = ['quiz', 'position']

class AdminQuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = "__all__"
        read_only_fields = ['admin_id', 'public_id', 'created_at', 'guided_current_question']

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
  