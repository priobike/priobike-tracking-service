import json
from time import time 

from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

DATA_DIR = str(settings.BASE_DIR) + '/data/'

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
        with open(DATA_DIR + 'metrics.txt', 'r') as file:
            metrics = file.readlines()

        # Return metrics as text file.
        return HttpResponse(metrics, content_type='text/plain')
       
@method_decorator(csrf_exempt, name='dispatch')
class ReportTrackBackupMetricsResource(View):
    def post(self, request):
        """
        Receives track backup metrics.
        """
        # Only allow access with a valid api key.
        api_key = request.GET.get("api_key", None)
        if not api_key or api_key != settings.API_KEY:
            print("API key is missing or invalid.")
            return HttpResponseBadRequest()
        
        # Get metrics from request body.
        body = request.body
        body_json = json.loads(body)
        backup_total_track_count = body_json.get("backup_total_track_count", None)
        backup_valid_track_count = body_json.get("backup_valid_track_count", None)
        
        if not backup_total_track_count:
            print("backup_track_count is missing.")
            return HttpResponseBadRequest()
        
        if not backup_valid_track_count:
            print("backup_valid_track_count is missing.")
            return HttpResponseBadRequest()
        
        now = int(time())
        
        with open(DATA_DIR + 'track-backup-state.json', 'w') as file:
            json.dump({
                "total_count": backup_total_track_count,
                "valid_count": backup_valid_track_count,
                "timestamp": now
            }, file)
            
        return HttpResponse()
        
@method_decorator(csrf_exempt, name='dispatch')
class ReportAnswerBackupMetricsResource(View):
    def post(self, request):
        """
        Receives answer backup metrics.
        """
        # Only allow access with a valid api key.
        api_key = request.GET.get("api_key", None)
        if not api_key or api_key != settings.API_KEY:
            print("API key is missing or invalid.")
            return HttpResponseBadRequest()
        
        # Get metrics from request body.
        body = request.body
        body_json = json.loads(body)
        backup_total_answer_count = body_json.get("backup_total_answer_count", None)
        backup_valid_answer_count = body_json.get("backup_valid_answer_count", None)
        
        if not backup_total_answer_count:
            print("backup_answer_count is missing.")
            return HttpResponseBadRequest()
        
        if not backup_valid_answer_count:
            print("backup_valid_answer_count is missing.")
            return HttpResponseBadRequest()
        
        now = int(time())
        
        with open(DATA_DIR + 'answer-backup-state.json', 'w') as file:
            json.dump({
                "total_count": backup_total_answer_count,
                "valid_count": backup_valid_answer_count,
                "timestamp": now
            }, file)
            
        return HttpResponse()
        
        
