import json
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase, Client, RequestFactory
from django.urls import reverse

from titles.models import StravaUser
from titles.views import strava_webhook, handle_event


class WebhookTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.webhook_url = reverse("titles:strava_webhook")
        self.factory = RequestFactory()
        self.mock_user = User.objects.create_user(username="testuser")
        self.athlete_id = 123456
        self.mock_strava_user = StravaUser.objects.create(
            user=self.mock_user, athlete_id=self.athlete_id
        )

    @patch("titles.views.update_activity_name")
    def test_webhook_update_event(self, mock_update_activity_name):
        payload = {
            "aspect_type": "update",
            "event_time": 1549560669,
            "object_id": 1234567890,
            "object_type": "activity",
            "owner_id": 9999999,
            "subscription_id": 999999,
        }

        response = self.client.post(
            self.webhook_url, data=json.dumps(payload), content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"status": "Event received"})
        mock_update_activity_name.assert_not_called()

    @patch("titles.views.update_activity_name")
    def test_handle_create_event(self, mock_update_activity_name):
        event_id = 1234567890
        payload = {
            "aspect_type": "create",
            "event_time": 1549560669,
            "object_id": event_id,
            "object_type": "activity",
            "owner_id": self.athlete_id,
        }
        request = self.factory.post(
            self.webhook_url, data=json.dumps(payload), content_type="application/json"
        )
        response = handle_event(request)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"status": "Event received"})
        mock_update_activity_name.assert_called_once_with(
            id=event_id, user=self.mock_user
        )
