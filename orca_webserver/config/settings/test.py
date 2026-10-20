"""Fast isolated settings; tests never need Supabase or provider credentials."""

from .base import *  # noqa: F403

DEBUG = False
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
PAYMENTS_LIVE_ENABLED = False
SMS_BACKEND = "console"
MIDDLEWARE = [
    item for item in MIDDLEWARE if item != "whitenoise.middleware.WhiteNoiseMiddleware"
]
