import json
import logging
from urllib.parse import urlencode, urlunparse

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views import generic
from django.views.decorators.csrf import csrf_exempt

from titles.strava import update_activity
from .models import Title, Token


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

        if hub_mode == "subscribe" and hub_verify_token == settings.VERIFY_TOKEN:
            logging.info("WEBHOOK_VERIFIED")
            return JsonResponse({"hub.challenge": hub_challenge})
        else:
            return JsonResponse(status=403, data={"error": "Verification failed"})

    elif request.method == "POST":
        event_data = json.loads(request.body)
        event_type = event_data.get("aspect_type")
        object_type = event_data.get("object_type")
        activity_id = event_data["object_id"]

        logging.info(f"Received event: {event_type}")
        messages.info(request, f"Received event: {event_type}")

        # Handle the event based on its type
        if object_type == "activity" and event_type == "create":
            update_activity(id=activity_id)
        return JsonResponse(status=200, data={"status": "Event received"})

    return JsonResponse(status=405, data={"error": "Method not allowed"})


def strava_login(request):
    """Connect with Strava button"""
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
    """Get the authorization code from the request"""
    code = request.GET.get("code")

    response = requests.post(
        url="https://www.strava.com/oauth/token",
        data={
            "client_id": settings.STRAVA_CLIENT_ID,
            "client_secret": settings.STRAVA_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
        },
    )

    if response.status_code == 200:
        token_data = response.json()
        user_data = token_data["athlete"]
        athlete_id = user_data["id"]
        access_token = token_data["access_token"]
        refresh_token = token_data["refresh_token"]
        expires_at = timezone.datetime.fromtimestamp(token_data["expires_at"])

        # Save or update the ShortLivedAccessToken
        Token.objects.update_or_create(
            athlete_id=athlete_id,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
        )

        user, created = User.objects.get_or_create(username=athlete_id)

        if created:
            # Set other details like email, first name, etc.
            user.first_name = user_data["firstname"]
            user.last_name = user_data["lastname"]
            user.save()

        # Log in the user
        login(request, user)
        logging.info("SUCCESS!")
        return redirect("titles:index")
    else:
        logging.info("NO success. womp womp")
        # Handle error in OAuth process
        return redirect("titles:index")


def update_activity_view(request, id):
    logging.info("In the view")
    update_activity(id)
    return redirect("titles:index")


def about(request):
    return render(request, "titles/about.html")
