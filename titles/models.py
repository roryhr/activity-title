import logging

import requests
from django.db import models
from django.utils import timezone

from titler import settings


class Title(models.Model):
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    used_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title


class Activity(models.Model):
    title = models.ForeignKey(Title, on_delete=models.CASCADE)
    activity_id = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Token(models.Model):
    """Bearer token for API auth"""

    athlete_id = models.IntegerField(db_index=True)
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)
    expires_at = models.DateTimeField()  # When the access token expires

    def __str__(self):
        return f"{self.athlete_id} - Token"

    def is_expired(self):
        """Check if the token is expired."""
        return timezone.now() >= self.expires_at

    def refresh(self):
        """Refresh the access token using the refresh token."""
        if not self.is_expired():
            logging.info("TOKEN GOOD")
            return None

        response = requests.post(
            "https://www.strava.com/oauth/token",
            data={
                "client_id": settings.STRAVA_CLIENT_ID,
                "client_secret": settings.STRAVA_CLIENT_SECRET,
                "grant_type": "refresh_token",
                "refresh_token": self.refresh_token,
            },
        )

        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data["access_token"]
            self.refresh_token = token_data.get("refresh_token", self.refresh_token)
            self.expires_at = timezone.now() + timezone.timedelta(
                seconds=token_data["expires_in"]
            )
            self.save()

    def save(self, *args, **kwargs):
        """Override save method to ensure that expires_at is in UTC."""
        if self.expires_at and not self.expires_at.tzinfo:
            self.expires_at = timezone.make_aware(
                self.expires_at, timezone.timezone.utc
            )
        super().save(*args, **kwargs)
