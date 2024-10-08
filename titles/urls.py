from django.urls import path

from . import views

app_name = "titles"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("<int:pk>/", views.DetailView.as_view(), name="detail"),
    path("webhook", views.strava_webhook, name="strava_webhook"),
    path("strava/callback", views.strava_callback, name="strava_callback"),
    path("strava/login", views.strava_login, name="strava_login"),
    path("about/", views.about, name="about"),
]
