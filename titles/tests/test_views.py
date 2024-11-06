import json
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase, Client, RequestFactory
from django.urls import reverse

from titles.models import StravaUser, Title
from titles.views import handle_event

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class IndexViewPaginationTest(TestCase):
    def setUp(self):
        # Set up a user and some titles for testing
        self.user = User.objects.create_user(username="testuser", password="password")
        self.client.login(username="testuser", password="password")

        # Create multiple titles for pagination (assuming 10 titles for a page size of 5)
        self.titles = [
            Title.objects.create(title=f"Title {i}", user=self.user) for i in range(10)
        ]

    def test_index_view_pagination_first_page(self):
        # Access the first page of the index view
        response = self.client.get(reverse("titles:index"))

        # Check that the response is successful
        self.assertEqual(response.status_code, 200)

        # Check that only 5 titles are displayed (first page)
        self.assertEqual(len(response.context["titles"]), 5)

        # Verify the pagination is working as expected
        self.assertTrue(response.context["titles"].has_next())
        self.assertFalse(response.context["titles"].has_previous())
        self.assertEqual(response.context["titles"].number, 1)

    def test_index_view_pagination_second_page(self):
        # Access the second page of the index view
        response = self.client.get(reverse("titles:index") + "?page=2")

        # Check that the response is successful
        self.assertEqual(response.status_code, 200)

        # Check that only 5 titles are displayed (second page)
        self.assertEqual(len(response.context["titles"]), 5)

        # Verify the pagination is working as expected
        self.assertFalse(response.context["titles"].has_next())
        self.assertTrue(response.context["titles"].has_previous())
        self.assertEqual(response.context["titles"].number, 2)

    def test_index_view_pagination_invalid_page(self):
        # Access an invalid page number
        response = self.client.get(reverse("titles:index") + "?page=999")

        # Check that the response redirects to a valid page (e.g., the last page)
        self.assertEqual(response.status_code, 200)

        # Check that we are on the second page (last page in this case)
        self.assertEqual(response.context["titles"].number, 2)


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
