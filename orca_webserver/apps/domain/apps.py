from django.apps import AppConfig


class DomainConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.domain"
    label = "domain"
    verbose_name = "ORCA Domain"

    def ready(self):
        from . import admin  # noqa: F401
