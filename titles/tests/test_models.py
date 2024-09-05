from django.test import TestCase
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
