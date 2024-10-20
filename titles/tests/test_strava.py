import json
from unittest.mock import patch, MagicMock

from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.utils import timezone

from titles.models import Title, Token, Activity
from titles.strava import update_activity, get_token


class StravaTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.token = Token.objects.create(
            athlete_id=23193264,
            access_token="test_access_token",
            refresh_token="test_refresh_token",
            expires_at=timezone.now() + timezone.timedelta(days=1),
        )
        self.title = Title.objects.create(user=self.user, title="Test Title")

    @patch("titles.strava.requests.put")
    def test_update_activity_success(self, mock_put):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_put.return_value = mock_response

        activity_id = 12345

        update_activity(activity_id, self.user)

        mock_put.assert_called_with(
            url=f"https://www.strava.com/api/v3/activities/{activity_id}",
            headers={"Authorization": f"Bearer test_access_token"},
            data={"name": "Test Title"},
        )
        self.title.refresh_from_db()
        self.assertIsNotNone(self.title.used_at)
        self.assertEqual(Activity.objects.count(), 1)

    @patch("titles.strava.requests.put")
    def test_update_activity_failure(self, mock_put):
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_put.return_value = mock_response

        activity_id = 12345

        update_activity(activity_id, self.user)

        self.title.refresh_from_db()
        self.assertIsNone(self.title.used_at)
        self.assertEqual(Activity.objects.count(), 0)
