# from unittest.mock import patch
#
# from django.test import TestCase
# from django.utils import timezone
# from requests import Response
#
# from titles.models import Token, Title
# from titles.strava import get_token, update_activity, get_activity
#
#
# class TestActivitiesAPI(TestCase):
#     def setUp(self):
#         # Create a mock user and athlete for testing
#         self.user_id = 23193264
#         self.athlete_id = self.user_id
#         self.token_record = Token.objects.create(athlete_id=self.athlete_id)
#         self.title_record = Title.objects.create(title="Test Activity")
#
#     def test_get_token(self):
#         # Test that get_token returns the correct token
#         token = get_token()
#         self.assertEqual(token, self.token_record.access_token)
#
#     @patch("logging.info")
#     def test_update_activity_success(self, mock_info):
#         # Test update_activity updates a successful activity
#         response = Response(status_code=200)
#         with patch("requests.put", return_value=response):
#             update_activity(1)
#             mock_info.assert_called_once_with("Attempting to update activity id: 1")
#             self.title_record.used_at = timezone.now()
#             self.title_record.save()
#
#     @patch("logging.info")
#     def test_update_activity_failure(self, mock_info):
#         # Test update_activity fails when the request is unsuccessful
#         response = Response(status_code=500)
#         with patch("requests.put", return_value=response):
#             update_activity(1)
#             self.assertFalse(update_activity(1))
#             mock_info.assert_called_once_with("Attempting to update activity id: 1")
#
#     @patch("logging.info")
#     def test_get_activity_success(self, mock_info):
#         # Test get_activity returns successful data
#         response = Response(status_code=200, json={"name": "Test Activity"})
#         with patch("requests.get", return_value=response):
#             self.assertEqual(get_activity(1), response.json())
#         mock_info.assert_called_once_with("Activity name updated successfully!")
#
#     @patch("logging.info")
#     def test_get_activity_failure(self, mock_info):
#         # Test get_activity fails when the request is unsuccessful
#         response = Response(status_code=500)
#         with patch("requests.get", return_value=response):
#             self.assertEqual(get_activity(1), None)
#             mock_info.assert_called_once_with("Activity name updated   successfully!")
