from django.urls import path
from .views import QuizListView

urlpatterns = [
     path('', QuizListView.as_view(), name='quiz-list'), # /api/quiz/
]