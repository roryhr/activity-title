#!/bin/bash

# Handy one-off curls to manage the webhook subscription and
# test my API
if [ -f .env ]; then
  # shellcheck disable=SC2046
  export $(grep -v '^#' .env | xargs)
else
  echo ".env file not found!"
fi

# Create a subscription
curl -X POST \
  https://www.strava.com/api/v3/push_subscriptions \
  -F client_id="$STRAVA_CLIENT_ID" \
  -F client_secret="$STRAVA_CLIENT_SECRET" \
  -F callback_url=https://strava-deck.fly.dev/webhook \
  -F verify_token=STRAVA


## View a subscription
#curl -sG https://www.strava.com/api/v3/push_subscriptions \
#  -d client_id="$STRAVA_CLIENT_ID"  \
#  -d client_secret="$STRAVA_CLIENT_SECRET" \
#  | jq


### Delete a subscription
## 204 No Content if the delete is successful
#curl -v -X DELETE https://www.strava.com/api/v3/push_subscriptions/262230 \
#  -G \
#  --data-urlencode "client_id=$STRAVA_CLIENT_ID" \
#  --data-urlencode "client_secret=$STRAVA_CLIENT_SECRET"


## Test the webhook
#curl -X POST http://127.0.0.1:8000/webhook \
#-H 'Content-Type: application/json' \
#-d '{
#    "aspect_type": "update",
#    "event_time": 1549560669,
#    "object_id": 1234567890,
#    "object_type": "activity",
#    "owner_id": 9999999,
#    "subscription_id": 999999
#  }'