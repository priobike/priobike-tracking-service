from django.urls import path

from tracks import views

app_name = 'tracks'

urlpatterns = [
    path("post/", views.PostTrackResource.as_view(), name="send-track"),
    path("list/", views.ListTracksResource.as_view(), name="list-tracks"),
    path("get/", views.GetTrackResource.as_view(), name="get-track"),
]
