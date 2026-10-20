"""Development-only SMS adapter. No real SMS provider is configured in Phase 1."""

from typing import Protocol

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class SMSBackend(Protocol):
    def send(self, phone_number: str, message: str) -> None: ...


def mask_phone_number(phone_number: str) -> str:
    """Keep only the final four digits visible in developer output."""
    digits = "".join(character for character in phone_number if character.isdigit())
    return f"***{digits[-4:]}" if digits else "***"


class ConsoleSMSBackend:
    """Print a development test message only when Django DEBUG is explicitly enabled."""

    def send(self, phone_number: str, message: str) -> None:
        if not settings.DEBUG:
            raise ImproperlyConfigured("Console SMS is available only when DEBUG=True")
        print(f"[DEV SMS to {mask_phone_number(phone_number)}] {message}")


def get_sms_backend() -> SMSBackend:
    if settings.SMS_BACKEND != "console":
        raise ImproperlyConfigured("No approved SMS provider is implemented")
    return ConsoleSMSBackend()
