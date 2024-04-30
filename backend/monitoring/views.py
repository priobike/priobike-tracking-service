import json
from time import time 

from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

@method_decorator(csrf_exempt, name='dispatch')
class GetMetricsResource(View):
    def get(self, request):
        """
        Return generated Prometheus metrics.
        """
        # Only allow access with a valid api key.
        api_key = request.GET.get("api_key", None)
        if not api_key or api_key != settings.API_KEY:
            print("API key is missing or invalid.")
            return HttpResponseBadRequest()
        
        # Get metrics.txt from data folder.
        # try open file metrics.txt
        with open(str(settings.BASE_DIR) + '/data/metrics.txt', 'r') as file:
            metrics = file.readlines()

        # Return metrics as text file.
        return HttpResponse(metrics, content_type='text/plain')
       
@method_decorator(csrf_exempt, name='dispatch')
class ReportBackupMetricsResource(View):
    def post(self, request):
        """
        Receives backup metrics.
        """
        # Only allow access with a valid api key.
        api_key = request.GET.get("api_key", None)
        if not api_key or api_key != settings.API_KEY:
            print("API key is missing or invalid.")
            return HttpResponseBadRequest()
        
        # Get metrics from request body.
        body = request.body
        body_json = json.loads(body)
        backup_track_count = body_json.get("backup_track_count", None)
        
        if not backup_track_count:
            print("Backup track count is missing.")
            return HttpResponseBadRequest()
        
        METRICS_FILE_PATH = str(settings.BASE_DIR) + '/data/backup_metrics.json'
        
        now = int(time())
        
        with open(METRICS_FILE_PATH, 'w') as file:
            json.dump({
                "backup_track_count": backup_track_count,
                "timestamp": now
            }, file)
            
        return HttpResponse()
        
        
        
