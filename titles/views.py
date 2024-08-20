import json
import logging
from urllib.parse import urlencode, urlunparse

import requests
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils import timezone
from django.views import generic
from django.views.decorators.csrf import csrf_exempt

from .models import Title, ShortLivedAccessToken, RefreshToken

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


@csrf_exempt
def strava_webhook(request):
    """Called upon activity updates and creates"""
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
        print("POST HANDLING")
        event_data = json.loads(request.body)
        print(event_data)
        event_type = event_data.get("aspect_type")
        object_type = event_data.get("object_type")
        activity_id = event_data["object_id"]
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


def strava_login(request):
    redirect_uri = request.build_absolute_uri("/strava/callback")
    params = {
        "client_id": settings.STRAVA_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "scope": "activity:read_all,activity:write",
        "approval_prompt": "auto",
    }

    query_string = urlencode(params)
    url = urlunparse(
        ("https", "www.strava.com", "/oauth/authorize", "", query_string, "")
    )
    return redirect(url)


def strava_callback(request):
    # Get the authorization code from the request
    code = request.GET.get("code")

    # Exchange the authorization code for an access token
    response = requests.post(
        "https://www.strava.com/oauth/token",
        data={
            "client_id": settings.STRAVA_CLIENT_ID,
            "client_secret": settings.STRAVA_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
        },
    )

    # Check if the request was successful
    if response.status_code == 200:
        token_data = response.json()

        athlete_id = token_data["athlete"]["id"]
        access_token = token_data["access_token"]
        refresh_token = token_data["refresh_token"]
        expires_at = timezone.datetime.fromtimestamp(token_data["expires_at"])
        scope = "read" in token_data["scope"]

        # Save or update the ShortLivedAccessToken
        ShortLivedAccessToken.objects.update_or_create(
            athlete_id=athlete_id,
            defaults={
                "scope": scope,
                "access_token_code": access_token,
                "expires_at": expires_at,
            },
        )

        # Save or update the RefreshToken
        RefreshToken.objects.update_or_create(
            athlete_id=athlete_id,
            defaults={
                "refresh_token_code": refresh_token,
                "scope": scope,
            },
        )

        # Redirect to a success page or wherever you want the user to go next
        return redirect("success_view_name")
    else:
        # Handle error in OAuth process
        return redirect("error_view_name")
