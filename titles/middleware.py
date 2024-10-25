from django.http import HttpResponseForbidden, HttpResponsePermanentRedirect


class BlockWordPressPathsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.blocked_paths = [
            "/website/wp-includes/wlwmanifest.xml",
            "/wordpress/wp-includes/wlwmanifest.xml",
            "/web/wp-includes/wlwmanifest.xml",
            "/blog/wp-includes/wlwmanifest.xml",
            "/xmlrpc.php",
            "/wp-includes/wlwmanifest.xml",
        ]

    def __call__(self, request):
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
