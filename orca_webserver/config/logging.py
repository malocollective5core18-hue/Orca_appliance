"""JSON log formatter that deliberately omits messages and request URLs."""

import json
import logging
from datetime import UTC, datetime

from config.middleware import request_id_context


class SafeJsonFormatter(logging.Formatter):
    """Emit only safe, structured fields; never serialize arbitrary log text."""

    SAFE_EVENTS = {
        "http.request.completed",
        "database.readiness.failed",
        "application.startup",
    }

    def format(self, record: logging.LogRecord) -> str:
        event = getattr(record, "event", "")
        if not isinstance(event, str) or event not in self.SAFE_EVENTS:
            event = "unstructured_log_suppressed"

        request = getattr(record, "request", None)
        request_id = getattr(record, "request_id", None) or getattr(
            request, "request_id", None
        ) or request_id_context.get()
        if not isinstance(request_id, str) or len(request_id) > 64:
            request_id = "-"

        payload = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "event": event,
            "request_id": request_id,
        }
        status_code = getattr(record, "status_code", None)
        if isinstance(status_code, int) and 100 <= status_code <= 599:
            payload["status_code"] = status_code
        method = getattr(record, "method", None)
        if isinstance(method, str) and method in {
            "GET",
            "POST",
            "PUT",
            "PATCH",
            "DELETE",
            "HEAD",
            "OPTIONS",
        }:
            payload["method"] = method
        return json.dumps(payload, separators=(",", ":"))
