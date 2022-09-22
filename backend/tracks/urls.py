from django.urls import path

from tracks import views

app_name = 'tracks'

urlpatterns = [
    path("post/", views.PostTrackResource.as_view(), name="send-track"),
]
