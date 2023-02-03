import json
import zlib

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.http import HttpResponseBadRequest, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from tracks.models import Track


@method_decorator(csrf_exempt, name='dispatch')
class PostTrackResource(View):
    def post(self, request):
        # This view only accepts multipart files.
        if not request.content_type.startswith("multipart/form-data"):
            return HttpResponseBadRequest(json.dumps({"error": "Invalid request."}))

        # Extract the multipart files.
        try:
            print(request.FILES)
            metadata_file = request.FILES.get("metadata.json.gz", None)
            metadata = json.loads(zlib.decompress(metadata_file.read(), 16+zlib.MAX_WBITS).decode("utf-8"))
            gps_csv = request.FILES.get("gps.csv.gz", None)
            gps_str = zlib.decompress(gps_csv.read(), 16+zlib.MAX_WBITS).decode("utf-8")
            accelerometer_csv = request.FILES.get("accelerometer.csv.gz", None)
            accelerometer_str = zlib.decompress(accelerometer_csv.read(), 16+zlib.MAX_WBITS).decode("utf-8")
            gyroscope_csv = request.FILES.get("gyroscope.csv.gz", None)
            gyroscope_str = zlib.decompress(gyroscope_csv.read(), 16+zlib.MAX_WBITS).decode("utf-8")
            magnetometer_csv = request.FILES.get("magnetometer.csv.gz", None)
            magnetometer_str = zlib.decompress(magnetometer_csv.read(), 16+zlib.MAX_WBITS).decode("utf-8")
        except Exception as e:
            print(e)
            return HttpResponseBadRequest(json.dumps({"error": "Invalid request."}))

        try:
            Track.objects.create(
                # Fields that are extracted from the raw json data for querying.
                start_time=metadata.get("startTime", None),
                end_time=metadata.get("endTime", None),
                debug=metadata.get("debug", False),
                backend=metadata.get("backend", "unknown"),
                positioning_mode=metadata.get("positioningMode", "unknown"),
                user_id=metadata.get("userId", "anonymous"),
                session_id=metadata.get("sessionId", "unknown"),
                device_type=metadata.get("deviceType", "unknown"),
                # Fields that contain raw data.
                metadata=metadata,
                gps_csv=gps_str,
                accelerometer_csv=accelerometer_str,
                gyroscope_csv=gyroscope_str,
                magnetometer_csv=magnetometer_str,
            )
        except (ValidationError, KeyError):
            return HttpResponseBadRequest(json.dumps({"error": "Invalid request."}))
        
        return JsonResponse({"success": True})


@method_decorator(csrf_exempt, name='dispatch')
class ListTracksResource(View):
    def get(self, request):
        # Get the API key from the request body.
        api_key = request.GET.get("key", None)
        if not api_key:
            return HttpResponseBadRequest(json.dumps({"error": "Missing key."}))
        if api_key != settings.API_KEY:
            return HttpResponseBadRequest(json.dumps({"error": "Invalid key."}))

        tracks = Track.objects.all()
        
        # Filter the tracks by the requested parameters.
        if "from" in request.GET: # Start time. (int)
            tracks = tracks.filter(start_time__gte=int(request.GET["from"]))
        if "to" in request.GET: # End time. (int)
            tracks = tracks.filter(end_time__lte=int(request.GET["to"]))
        if "debug" in request.GET: # Debug mode. (bool)
            if request.GET["debug"] == "true":
                tracks = tracks.filter(debug=True)
            elif request.GET["debug"] == "false":
                tracks = tracks.filter(debug=False)
        if "backend" in request.GET: # Backend. (str)
            tracks = tracks.filter(backend=request.GET["backend"])
        if "positioning" in request.GET: # Positioning mode. (str)
            tracks = tracks.filter(positioning_mode=request.GET["positioning"])
        if "deviceType" in request.GET: # Device type. (str)
            tracks = tracks.filter(device_type=request.GET["deviceType"])
        if "userId" in request.GET: # User ID. (str)
            tracks = tracks.filter(user_id=request.GET["userId"])
        if "sessionId" in request.GET: # Session ID. (str)
            tracks = tracks.filter(session_id=request.GET["sessionId"])
        
        # Paginate the tracks.
        page = int(request.GET.get("page", 1))
        if page < 1:
            page = 1

        page_size = int(request.GET.get("pageSize", 10))
        if page_size > 100:
            page_size = 100

        paginator = Paginator(tracks, page_size)
        tracks = paginator.get_page(page)

        # Serialize the tracks.
        return JsonResponse({
            "results": [
                {
                    "pk": track.pk,
                    "startTime": track.start_time,
                    "endTime": track.end_time,
                    "debug": track.debug,
                    "backend": track.backend,
                    "positioningMode": track.positioning_mode,
                    "deviceType": track.device_type,
                    "userId": track.user_id,
                    "sessionId": track.session_id,
                } 
                for track in tracks
            ], 
            "page": page,
            "pageSize": page_size,
            "totalPages": tracks.paginator.num_pages,
        })


@method_decorator(csrf_exempt, name='dispatch')
class FetchTrackResource(View):
    def get(self, request):
        # Get the API key from the request.
        api_key = request.GET.get("key", None)
        if not api_key:
            return HttpResponseBadRequest(json.dumps({"error": "Missing key."}))
        if api_key != settings.API_KEY:
            return HttpResponseBadRequest(json.dumps({"error": "Invalid key."}))

        if "pk" not in request.GET:
            return HttpResponseBadRequest(json.dumps({"error": "Missing pk."}))
        try:
            track = Track.objects.get(pk=request.GET["pk"])
        except Track.DoesNotExist:
            return HttpResponseBadRequest(json.dumps({"error": "Invalid pk."}))

        return JsonResponse({
            "metadata": track.metadata,
            "gpsCSV": track.gps_csv,
            "accelerometerCSV": track.accelerometer_csv,
            "gyroscopeCSV": track.gyroscope_csv,
            "magnetometerCSV": track.magnetometer_csv,
            "pk": track.pk,
        })
