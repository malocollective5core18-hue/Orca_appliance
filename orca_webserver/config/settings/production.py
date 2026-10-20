"""Hardened Render production settings; required values fail closed."""

import os

from django.core.exceptions import ImproperlyConfigured

from . import base
from .base import *  # noqa: F403
from .base import database_from_url, env_bool, env_csv

DEBUG = False
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "")
if len(SECRET_KEY) < 50 or "change-me" in SECRET_KEY.lower() or "fake" in SECRET_KEY.lower():
    raise ImproperlyConfigured("DJANGO_SECRET_KEY must be a real secret of at least 50 characters")

DATABASE_URL = os.environ.get("DATABASE_URL", "")
if not DATABASE_URL:
    raise ImproperlyConfigured("DATABASE_URL is required in production")
DATABASES = {"default": database_from_url(DATABASE_URL, require_ssl=True)}

DATABASE_CONNECTION_MODE = os.environ.get("DATABASE_CONNECTION_MODE", "")
if DATABASE_CONNECTION_MODE != "session":
    raise ImproperlyConfigured("DATABASE_CONNECTION_MODE must be session in Render production")
if env_bool("DISABLE_SERVER_SIDE_CURSORS", False):
    raise ImproperlyConfigured(
        "Server-side cursors must remain enabled with the selected session pooler"
    )

ALLOWED_HOSTS = env_csv("ALLOWED_HOSTS")
CSRF_TRUSTED_ORIGINS = env_csv("CSRF_TRUSTED_ORIGINS")
if not ALLOWED_HOSTS or not CSRF_TRUSTED_ORIGINS:
    raise ImproperlyConfigured("ALLOWED_HOSTS and CSRF_TRUSTED_ORIGINS must be configured")
if base.PAYMENTS_LIVE_ENABLED:
    raise ImproperlyConfigured("Live payments are not implemented in Phase 1")
if base.SMS_BACKEND != "console":
    raise ImproperlyConfigured("An SMS provider is not approved or implemented yet")

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SECURE_REDIRECT_EXEMPT = [r"^healthz$", r"^readyz$"]
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31_536_000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_REFERRER_POLICY = "same-origin"
