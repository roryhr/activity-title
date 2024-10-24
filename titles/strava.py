import logging

import requests
from django.utils import timezone

from titles.models import Token, Title


def get_token(user):
    """Get a token from the database"""
    token_record = Token.objects.filter(user=user).last()
    token_record.refresh()
    return token_record.access_token


def update_activity_name(id, user):
    """Update activity name

    Parameters
    ----------
    id : int
    user : django.contrib.auth.models.User
    """
    logging.info(f"Update activity name {id}, {user}")
    t = (
        Title.objects.filter(user=user)
        .filter(used_at__isnull=True)
        .order_by("-created_at")
        .first()
    )
    logging.info(f"Attempting to update activity id: {id}")
    response = requests.put(
        url=f"https://www.strava.com/api/v3/activities/{id}",
        headers={"Authorization": f"Bearer {get_token(user)}"},
        data={"name": t.title},
    )

    if response.status_code == 200:
        logging.info("Activity name updated successfully!")
        t.used_at = timezone.now()
        t.activity_set.create(activity_id=id)
        t.save()
