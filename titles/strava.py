import requests
from django.shortcuts import get_object_or_404

from titles.models import Token


def get_token():
    """Get a token from the database
    if there's no token perform the auth and then persist the token"""
    access_token_record = get_object_or_404(Token, athlete_id=23193264)
    if access_token_record:
        return access_token_record.access_token


def update_activity(id, new_name):

    headers = {"Authorization": f"Bearer {get_token()}"}

    # Data to be updated
    data = {"name": new_name}

    # Make the PUT request to update the activity name
    response = requests.put(
        url=f"https://www.strava.com/api/v3/activities/{id}",
        headers=headers,
        data=data,
    )

    # Check if the request was successful
    if response.status_code == 200:
        print("Activity name updated successfully!")

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
