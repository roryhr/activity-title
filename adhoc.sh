#!/bin/bash

#Handy one-off scripts
if [ -f .env ]; then
  # shellcheck disable=SC2046
  export $(grep -v '^#' .env | xargs)
else
  echo ".env file not found!"
fi

## Create a subscription
#curl -X POST \
#  https://www.strava.com/api/v3/push_subscriptions \
#  -F client_id="$STRAVA_CLIENT_ID" \
#  -F client_secret="$STRAVA_CLIENT_SECRET" \
#  -F callback_url=https://568a-98-245-200-18.ngrok-free.app/webhook \
#  -F verify_token=STRAVA


## View a subscription
#curl -G https://www.strava.com/api/v3/push_subscriptions \
#  -d client_id="$STRAVA_CLIENT_ID"  \
#  -d client_secret="$STRAVA_CLIENT_SECRET" \
#  | jq


## Delete a subscription
#curl -vX DELETE \
#"https://www.strava.com/api/v3/push_subscriptions/$STRAVA_CLIENT_ID?client_id=$STRAVA_CLIENT_ID&client_secret=$STRAVA_CLIENT_SECRET"
