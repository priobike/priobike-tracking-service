import json

from django.core.exceptions import ValidationError
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
        
        # Make some sanity checks on the requested data.
        try:
            Track.objects.create(
                raw=json_data,
                start_time=start_time,
                end_time=end_time,
                debug=debug,
                backend=backend,
                positioning_mode=positioning_mode,
            )
        except (ValidationError, KeyError):
            return HttpResponseBadRequest(json.dumps({"error": "Invalid request."}))
        
        return JsonResponse({"success": True})
