"""Data-free process and database health endpoints."""

import logging

from django.db import DatabaseError, connection
from django.http import HttpResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET

health_logger = logging.getLogger("orca.health")


@never_cache
@require_GET
def healthz(_request):
    """Report that the Django process can serve HTTP without querying data."""
    return HttpResponse(status=204)


@never_cache
@require_GET
def readyz(_request):
    """Report database connectivity without exposing exception details."""
    try:
        connection.ensure_connection()
    except DatabaseError:
        health_logger.warning(
            "database readiness failed", extra={"event": "database.readiness.failed"}
        )
        return HttpResponse(status=503)
    return HttpResponse(status=204)
