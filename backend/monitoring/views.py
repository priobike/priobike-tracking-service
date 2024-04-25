from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

@method_decorator(csrf_exempt, name='dispatch')
class GetMetricsResource(View):
    def get(self, request):
        """
        Generate Prometheus metrics as a text file and return it.
        """
        print("GET /monitoring/metrics")
        # Only allow access with a valid api key.
        api_key = request.GET.get("api_key", None)
        if not api_key or api_key != settings.API_KEY:
            print("API key is missing or invalid.")
            return HttpResponseBadRequest()
        
        # Get metrics.txt from data folder.
        # try open file metrics.txt
        
        with open('./backend/data/metrics.txt', 'r') as file:
            metrics = file.readlines()

        # Return metrics as text file.
        return HttpResponse(metrics, content_type='text/plain')
       
