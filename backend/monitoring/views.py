from typing import List
from answers.models import Answer
from django.conf import settings
from django.db.models import Count, Sum
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from tracks.models import Track

class BatteryConsumptionHistogram:
    def __init__(self, number_of_buckets, is_android, is_dark, save_battery):
        self.number_of_buckets = number_of_buckets
        self.buckets = [0 for i in range(number_of_buckets)]
        self.is_android = is_android
        self.is_dark = is_dark
        self.save_battery = save_battery
        
    def add_value(self, bucket_idx):
        for i in range(bucket_idx, self.number_of_buckets):
            self.buckets[i] += 1
        
    def get_metric_lines(self) -> List[str]:
        lines = []
        for i in range(self.number_of_buckets):
            if i == self.number_of_buckets - 1:
                lines.append(f'battery_consumption_bucket{{os="{"Android" if self.is_android else "iOS"}", is_dark="{self.is_dark}", save_battery="{self.save_battery}", le="+Inf"}} {self.buckets[i]}')
            else:
                lines.append(f'battery_consumption_bucket{{os="{"Android" if self.is_android else "iOS"}", is_dark="{self.is_dark}", save_battery="{self.save_battery}", le="%.2f"}} {self.buckets[i]}'  % ((i * 0.1) + 0.1) )

        lines.append(f'battery_consumption_sum{{os="{"Android" if self.is_android else "iOS"}", is_dark="{self.is_dark}", save_battery="{self.save_battery}"}} {self.get_total()}')
        lines.append(f'battery_consumption_count{{os="{"Android" if self.is_android else "iOS"}", is_dark="{self.is_dark}", save_battery="{self.save_battery}"}} {self.get_count()}')

        return lines
    
    def get_total(self) -> float:
        total = 0
        last_value = 0
        for (i, value) in enumerate(self.buckets):
            if value != last_value:
                total += (value - last_value) * ((i * 0.1) + 0.1)
                last_value = value
        return round(total, 2)
    
    def get_count(self) -> int:
        return self.buckets[-1]
        


@method_decorator(csrf_exempt, name='dispatch')
class GetMetricsResource(View):
    def get(self, request):
        """
        Generate Prometheus metrics as a text file and return it.
        """
        # Only allow access with a valid api key.
        api_key = request.GET.get("api_key", None)
        if not api_key or api_key != settings.API_KEY:
            return HttpResponseBadRequest()
        
        # Get metrics.txt from data folder.
        with open('./backend/data/metrics.txt', 'r') as file:
            metrics = file.readlines()

        if metrics:
            content = '\n'.join(metrics) + '\n'
            return HttpResponse(content, content_type='text/plain')
        else:
            return HttpResponseBadRequest()
