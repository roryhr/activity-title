import json
from unittest.mock import patch

from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from titles.models import Token


class TokenTest(TestCase):
    def setUp(self):
        # Create a StravaToken instance with an expiration time in the future
        self.future_expires_at = timezone.now() + timezone.timedelta(hours=1)
        self.token = Token.objects.create(
            athlete_id=1,
            access_token="test_access_token",
            refresh_token="test_refresh_token",
            expires_at=self.future_expires_at,
        )

    def test_is_expired_false(self):
        """Test that is_expired() returns False when the token is not expired."""
        self.assertFalse(self.token.is_expired())

    def test_is_expired_true(self):
        """Test that is_expired() returns True when the token is expired."""
        # Set the expires_at to a time in the past
        self.token.expires_at = timezone.now() - timezone.timedelta(hours=1)
        self.token.save()

        self.assertTrue(self.token.is_expired())


class WebhookTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.webhook_url = reverse("titles:strava_webhook")

    @patch("titles.views.update_activity")
    def test_webhook_update_event(self, mock_update_activity):
        # Data to be sent in the POST request
        payload = {
            "aspect_type": "update",
            "event_time": 1549560669,
            "object_id": 1234567890,
            "object_type": "activity",
            "owner_id": 9999999,
            "subscription_id": 999999,
        }

        # Perform the POST request
        response = self.client.post(
            self.webhook_url, data=json.dumps(payload), content_type="application/json"
        )

        # Check the response status code and content
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"status": "Event received"})
        mock_update_activity.assert_not_called()

    @patch("titles.views.update_activity")
    def test_webhook_create_event(self, mock_update_activity):
        event_id = 1234567890
        payload = {
            "aspect_type": "create",
            "event_time": 1549560669,
            "object_id": event_id,
            "object_type": "activity",
        }

        response = self.client.post(
            self.webhook_url, data=json.dumps(payload), content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"status": "Event received"})
        mock_update_activity.assert_called_once_with(id=event_id)
