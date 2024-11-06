import logging

import requests
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.utils import timezone

from titles.models import Token, Title, StravaUser


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
        Activity id to change
    user : django.contrib.auth.models.User
    """
    logging.info(f"Update activity name {id}, {user}")
    t = (
        Title.objects.filter(user=user)
        .filter(used_at__isnull=True)
        .order_by("-created_at")
        .last()
    )

    logging.info(f"Attempting to update activity id to title: {id}, {t.title}")
    response = requests.put(
        url=f"https://www.strava.com/api/v3/activities/{id}",
        headers={"Authorization": f"Bearer {get_token(user)}"},
        data={"name": t.title},
    )
    logging.info(f"Activities API response {response.content}")
    if response.status_code == 200:
        logging.info("Activity name updated successfully!")
        t.used_at = timezone.now()
        t.save()

        try:
            _, created = t.activity_set.get_or_create(activity_id=id)
            if created:
                logging.info(f"New activity created with ID {id}")
            else:
                logging.info(f"Activity with ID {id} already exists")
        except IntegrityError:
            logging.error(
                f"Failed to create or find existing activity with ID {id} due to IntegrityError"
            )


def create_user(token_data):
    """Create a new user and associated StravaUser and Token based on the provided token data.

    Parameters
    ----------
    token_data : dict
        A dictionary containing user data returned from the Strava API.
        Expected keys are:
            - "athlete": A dictionary containing information about the athlete:
                - "id": Unique identifier for the athlete.
                - "username": The username of the athlete (can be None).
                - "firstname": The first name of the athlete.
                - "lastname": The last name of the athlete.
            - "access_token": The access token for the Strava API.
            - "refresh_token": The refresh token for the Strava API.
            - "expires_at": The expiration time for the access token in Unix timestamp format.

    Returns
    -------
    User
        The User object associated with the newly created or retrieved user.

    Notes
    -----
    If the athlete does not have a username, the username will be set to their athlete ID.
    The function will log the incoming token data for debugging purposes.

    Raises
    ------
    KeyError
        If any of the expected keys are missing from `token_data` or `user_data`.
    """
    logging.info("Create user")
    logging.info(token_data)
    user_data = token_data["athlete"]
    athlete_id = user_data["id"]

    if not user_data["username"]:
        username = str(athlete_id)
    else:
        username = user_data["username"]

    user, _ = User.objects.get_or_create(
        username=username,
        defaults={
            "username": username,
            "first_name": user_data["firstname"],
            "last_name": user_data["lastname"],
        },
    )
    StravaUser.objects.get_or_create(athlete_id=athlete_id, user=user)

    Token.objects.update_or_create(
        user=user,
        defaults={
            "access_token": token_data["access_token"],
            "refresh_token": token_data["refresh_token"],
            "expires_at": timezone.datetime.fromtimestamp(token_data["expires_at"]),
        },
    )

    return user
