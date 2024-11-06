import json
import logging
from urllib.parse import urlencode, urlunparse

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import generic
from django.views.decorators.csrf import csrf_exempt

from titles.strava import update_activity_name, create_user
from .forms import TitleForm
from .models import Title


from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


@login_required
def index(request):
    if request.method == "POST":
        form = TitleForm(request.POST)
        if form.is_valid():
            title = form.save(commit=False)
            title.user = request.user
            title.save()
            messages.success(request, "Title saved successfully!")
            return redirect("titles:detail", pk=title.pk)
    else:
        form = TitleForm()

    title_list = Title.objects.filter(user=request.user).order_by("-created_at")

    # Set up pagination with 5 titles per page
    paginator = Paginator(title_list, 5)
    page = request.GET.get("page")

    try:
        titles = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        titles = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page of results.
        titles = paginator.page(paginator.num_pages)

    context = {
        "form": form,
        "titles": titles,
        "DEBUG": settings.DEBUG,
    }
    return render(request, "titles/index.html", context)


class DetailView(LoginRequiredMixin, generic.DetailView):
    model = Title
    template_name = "titles/detail.html"


class DeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Title
    success_url = reverse_lazy("titles:index")


@csrf_exempt
def strava_webhook(request):
    """Called upon activity updates and creates"""
    if request.method == "GET":
        return verify_webhook(request)
    elif request.method == "POST":
        return handle_event(request)
    return JsonResponse(status=405, data={"error": "Method not allowed"})


def verify_webhook(request):
    """Verifies the webhook subscription with Strava."""
    hub_mode = request.GET.get("hub.mode")
    hub_challenge = request.GET.get("hub.challenge")
    hub_verify_token = request.GET.get("hub.verify_token")

    if hub_mode == "subscribe" and hub_verify_token == settings.VERIFY_TOKEN:
        logging.info("WEBHOOK_VERIFIED")
        return JsonResponse({"hub.challenge": hub_challenge})
    else:
        return JsonResponse(status=403, data={"error": "Verification failed"})


def handle_event(request):
    """Handles the POST request for activity updates from Strava."""
    event_data = json.loads(request.body)
    event_type = event_data.get("aspect_type")
    object_type = event_data.get("object_type")
    activity_id = event_data["object_id"]
    logging.info(f"Received event: {event_type}")
    if (object_type == "activity") and (event_type == "create"):
        user = User.objects.filter(
            stravauser__athlete_id=event_data["owner_id"]
        ).first()
        update_activity_name(id=activity_id, user=user)

    return JsonResponse(status=200, data={"status": "Event received"})


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


def strava_mobile_login(request):
    """Connect with Strava button"""
    redirect_uri = request.build_absolute_uri("/strava/callback")
    params = {
        "client_id": settings.STRAVA_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "scope": "activity:read_all,activity:write",
        "approval_prompt": "auto",
    }
    # let appOAuthUrlStravaScheme = URL(string: "strava://oauth/mobile/authorize?client_id=1234321&redirect_uri=YourApp%3A%2F%2Fwww.yourapp.com%2Fen-US&response_type=code&approval_prompt=auto&scope=activity%3Awrite%2Cread&state=test")!
    query_string = urlencode(params)
    url = urlunparse(
        ("https", "www.strava.com", "/oauth/mobile/authorize", "", query_string, "")
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

    if response.status_code != 200:
        logging.info("NO success. Error in OAuth process")
        return redirect("titles:index")

    user = create_user(token_data=response.json())

    login(request, user)
    logging.info("SUCCESS!")
    return redirect("titles:index")


def about(request):
    return render(request, "titles/about.html")


def logged_out(request):
    logout(request)
    return redirect("titles:login")


def faq(request):
    return render(request, "titles/faq.html")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("titles:index")

    first_five = Title.objects.filter(user__username="rhartong-redden").order_by(
        "created_at"
    )[:5]

    context = {
        "form": TitleForm(),
        "titles": reversed(first_five),
        "DEBUG": settings.DEBUG,
    }
    return render(request, "titles/login.html", context)
