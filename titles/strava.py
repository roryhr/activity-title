import logging

import requests
from django.utils import timezone

from titles.models import Token, Title


def get_token():
    """Get a token from the database"""
    token_record = Token.objects.filter(athlete_id=23193264).last()
    token_record.refresh()
    return token_record.access_token


def update_activity(id):
    t = Title.objects.filter(used_at__isnull=True).order_by("-created_at").first()
    logging.info(f"Attempting to update activity id: {id}")
    response = requests.put(
        url=f"https://www.strava.com/api/v3/activities/{id}",
        headers={"Authorization": f"Bearer {get_token()}"},
        data={"name": t.title},
    )

    if response.status_code == 200:
        logging.info("Activity name updated successfully!")
        t.used_at = timezone.now()
        t.activity_set.create(activity_id=id)
        t.save()


def get_activity(id):
    headers = {"Authorization": f"Bearer {get_token()}"}
    response = requests.get(
        url=f"https://www.strava.com/api/v3/activities/{id}",
        headers=headers,
    )

    if response.status_code == 200:
        logging.info("Activity name updated successfully!")
    return response.json()
