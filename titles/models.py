import datetime

import requests
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published")

    def __str__(self):
        return self.question_text

    def was_published_recently(self):
        return self.pub_date >= (timezone.now() - datetime.timedelta(days=1))


class Title(models.Model):
    title = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Activity(models.Model):
    title = models.ForeignKey(Title, on_delete=models.CASCADE)

    activity_id = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Token(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE
    )  # If you want to associate the token with a user
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)
    expires_at = models.DateTimeField()  # When the access token expires
    token_type = models.CharField(max_length=50, default="Bearer")  # Usually "Bearer"
    scope = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - Token"

    def is_expired(self):
        """Check if the token is expired."""
        return timezone.now() >= self.expires_at

    def refresh(self):
        """Refresh the access token using the refresh token."""
        if self.is_expired():
            # Make the request to refresh the token
            data = {
                "client_id": "YOUR_CLIENT_ID",
                "client_secret": "YOUR_CLIENT_SECRET",
                "grant_type": "refresh_token",
                "refresh_token": self.refresh_token,
            }
            response = requests.post("https://www.strava.com/oauth/token", data=data)
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data["access_token"]
                self.refresh_token = token_data.get("refresh_token", self.refresh_token)
                self.expires_at = timezone.now() + timezone.timedelta(
                    seconds=token_data["expires_in"]
                )
                self.save()
            else:
                raise Exception("Failed to refresh token")

    def save(self, *args, **kwargs):
        """Override save method to ensure that expires_at is in UTC."""
        if self.expires_at and not self.expires_at.tzinfo:
            self.expires_at = timezone.make_aware(
                self.expires_at, timezone.timezone.utc
            )
        super().save(*args, **kwargs)


class RefreshToken(models.Model):
    athlete_id = models.IntegerField(db_index=True)  # Indexing athlete ID
    refresh_token_code = models.CharField(
        max_length=255, db_index=True
    )  # Indexing refresh token code
    scope = models.BooleanField()  # Store as a boolean

    def __str__(self):
        return f"Athlete {self.athlete_id} - Refresh Token"


class ShortLivedAccessToken(models.Model):
    athlete_id = models.IntegerField(db_index=True)  # Indexing athlete ID
    scope = models.BooleanField()  # Store as a boolean
    access_token_code = models.CharField(
        max_length=255, db_index=True
    )  # Indexing access token
    expires_at = models.DateTimeField(db_index=True)  # Indexing expiration timestamp

    def __str__(self):
        return f"Athlete {self.athlete_id} - Access Token"
