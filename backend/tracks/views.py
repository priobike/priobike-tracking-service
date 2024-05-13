import json
import zlib
from io import StringIO

import pandas as pd
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db.utils import IntegrityError
from django.http import (HttpResponseBadRequest, HttpResponseServerError,
                         JsonResponse)
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from tracks.models import Track


def validate_track(track):
    if track.debug:
        return "Track is in debug mode."
    if track.positioning_mode != "gnss":
        return "Track is created using mock position mode."
    
    track_gps_data = pd.read_csv(StringIO(track.gps_csv), sep=",")
    
    if len(track_gps_data.index) < 6:
        return "Track is too short."
    
    if track.backend == 'staging':
        # Bounding box Dresden 
        min_lat, max_lat = 50.8, 51.3
        min_lon, max_lon = 13.2, 14.3
    elif track.backend == 'production':
        # Bounds for Hamburg
        min_lat, max_lat = 53.1, 54.0
        min_lon, max_lon = 9.1, 10.9
    elif track.backend == 'release':
        # Bounds for Hamburg
        min_lat, max_lat = 53.1, 54.0
        min_lon, max_lon = 9.1, 10.9
    else:
        return "Track is not from a valid backend."
    
    # Get the maximum and minimum latitude and longitude values of the track.
    try:
        track_max_lat = track_gps_data['latitude'].max()
        track_min_lat = track_gps_data['latitude'].min()
        track_max_lon = track_gps_data['longitude'].max()
        track_min_lon = track_gps_data['longitude'].min()
    except KeyError as e:
        print(f"Track with id {track.session_id} has no latitude or longitude column (in GPS data).")
        return
    
    # Check if the track is fully within the bounding box of the city.
    if track_max_lat > max_lat or track_min_lat < min_lat or track_max_lon > max_lon or track_min_lon < min_lon:
        return "Track is out of bounding box of the city."
    
    return None


@method_decorator(csrf_exempt, name='dispatch')
class PostTrackResource(View):
    def post(self, request):
        # This view only accepts multipart files.
        if not request.content_type.startswith("multipart/form-data"):
            return HttpResponseBadRequest(json.dumps({"error": "Invalid request."}))

        # Extract the multipart files.
        try:
            metadata_file = request.FILES.get("metadata.json.gz", None)
            metadata = json.loads(zlib.decompress(metadata_file.read(), 16+zlib.MAX_WBITS).decode("utf-8"))
            gps_csv = request.FILES.get("gps.csv.gz", None)
            gps_str = zlib.decompress(gps_csv.read(), 16+zlib.MAX_WBITS).decode("utf-8")
            accelerometer_csv = request.FILES.get("accelerometer.csv.gz", None)
            accelerometer_str = zlib.decompress(accelerometer_csv.read(), 16+zlib.MAX_WBITS).decode("utf-8") if accelerometer_csv else None
            gyroscope_csv = request.FILES.get("gyroscope.csv.gz", None)
            gyroscope_str = zlib.decompress(gyroscope_csv.read(), 16+zlib.MAX_WBITS).decode("utf-8") if gyroscope_csv else None
            magnetometer_csv = request.FILES.get("magnetometer.csv.gz", None)
            magnetometer_str = zlib.decompress(magnetometer_csv.read(), 16+zlib.MAX_WBITS).decode("utf-8") if magnetometer_csv else None
        except Exception as e:
            print(e)
            return HttpResponseBadRequest(json.dumps({"error": "Invalid request."}))

        try:
            track = Track(
                # Fields that are extracted from the raw json data for querying.
                start_time=metadata.get("startTime", None),
                end_time=metadata.get("endTime", None),
                debug=metadata.get("debug", False) if metadata.get("debug", False) != None else False,
                backend=metadata.get("backend", "unknown") if metadata.get("backend", "unknown") != None else "unknown",
                positioning_mode=metadata.get("positioningMode", "unknown") if metadata.get("positioningMode", "unknown") != None else "unknown",
                user_id=metadata.get("userId", "anonymous") if metadata.get("userId", "anonymous") != None else "anonymous",
                session_id=metadata.get("sessionId", "unknown") if metadata.get("sessionId", "unknown") != None else "unknown",
                device_type=metadata.get("deviceType", "unknown") if metadata.get("deviceType", "unknown") != None else "unknown",
                bike_type=metadata.get("bikeType", "unknown") if metadata.get("bikeType", "unknown") != None else "unknown",
                preference_type=metadata.get("preferenceType", "unknown") if metadata.get("preferenceType", "unknown") != None else "unknown",
                activity_type=metadata.get("activityType", "unknown") if metadata.get("activityType", "unknown") != None else "unknown",
                has_battery_data = metadata.get("batteryStates") != None and len(metadata.get("batteryStates")) >= 2,
                # Fields that contain raw data.
                metadata=metadata,
                gps_csv=gps_str,
                accelerometer_csv=accelerometer_str,
                gyroscope_csv=gyroscope_str,
                magnetometer_csv=magnetometer_str,
            )
            err = validate_track(track)
            if not err:
                track.save()
            else:
                # Log but don't tell the client to not leak validation information.
                print(f"Track with id {track.session_id} won't be inserted into the DB: {err}")
        except (ValidationError, KeyError) as e:
            print(e)
            return HttpResponseBadRequest(json.dumps({"error": "Invalid request."}))
        except IntegrityError as e:
            return HttpResponseBadRequest(json.dumps({"error": "Track already exists."}))
        except Exception as e:
            print(e, type(e))
            return HttpResponseServerError(json.dumps({"error": "Unknown error."}))
        
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

        # Always fetch non debug tracks.
        tracks = tracks.filter(debug=False)
        
        # Filter the tracks by the requested parameters.
        if "from" in request.GET: # Start time. (int)
            tracks = tracks.filter(start_time__gte=int(request.GET["from"]))
        if "to" in request.GET: # End time. (int)
            tracks = tracks.filter(end_time__lte=int(request.GET["to"]))
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
        if "pk" in request.GET: # Primary key. (int)
            tracks = tracks.filter(pk__gt=int(request.GET["pk"]))
        
        # Order the tracks by pk.
        tracks = tracks.order_by("pk")
        
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
