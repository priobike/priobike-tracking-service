from django.conf import settings
from django.urls import path

from . import views

app_name = 'answers'

if settings.WORKER_MODE:
    urlpatterns = [
        path("post/", views.PostAnswerResource.as_view(), name="send-answer"),
    ]
else:
    urlpatterns = [
        path("list/", views.ListAnswersResource.as_view(), name="list-answers"),
    ]
