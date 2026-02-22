from django.shortcuts import render
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from collections import Counter
from django.http import QueryDict

from main.models import *
from .models import *
from main.views import booths_list
from .serializers import *
from main.serializers import *

class QuizListView(APIView):
     def get(self, request):
          set = Quiz.objects.all().prefetch_related('options').order_by('order')
          serializer = QuizSerializer(set, many=True)
          return Response(serializer.data, status=status.HTTP_200_OK)


class QuizSubmitView(APIView) :
     def post(self, request) :
          division_ids = request.data.get('division_ids', [])

          # 6개 분과 id 필요
          if not division_ids or len(division_ids) < 6:
               return Response(
                    {"error": "6개의 답변 데이터가 모두 필요합니다."}, 
                    status=status.HTTP_400_BAD_REQUEST
               )
          
          # 1. 가장 많이 선택된 분과 ID
          counts = Counter(division_ids)
          most_common_id = counts.most_common(1)[0][0]

          try:
               # 2. 결과 분과 조회
               target_division = Division.objects.get(id=most_common_id)
               today_str = timezone.localtime(timezone.now()).strftime('%Y-%m-%d')

               # 3. 해당 분과에 속하는 부스 리스트
               inner_request = request._request
               
               qd = QueryDict(mutable=True)
               qd.update({
                    'division_id': str(target_division.id),
                    'day': today_str
               })
               inner_request.GET = qd
               booths_response = booths_list(inner_request)

               # 3. 결과 반환
               return Response({
                    "recommended_division": {
                         "id": target_division.id,
                         "name": target_division.name,
                    },
                    "booths": booths_response.data.get('results', [])
               }, status=status.HTTP_200_OK)

          except Division.DoesNotExist:
               return Response({"error": "존재하지 않는 분과 ID입니다."}, status=status.HTTP_404_NOT_FOUND)