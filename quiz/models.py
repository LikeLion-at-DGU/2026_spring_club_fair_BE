from django.db import models

class Quiz(models.Model):
     question = models.CharField(max_length=255, verbose_name="질문 내용")
     order = models.PositiveIntegerField(
          unique=True, 
          help_text="퀴즈 순서 (1~6)"
     )

     class Meta:
          verbose_name = "퀴즈 질문"
          verbose_name_plural = "퀴즈 질문들"
          ordering = ['order']

     def __str__(self):
          return f"Q{self.order}. {self.question}"


class QuizOption(models.Model):
     quiz = models.ForeignKey(
          Quiz, 
          on_delete=models.CASCADE, 
          related_name="options",
          verbose_name="해당 질문"
     )
     division = models.ForeignKey(
          'main.Division',  # main > Division 참조
          on_delete=models.CASCADE, 
          related_name="quiz_options",
          verbose_name="연결된 분과"
     )
     answer = models.CharField(max_length=255, verbose_name="선택지 텍스트")

     class Meta:
          verbose_name = "퀴즈 선택지"
          verbose_name_plural = "퀴즈 선택지들"

     def __str__(self):
          return f"[Q{self.quiz.order}] {self.answer} -> {self.division.name}"