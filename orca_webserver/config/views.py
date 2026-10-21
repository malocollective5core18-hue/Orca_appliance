"""Public views for the ORCA Cloud website."""

from django.conf import settings
from django.http import FileResponse, HttpResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_safe


@never_cache
@require_safe
def home(request):
    """Serve the existing public landing page for GET and HEAD requests."""
    index_file = settings.BASE_DIR / "index.html"
    if request.method == "HEAD":
        response = HttpResponse(content_type="text/html; charset=utf-8")
        response["Content-Length"] = str(index_file.stat().st_size)
        return response
    return FileResponse(
        index_file.open("rb"),
        content_type="text/html; charset=utf-8",
    )
