from django.urls import path

from . import views

app_name = "titles"
urlpatterns = [
    path("", views.index, name="index"),
    path("<int:pk>/", views.DetailView.as_view(), name="detail"),
    path("delete/<int:pk>/", views.DeleteView.as_view(), name="delete"),
    path("webhook", views.strava_webhook, name="strava_webhook"),
    path("strava/callback", views.strava_callback, name="strava_callback"),
    path("strava/login", views.strava_login, name="strava_login"),
    path("about/", views.about, name="about"),
    path("faq/", views.faq, name="faq"),
    path("logout/", views.logged_out, name="logout"),
    path("login/", views.login_view, name="login"),
]
