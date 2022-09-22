import json

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
        try:
            json_data = json.loads(request.body)
        except json.JSONDecodeError:
            return HttpResponseBadRequest(json.dumps({"error": "Invalid request."}))

        # Unwrap some data from the json that is useful for querying.

        start_time = json_data.get("startTime", None)
        if not start_time:
            return HttpResponseBadRequest(json.dumps({"error": "Missing startTime."}))

        end_time = json_data.get("endTime", None)
        if not end_time:
            return HttpResponseBadRequest(json.dumps({"error": "Missing endTime."}))

        debug = json_data.get("debug", None)
        if debug is None:
            return HttpResponseBadRequest(json.dumps({"error": "Missing debug."}))

        settings = json_data.get("settings", None)
        if not settings:
            return HttpResponseBadRequest(json.dumps({"error": "Missing settings."}))

        backend = settings.get("backend", None)
        if not backend:
            return HttpResponseBadRequest(json.dumps({"error": "Missing backend."}))

        positioning_mode = settings.get("positioningMode", None)
        if not positioning_mode:
            return HttpResponseBadRequest(json.dumps({"error": "Missing positioningMode."}))

        device_info = json_data.get("deviceInfo", None)
        if not device_info:
            return HttpResponseBadRequest(json.dumps({"error": "Missing deviceInfo."}))

        device_type = device_info.get("name", None)
        if not device_type:
            return HttpResponseBadRequest(json.dumps({"error": "Missing deviceInfo.name."}))

        device_id = device_info.get("androidId", None) # Android
        if not device_id:
            device_id = device_info.get("identifierForVendor", None) # iOS
        if not device_id:
            return HttpResponseBadRequest(json.dumps({"error": "Missing deviceInfo.androidId or deviceInfo.identifierForVendor."}))
        
        # Make some sanity checks on the requested data.
        try:
            Track.objects.create(
                raw=json_data,
                start_time=start_time,
                end_time=end_time,
                debug=debug,
                backend=backend,
                positioning_mode=positioning_mode,
                device_id=device_id,
                device_type=device_type,
            )
        except (ValidationError, KeyError):
            return HttpResponseBadRequest(json.dumps({"error": "Invalid request."}))
        
        return JsonResponse({"success": True})


@method_decorator(csrf_exempt, name='dispatch')
class ListTracksResource(View):
    def post(self, request):
        # Get the API key from the request body.
        try:
            json_data = json.loads(request.body)
        except json.JSONDecodeError:
            return HttpResponseBadRequest(json.dumps({"error": "Invalid request."}))
        api_key = json_data.get("key", None)
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
                } 
                for track in tracks
            ], 
            "page": page,
            "pageSize": page_size,
            "totalPages": tracks.paginator.num_pages,
        })


@method_decorator(csrf_exempt, name='dispatch')
class FetchTrackResource(View):
    def post(self, request):
        # Get the API key from the request body.
        try:
            json_data = json.loads(request.body)
        except json.JSONDecodeError:
            return HttpResponseBadRequest(json.dumps({"error": "Invalid request."}))
        api_key = json_data.get("key", None)
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
            "data": track.raw,
            "pk": track.pk,
        })
