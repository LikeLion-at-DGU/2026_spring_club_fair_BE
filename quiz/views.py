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
          
          # 0. 세팅
          weights = [1, 1, 1, 2, 2, 3]
          PRIORITY = [1, 2, 3, 4, 5, 6, 7, 8]
          NEW_DIVISION_ID = 8

          # 1. 점수 계산
          scores = {}
          for i in range(6) :
               weight = weights[i]
               div_id = division_ids[i]
               point = 2 if div_id == NEW_DIVISION_ID else 1
               plus = weight * point
               scores[div_id] = scores.get(div_id, 0) + plus

          # 2. 1차 결과
          max_score = max(scores.values())
          candidates = [div_id for div_id, score in scores.items() if score == max_score]

          # 3. 타이브레이커
          final_division_id = None

          if len(candidates) == 1:
               final_division_id = candidates[0]
          else:
               # 동점 시: Q6 -> Q1 순으로 사용자가 해당 문항에서 고른 분과가 후보군에 있는지 확인
               for picked_id in reversed(division_ids[:6]):
                    if picked_id in candidates:
                         final_division_id = picked_id
                         break
               
               # 4. 최후 안전장치: 고정 우선순위
               if final_division_id is None:
                    for p_id in PRIORITY:
                         if p_id in candidates:
                              final_division_id = p_id
                              break


          # 5. 결과 반환 + 부스 정보 리스트
          try:
               target_division = Division.objects.get(id=final_division_id)
               today_str = timezone.localtime(timezone.now()).strftime('%Y-%m-%d')

               # 내부 부스 조회 함수 호출 (기존 로직 유지)
               from .views import booths_list 
               inner_request = request._request
               qd = QueryDict(mutable=True)
               qd.update({'division_id': str(target_division.id), 'day': today_str})
               inner_request.GET = qd
               
               booths_response = booths_list(inner_request)

               return Response({
                    "recommended_division": {
                         "id": target_division.id,
                         "name": target_division.name,
                    },
                    "booths": booths_response.data.get('results', [])
               }, status=status.HTTP_200_OK)

          except Division.DoesNotExist:
               return Response({"error": "산출된 분과 ID가 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)