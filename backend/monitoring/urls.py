from django.conf import settings
from django.urls import path

from . import views

app_name = 'monitoring'

if settings.WORKER_MODE:
    urlpatterns = []
else:
    urlpatterns = [
        path("metrics", views.GetMetricsResource.as_view(), name="get-metrics"),
        path("backup", views.ReportBackupMetricsResource.as_view(), name="report-backup-metrics"),
    ]
