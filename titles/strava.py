import requests
from django.shortcuts import get_object_or_404

from titler import settings
from titles.models import ShortLivedAccessToken

# Step 1: Define your credentials
client_id = settings.STRAVA_CLIENT_ID
redirect_uri = "http://localhost/exchange_token"
authorization_url = "https://www.strava.com/oauth/authorize"
token_url = "https://www.strava.com/oauth/token"

# Step 2: Get the authorization code
params = {
    "client_id": client_id,
    "response_type": "code",
    "redirect_uri": redirect_uri,
    "scope": "read,activity:read",  # Specify the scopes you need
    "approval_prompt": "auto",
}


activity_id = "12149146937"
# new_name = "TESTING Name yo yo yo"
new_name = "Donut Ride to Lamars"

# Strava API endpoint for updating an activity
url = f"https://www.strava.com/api/v3/activities/{activity_id}"


def get_token():
    """Get a token from the database
    if there's no token perform the auth and then persist the token"""
    access_token_record = get_object_or_404(ShortLivedAccessToken, athlete_id=23193264)
    if access_token_record:
        return access_token_record.access_token_code


def update_activity(id, new_name):
    athlete_id = 2

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


if __name__ == "__main__":
    update_activity(12149146937, "testing 124")
