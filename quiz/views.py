from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *

class QuizListView(APIView):
     def get(self, request):
          set = Quiz.objects.all().prefetch_related('options').order_by('order')
          serializer = QuizSerializer(set, many=True)
          return Response(serializer.data, status=status.HTTP_200_OK)