from django.conf import settings
from django.urls import path

from . import views

app_name = 'monitoring'

if settings.WORKER_MODE:
    urlpatterns = []
else:
    urlpatterns = [
        path("metrics", views.GetMetricsResource.as_view(), name="get-metrics"),
        path("backup/tracks", views.ReportTrackBackupMetricsResource.as_view(), name="report-track-backup-metrics"),
        path("backup/answers", views.ReportAnswerBackupMetricsResource.as_view(), name="report-answer-backup-metrics"),
    ]
