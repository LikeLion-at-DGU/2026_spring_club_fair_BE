from rest_framework import serializers
from .models import *

class QuizOptionSerializer(serializers.ModelSerializer) :
     class Meta:
          model = QuizOption
          fields = ['id', 'answer', 'division']


class QuizSerializer(serializers.ModelSerializer):
     options = QuizOptionSerializer(many=True, read_only=True)

     class Meta:
          model = Quiz
          fields = ['id', 'question', 'order', 'options']