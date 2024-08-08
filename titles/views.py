import logging

from django.http import JsonResponse
import hashlib
import hmac
import json

from django.http import JsonResponse
from django.views import generic
from django.views.decorators.csrf import csrf_exempt

from .models import Question, Title

STRAVA_CLIENT_SECRET = "your_strava_client_secret"

# Your verify token. Should be a random string.
VERIFY_TOKEN = "STRAVA"


class IndexView(generic.ListView):
    template_name = "titles/index.html"
    context_object_name = "latest_strava_title_list"

    def get_queryset(self):
        """Return the last five published questions."""
        return Title.objects.order_by("-created_at")[:5]


class DetailView(generic.DetailView):
    model = Title
    template_name = "titles/detail.html"


class ResultsView(generic.DetailView):
    model = Question
    template_name = "titles/results.html"


@csrf_exempt
def strava_webhook(request):
    if request.method == "GET":
        # Verification step
        hub_mode = request.GET.get("hub.mode")
        hub_challenge = request.GET.get("hub.challenge")
        hub_verify_token = request.GET.get("hub.verify_token")

        if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
            logging.info("WEBHOOK_VERIFIED")
            return JsonResponse({"hub.challenge": hub_challenge})
        else:
            return JsonResponse(status=403, data={"error": "Verification failed"})

    elif request.method == "POST":
        # Verify the signature
        signature = request.META.get("HTTP_X_STRAVA_SIGNATURE")
        body = request.body
        expected_signature = hmac.new(
            key=STRAVA_CLIENT_SECRET.encode(), msg=body, digestmod=hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(signature, expected_signature):
            return JsonResponse(status=400, data={"error": "Invalid signature"})

        # Process the event
        event_data = json.loads(body)
        event_type = event_data.get("aspect_type")
        object_type = event_data.get("object_type")

        # Handle the event based on its type
        if object_type == "activity":
            if event_type == "create":
                # Handle new activity
                pass
            elif event_type == "update":
                # Handle activity update
                pass
            elif event_type == "delete":
                # Handle activity deletion
                pass

        return JsonResponse(status=200, data={"status": "Event received"})

    else:
        return JsonResponse(status=405, data={"error": "Method not allowed"})
