import re

from django.http import HttpResponseForbidden, HttpResponsePermanentRedirect


class BlockWordPressPathsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Use a regex to match paths containing "wp-includes/wlwmanifest.xml"
        self.wlwmanifest_regex = re.compile(r"/[^/]+/wp-includes/wlwmanifest\.xml")
        self.blocked_paths = ["/xmlrpc.php"]

    def __call__(self, request):
        # Check if the path matches the regex
        if self.wlwmanifest_regex.search(request.path):
            return HttpResponseForbidden("Blocked")

        # Check if the path is in the blocked paths list
        if request.path in self.blocked_paths:
            return HttpResponseForbidden("Blocked")

        return self.get_response(request)


class CanonicalDomainMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host()
        if host in ["www.activitytitle.com", "m.activitytitle.com"]:
            return HttpResponsePermanentRedirect(
                f"https://activitytitle.com{request.path}"
            )
        return self.get_response(request)
