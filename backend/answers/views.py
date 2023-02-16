import json

from answers.models import Answer
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.http import HttpResponseBadRequest, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View


@method_decorator(csrf_exempt, name='dispatch')
class PostAnswerResource(View):
    def post(self, request):
        try:
            json_data = json.loads(request.body)
        except json.JSONDecodeError:
            return HttpResponseBadRequest(json.dumps({"error": "Invalid request."}))
        
        # Make some sanity checks on the requested data.
        try:
            Answer.objects.create(
                # Necessary args
                user_id=json_data.get("userId", "anonymous"),
                question_text=json_data["questionText"],
                # Optional args
                question_image=json_data.get("questionImage"),
                session_id=json_data.get("sessionId"),
                value=json_data.get("value"),
            )
        except (ValidationError, KeyError):
            return HttpResponseBadRequest(json.dumps({"error": "Invalid request."}))
        
        return JsonResponse({"success": True})

@method_decorator(csrf_exempt, name='dispatch')
class ListAnswersResource(View):
    def get(self, request):
        # Get the API key from the request.
        api_key = request.GET.get("key", None)
        if not api_key:
            return HttpResponseBadRequest(json.dumps({"error": "Missing key."}))
        if api_key != settings.API_KEY:
            return HttpResponseBadRequest(json.dumps({"error": "Invalid key."}))

        # Paginate the answers.
        page = int(request.GET.get("page", 1))
        if page < 1:
            page = 1

        page_size = int(request.GET.get("pageSize", 10))
        if page_size > 100:
            page_size = 100

        answers = Answer.objects.all()
        paginator = Paginator(answers, page_size)
        answers = paginator.get_page(page)

        return JsonResponse({
            "results": [
                {
                    "pk": answer.pk,
                    "userId": answer.user_id,
                    "questionText": answer.question_text,
                    "questionImage": answer.question_image,
                    "sessionId": answer.session_id,
                    "value": answer.value,
                    "date": answer.date.isoformat(),
                }
                for answer in answers
            ],
            "page": page,
            "pageSize": page_size,
            "totalPages": answers.paginator.num_pages,
        })