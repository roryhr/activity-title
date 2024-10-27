from django.test import TestCase
from django.http import HttpRequest

from titles.middleware import BlockWordPressPathsMiddleware


class BlockWordPressPathsMiddlewareTests(TestCase):
    def test_block_wlwmanifest_path(self):
        middleware = BlockWordPressPathsMiddleware(get_response=lambda request: None)
        request = HttpRequest()
        request.path = "/website/wp-includes/wlwmanifest.xml"
        response = middleware(request)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.content, b"Blocked")

    def test_block_wlwmanifest_path_with_different_prefix(self):
        middleware = BlockWordPressPathsMiddleware(get_response=lambda request: None)
        request = HttpRequest()
        request.path = "/someprefix/wp-includes/wlwmanifest.xml"
        response = middleware(request)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.content, b"Blocked")

    def test_block_xmlrpc_php(self):
        middleware = BlockWordPressPathsMiddleware(get_response=lambda request: None)
        request = HttpRequest()
        request.path = "/xmlrpc.php"
        response = middleware(request)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.content, b"Blocked")

    def test_allow_other_paths(self):
        middleware = BlockWordPressPathsMiddleware(get_response=lambda request: None)
        request = HttpRequest()
        request.path = "/some/other/path"
        response = middleware(request)
        self.assertIsNone(response)  # No response means the request passed through

    def test_allow_path_without_wp_includes(self):
        middleware = BlockWordPressPathsMiddleware(get_response=lambda request: None)
        request = HttpRequest()
        request.path = "/some/path/with/no/wp-includes"
        response = middleware(request)
        self.assertIsNone(response)  # No response means the request passed through
