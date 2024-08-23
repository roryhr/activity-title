import requests
from django.shortcuts import get_object_or_404
from django.utils import timezone

from titles.models import Token, Title


def get_token():
    """Get a token from the database"""
    token_record = get_object_or_404(Token, athlete_id=23193264)
    token_record.refresh()
    return token_record.access_token


def update_activity(id):
    t = Title.objects.filter(used_at__isnull=True).order_by("-created_at").first()

    response = requests.put(
        url=f"https://www.strava.com/api/v3/activities/{id}",
        headers={"Authorization": f"Bearer {get_token()}"},
        data={"name": t.title},
    )

    if response.status_code == 200:
        print("Activity name updated successfully!")
        t.used_at = timezone.now()
    print(response.json())


def get_activity(id):
    headers = {"Authorization": f"Bearer {get_token()}"}
    response = requests.get(
        url=f"https://www.strava.com/api/v3/activities/{id}",
        headers=headers,
    )

    if response.status_code == 200:
        print("Activity name updated successfully!")
    return response.json()


if __name__ == "__main__":
    get_activity(12149146937)
