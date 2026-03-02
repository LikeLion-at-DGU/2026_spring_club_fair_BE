"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from main.views import booths_list, booth_detail, timetable_list, health_check
from quiz.views import *

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/booths", booths_list),
    path("api/booths/<int:booth_id>", booth_detail),
    path("api/timetable", timetable_list),

    path("api/quiz", QuizListView.as_view(), name="quiz-list"),
    path('api/quiz/submit', QuizSubmitView.as_view(), name='quiz-submit'),

    path("api/health", health_check),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)