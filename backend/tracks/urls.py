from django.conf import settings
from django.urls import path
from tracks import views

app_name = 'tracks'

if settings.WORKER_MODE:
    urlpatterns = [
        path("post/", views.PostTrackResource.as_view(), name="send-track"),
    ]
else:
    urlpatterns = [
        path("list/", views.ListTracksResource.as_view(), name="list-tracks"),
        path("fetch/", views.FetchTrackResource.as_view(), name="fetch-track"),
    ]
