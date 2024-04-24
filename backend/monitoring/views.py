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
    
        metrics = []

        # Add debug tracks to n_tracks.
        metrics.append(f'n_tracks{{debug=\"true\"}} {Track.objects.filter(debug=True).count()}')
        # Add valid tracks to n_tracks.
        metrics.append(f'n_tracks{{debug=\"false\"}} {Track.objects.filter(debug=False).count()}')

        # Add debug answers.
        metrics.append(f'n_answers{{debug=\"true\"}} {Answer.objects.filter(user_id__contains="Biker-Swarm").count()}')
        # Add valid answers.
        metrics.append(f'n_answers{{debug=\"false\"}} {Answer.objects.exclude(user_id__contains="Biker-Swarm").count()}')

        # Sum up how much time users spent riding.
        tracks_with_end_time_debug = Track.objects.filter(debug=True).exclude(end_time=None)
        tracks_with_end_time = Track.objects.filter(debug=False).exclude(end_time=None)

        # Use an aggregate to sum up the duration of all debug tracks.
        sum_of_starts = tracks_with_end_time_debug.aggregate(v=Sum('start_time'))['v'] or 0
        sum_of_ends = tracks_with_end_time_debug.aggregate(v=Sum('end_time'))['v'] or 0
        metrics.append(f'n_seconds_riding{{debug=\"true\"}} {(sum_of_ends - sum_of_starts) // 1000}')

        # Use an aggregate to sum up the duration of all valid tracks.
        sum_of_starts = tracks_with_end_time.aggregate(v=Sum('start_time'))['v'] or 0
        sum_of_ends = tracks_with_end_time.aggregate(v=Sum('end_time'))['v'] or 0

        metrics.append(f'n_seconds_riding{{debug=\"false\"}} {(sum_of_ends - sum_of_starts) // 1000}')

        # Calculate the number of unique users.
        metrics.append(f'n_users{{debug=\"false\"}} {Track.objects.filter(debug=False).values("user_id").distinct().count()}')
        metrics.append(f'n_users{{debug=\"true\"}} {Track.objects.filter(debug=True).values("user_id").distinct().count()}')

        # Count the numbers each device_type occurs in the database debug.
        counts = Track.objects.filter(debug=True) \
            .values("device_type") \
            .annotate(v=Count('device_type')) \
            .values_list("device_type", "v")
        for device_type, count in counts:
            metrics.append(f'n_tracks_by_device_type{{device_type="{device_type}", debug=\"true\"}} {count}')

        # Count the numbers each device_type occurs in the database debug.
        counts = Track.objects.filter(debug=False) \
            .values("device_type") \
            .annotate(v=Count('device_type')) \
            .values_list("device_type", "v")
        for device_type, count in counts:
            metrics.append(f'n_tracks_by_device_type{{device_type="{device_type}", debug=\"false\"}} {count}')

        # Count the numbers of bike types.
        counts = Track.objects \
            .values("bike_type") \
            .annotate(v=Count('bike_type')) \
            .values_list("bike_type", "v")
        for bike_type, count in counts:
            metrics.append(f'n_tracks_by_bike_type{{bike_type="{bike_type}"}} {count}')

        # Count the number of preference types.
        counts = Track.objects \
            .values("preference_type") \
            .annotate(v=Count('preference_type')) \
            .values_list("preference_type", "v")
        for preference_type, count in counts:
            metrics.append(f'n_tracks_by_preference_type{{preference_type="{preference_type}"}} {count}')

        # Count the number of activity types.
        counts = Track.objects \
            .values("activity_type") \
            .annotate(v=Count('activity_type')) \
            .values_list("activity_type", "v")
        for activity_type, count in counts:
            metrics.append(f'n_tracks_by_activity_type{{activity_type="{activity_type}"}} {count}')

        # Count the distribution of in-app ratings.
        # Only get the most recent rating for each user (user_id field)
        # and only count the ratings for the "Dein Feedback zur App" question.
        most_recent_ratings = Answer.objects \
            .filter(question_text="Dein Feedback zur App") \
            .order_by("user_id", "-date") \
            .distinct("user_id")

        # Count in Python
        counts = {}
        for rating in most_recent_ratings:
            counts[rating.value] = counts.get(rating.value, 0) + 1
        # Add the counts to the metrics.
        for rating, count in counts.items():
            metrics.append(f'n_ratings{{rating="{rating}"}} {count}')
            
        # Battery stats
        max_energy_consumption_per_minute = 5 # in percent
        min_energy_consumption_per_minute = 0 # in percent
        number_of_buckets = 50

        # Migrate tracks that can be used for battery analysis.
        for track in Track.objects.filter(has_battery_data=None):
            if "batteryStates" not in track.metadata or len(track.metadata["batteryStates"]) < 2:
                track.has_battery_data = False
            else:
                track.has_battery_data = True
            track.save()
        
        # Migrate tracks that can be used for battery analysis and add average battery consumption if not set yet.
        for track in Track.objects.filter(has_battery_data=True, avg_battery_consumption=None):
            total_battery_consumption = track.metadata["batteryStates"][0]["level"] - track.metadata["batteryStates"][-1]["level"]
            total_milliseconds = track.metadata["batteryStates"][-1]["timestamp"] - track.metadata["batteryStates"][0]["timestamp"] 
            total_minutes = total_milliseconds / 1000 / 60
            track.avg_battery_consumption = total_battery_consumption / total_minutes
            track.save()

        le_histogram_android_is_dark_save_battery = BatteryConsumptionHistogram(number_of_buckets, True, True, True)
        le_histogram_android_is_dark_no_save_battery = BatteryConsumptionHistogram(number_of_buckets, True, True, False)
        le_histogram_android_no_dark_save_battery = BatteryConsumptionHistogram(number_of_buckets, True, False, True)
        le_histogram_android_no_dark_no_save_battery = BatteryConsumptionHistogram(number_of_buckets, True, False, False)
        le_histogram_ios_is_dark_save_battery = BatteryConsumptionHistogram(number_of_buckets, False, True, True)
        le_histogram_ios_is_dark_no_save_battery = BatteryConsumptionHistogram(number_of_buckets, False, True, False)
        le_histogram_ios_no_dark_save_battery = BatteryConsumptionHistogram(number_of_buckets, False, False, True)
        le_histogram_ios_no_dark_no_save_battery = BatteryConsumptionHistogram(number_of_buckets, False, False, False)

        # get all values for tracks with can battery analysis and debug.
        for track in Track.objects.filter(has_battery_data=True, debug=False).values("device_type", "metadata", "avg_battery_consumption"):
            if "isDarkMode" not in track["metadata"]:
                continue
            if "saveBatteryModeEnabled" not in track["metadata"]:
                continue
            
            is_android = "Android" in track["device_type"]
            is_dark_mode = track["metadata"]["isDarkMode"]
            save_battery_mode_enabled = track["metadata"]["saveBatteryModeEnabled"]
            
            bucket_idx = int((track["avg_battery_consumption"] - min_energy_consumption_per_minute) / (max_energy_consumption_per_minute - min_energy_consumption_per_minute) * number_of_buckets)
            if bucket_idx > number_of_buckets - 1:
                bucket_idx = number_of_buckets - 1
                
            if is_android and is_dark_mode and save_battery_mode_enabled:
                le_histogram_android_is_dark_save_battery.add_value(bucket_idx)
            elif is_android and is_dark_mode and not save_battery_mode_enabled:
                le_histogram_android_is_dark_no_save_battery.add_value(bucket_idx)
            elif is_android and not is_dark_mode and save_battery_mode_enabled:
                le_histogram_android_no_dark_save_battery.add_value(bucket_idx)
            elif is_android and not is_dark_mode and not save_battery_mode_enabled:
                le_histogram_android_no_dark_no_save_battery.add_value(bucket_idx)
            elif not is_android and is_dark_mode and save_battery_mode_enabled:
                le_histogram_ios_is_dark_save_battery.add_value(bucket_idx)
            elif not is_android and is_dark_mode and not save_battery_mode_enabled:
                le_histogram_ios_is_dark_no_save_battery.add_value(bucket_idx)
            elif not is_android and not is_dark_mode and save_battery_mode_enabled:
                le_histogram_ios_no_dark_save_battery.add_value(bucket_idx)
            elif not is_android and not is_dark_mode and not save_battery_mode_enabled:
                le_histogram_ios_no_dark_no_save_battery.add_value(bucket_idx)
                
        metrics.extend(le_histogram_android_is_dark_save_battery.get_metric_lines())
        metrics.extend(le_histogram_android_is_dark_no_save_battery.get_metric_lines())
        metrics.extend(le_histogram_android_no_dark_save_battery.get_metric_lines())
        metrics.extend(le_histogram_android_no_dark_no_save_battery.get_metric_lines())
        metrics.extend(le_histogram_ios_is_dark_save_battery.get_metric_lines())
        metrics.extend(le_histogram_ios_is_dark_no_save_battery.get_metric_lines())
        metrics.extend(le_histogram_ios_no_dark_save_battery.get_metric_lines())
        metrics.extend(le_histogram_ios_no_dark_no_save_battery.get_metric_lines())

        content = '\n'.join(metrics) + '\n'
        return HttpResponse(content, content_type='text/plain')
        