from unittest.mock import patch, MagicMock

from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.utils import timezone

from titles.models import Title, Token, Activity, StravaUser
from titles.strava import update_activity_name, create_user


class StravaTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.token = Token.objects.create(
            user=self.user,
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

        update_activity_name(activity_id, self.user)

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

        update_activity_name(id=activity_id, user=self.user)

        self.title.refresh_from_db()
        self.assertIsNone(self.title.used_at)
        self.assertEqual(Activity.objects.count(), 0)


class CreateUserTests(TestCase):

    def test_create_user_with_username(self):
        token_data = {
            "athlete": {
                "id": 1,
                "username": "testuser",
                "firstname": "Test",
                "lastname": "User",
            },
            "access_token": "dummy_access_token",
            "refresh_token": "dummy_refresh_token",
            "expires_at": timezone.now().timestamp() + 3600,  # 1 hour in the future
        }

        user = create_user(token_data)

        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.first_name, "Test")
        self.assertEqual(user.last_name, "User")

        strava_user = StravaUser.objects.get(athlete_id=1)
        self.assertEqual(strava_user.user, user)

        token = Token.objects.get(user=user)
        self.assertEqual(token.access_token, "dummy_access_token")
        self.assertEqual(token.refresh_token, "dummy_refresh_token")

    def test_create_user_without_username(self):
        token_data = {
            "athlete": {
                "id": 2,
                "username": None,  # No username provided
                "firstname": "Another",
                "lastname": "User",
            },
            "access_token": "dummy_access_token_2",
            "refresh_token": "dummy_refresh_token_2",
            "expires_at": timezone.now().timestamp() + 3600,  # 1 hour in the future
        }

        user = create_user(token_data)

        self.assertEqual(user.username, "2")  # Username should default to athlete ID
        self.assertEqual(user.first_name, "Another")
        self.assertEqual(user.last_name, "User")

        strava_user = StravaUser.objects.get(athlete_id=2)
        self.assertEqual(strava_user.user, user)

        token = Token.objects.get(user=user)
        self.assertEqual(token.access_token, "dummy_access_token_2")
        self.assertEqual(token.refresh_token, "dummy_refresh_token_2")

    def test_create_user_existing_user(self):
        existing_user = User.objects.create_user(
            username="existinguser", first_name="Existing", last_name="User"
        )

        token_data = {
            "athlete": {
                "id": 3,
                "username": "existinguser",  # Same username as existing user
                "firstname": "Existing",
                "lastname": "User",
            },
            "access_token": "dummy_access_token_3",
            "refresh_token": "dummy_refresh_token_3",
            "expires_at": timezone.now().timestamp() + 3600,  # 1 hour in the future
        }

        user = create_user(token_data)

        self.assertEqual(user, existing_user)  # Should return the existing user

        # Check if a StravaUser is created or updated correctly
        strava_user = StravaUser.objects.get(athlete_id=3)
        self.assertEqual(strava_user.user, existing_user)

        token = Token.objects.get(user=existing_user)
        self.assertEqual(token.access_token, "dummy_access_token_3")
        self.assertEqual(token.refresh_token, "dummy_refresh_token_3")
