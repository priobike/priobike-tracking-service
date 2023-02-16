from django.urls import path

from . import views

app_name = 'answers'

urlpatterns = [
    path("post/", views.PostAnswerResource.as_view(), name="send-answer"),
    path("list/", views.ListAnswersResource.as_view(), name="list-answers"),
]
