import io
import json

from answers.models import Answer
from django.conf import settings
from django.core.management import call_command
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from tracks.models import Track


@method_decorator(csrf_exempt, name='dispatch')
class SyncResource(View):
    def get(self, request):
        sync_key = request.GET.get("key")
        if sync_key != settings.SYNC_KEY:
            print(f"Invalid key: {sync_key}")
            return HttpResponseBadRequest(json.dumps({"error": "Invalid key."}))
        
        pipe = io.StringIO()
        call_command("dumpdata", "--format", "xml", "tracks", "answers", stdout=pipe)
        contents = pipe.getvalue()
        pipe.close()

        return HttpResponse(contents, content_type="application/xml")

    def delete(self, request):        
        # Check that the sync key is correct.
        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            print("Invalid JSON.")
            return HttpResponseBadRequest(json.dumps({"error": "Invalid JSON."}))

        if not settings.WORKER_MODE:
            print("Delete is disabled in non-worker mode.")
            return HttpResponseBadRequest(json.dumps({"error": "Delete is disabled in non-worker mode."}))

        sync_key = body.get("key")
        if sync_key != settings.SYNC_KEY:
            print(f"Invalid key: {sync_key}")
            return HttpResponseBadRequest(json.dumps({"error": "Invalid key."}))

        try:
            qs = Track.objects.all()
            qs_n = qs.count()
            if qs_n > 0:
                print(f"Deleting {qs_n} tracks as requested by manager.")
                qs.delete()
            qs = Answer.objects.all()
            qs_n = qs.count()
            if qs_n > 0:
                print(f"Deleting {qs_n} answers as requested by manager.")
                qs.delete()
        except Exception as err:
            print(f"Error during sync: {err}")
            return HttpResponseBadRequest(json.dumps({"error": "Error during sync."}))   
        return JsonResponse({"status": "ok"})