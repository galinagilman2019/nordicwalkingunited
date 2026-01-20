# core/middleware.py
from django.http import HttpResponseRedirect

class AdminToPythonAnywhereMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(":")[0].lower()
        if host == "www.nordicwalkingunited.org" and request.path.startswith("/admin/"):
            return HttpResponseRedirect("https://nwu.pythonanywhere.com" + request.get_full_path())
        return self.get_response(request)
