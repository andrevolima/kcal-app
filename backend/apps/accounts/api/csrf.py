from django.middleware.csrf import CsrfViewMiddleware
from rest_framework.exceptions import PermissionDenied


def enforce_csrf(request):
    check = CsrfViewMiddleware(lambda _request: None)
    check.process_request(request)
    reason = check.process_view(request, None, (), {})
    if reason:
        raise PermissionDenied('CSRF validation failed.')
