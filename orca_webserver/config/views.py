"""Small human-facing pages for the ORCA Cloud service."""

from django.conf import settings
from django.http import HttpResponse
from django.urls import reverse
from django.utils.html import format_html
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_safe


@never_cache
@require_safe
def home(_request):
    """Render a data-free service welcome page for GET and HEAD requests."""
    mode = "demo" if settings.SERVER_MODE == "demo" else "live"
    body = format_html(
        "<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
        "<title>ORCA Cloud</title></head><body><main><h1>ORCA Cloud</h1>"
        "<p>Service mode: <strong>{}</strong></p><nav aria-label=\"Service checks\">"
        "<ul><li><a href=\"{}\">Process health</a></li>"
        "<li><a href=\"{}\">Database readiness</a></li></ul></nav></main></body></html>",
        mode,
        reverse("healthz"),
        reverse("readyz"),
    )
    return HttpResponse(body, content_type="text/html; charset=utf-8")
