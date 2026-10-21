"""Request correlation without logging request URLs or customer data."""

import logging
from contextvars import ContextVar, Token
from uuid import uuid4


request_id_context: ContextVar[str] = ContextVar("request_id", default="-")
request_logger = logging.getLogger("orca.request")


class RequestIdMiddleware:
    """Generate a server-owned correlation ID for each request."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = uuid4().hex
        request.request_id = request_id
        token: Token = request_id_context.set(request_id)
        try:
            response = self.get_response(request)
            response["X-Request-ID"] = request_id
            request_logger.info(
                "request completed",
                extra={
                    "event": "http.request.completed",
                    "method": request.method,
                    "status_code": response.status_code,
                    "request_id": request_id,
                },
            )
            return response
        finally:
            request_id_context.reset(token)
