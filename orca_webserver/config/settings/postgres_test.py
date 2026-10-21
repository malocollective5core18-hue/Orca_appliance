"""PostgreSQL test settings for locking, uniqueness races, and CI integration tests."""

import os

from django.core.exceptions import ImproperlyConfigured

from .test import *  # noqa: F403
from .base import database_from_url

_database_url = os.environ.get("DATABASE_URL", "")
if not _database_url:
    raise ImproperlyConfigured("DATABASE_URL is required for config.settings.postgres_test")
DATABASES = {"default": database_from_url(_database_url)}
