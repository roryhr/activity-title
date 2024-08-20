from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone

from titles.models import Token

# Create your tests here.
output = {
    "token_type": "Bearer",
    "expires_at": 1723863061,
    "expires_in": 19800,
    "refresh_token": "ba9c6e6ca14c6f231377317adcf0e7f167c4730e",
    "access_token": "3bee7c7f1fb846f3db2421c7558aa982a3d46448",
    "athlete": {
        "id": 23193264,
        "username": "rhartong-redden",
        "resource_state": 2,
        "firstname": "Rory",
        "lastname": "Hartong-Redden",
        "bio": "",
        "city": "Boulder",
        "state": "Colorado",
        "country": "United States",
        "sex": "M",
        "premium": True,
        "summit": True,
        "created_at": "2017-07-06T01:46:42Z",
        "updated_at": "2024-08-05T23:18:17Z",
        "badge_type_id": 1,
        "weight": 89.8113,
        "profile_medium": "https://dgalywyr863hv.cloudfront.net/pictures/athletes/23193264/11231691/2/medium.jpg",
        "profile": "https://dgalywyr863hv.cloudfront.net/pictures/athletes/23193264/11231691/2/large.jpg",
        "friend": None,
        "follower": None,
    },
}


class TokenTest(TestCase):

    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username="testuser", password="12345")

        # Create a StravaToken instance with an expiration time in the future
        self.future_expires_at = timezone.now() + timezone.timedelta(hours=1)
        self.token = Token.objects.create(
            user=self.user,
            access_token="test_access_token",
            refresh_token="test_refresh_token",
            expires_at=self.future_expires_at,
            token_type="Bearer",
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
