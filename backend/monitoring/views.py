from answers.models import Answer
from django.conf import settings
from django.db.models import Count, Sum
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from tracks.models import Track


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
        sum_of_starts = tracks_with_end_time_debug.aggregate(v=Sum('start_time'))['v']
        sum_of_ends = tracks_with_end_time_debug.aggregate(v=Sum('end_time'))['v']
        metrics.append(f'n_seconds_riding{{debug=\"true\"}} {(sum_of_ends - sum_of_starts) // 1000}')
        print(sum_of_starts, sum_of_ends)
        # Use an aggregate to sum up the duration of all valid tracks.
        sum_of_starts = tracks_with_end_time.aggregate(v=Sum('start_time'))['v']
        sum_of_ends = tracks_with_end_time.aggregate(v=Sum('end_time'))['v']
        print(sum_of_starts, sum_of_ends)
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
            metrics.append(f'n_tracks_by_device_type{{device_type="{device_type}, debug=\"true\""}} {count}')

        # Count the numbers each device_type occurs in the database debug.
        counts = Track.objects.filter(debug=False) \
            .values("device_type") \
            .annotate(v=Count('device_type')) \
            .values_list("device_type", "v")
        for device_type, count in counts:
            metrics.append(f'n_tracks_by_device_type{{device_type="{device_type}, debug=\"false\""}} {count}')

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

        content = '\n'.join(metrics) + '\n'
        return HttpResponse(content, content_type='text/plain')
        