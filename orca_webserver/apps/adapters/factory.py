"""Environment-selected adapter construction. Unsupported backends fail closed."""

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def get_payment_provider():
    if settings.PAYMENTS_PROVIDER == "fake_clickpesa":
        from apps.adapters.payments import FakeClickPesa

        return FakeClickPesa()
    raise ImproperlyConfigured(f"Payment adapter {settings.PAYMENTS_PROVIDER!r} is not implemented")


def get_storage_backend():
    if settings.STORAGE_BACKEND == "local":
        from apps.adapters.storage import LocalFileStorageBackend

        return LocalFileStorageBackend()
    raise ImproperlyConfigured(f"Storage adapter {settings.STORAGE_BACKEND!r} is not implemented")


def get_sms_backend():
    from apps.accounts.sms import get_sms_backend as build_sms

    return build_sms()


def get_device_transport():
    if settings.DEVICE_TRANSPORT == "database":
        from apps.adapters.device import DatabaseQueueDeviceTransport

        return DatabaseQueueDeviceTransport()
    raise ImproperlyConfigured(f"Device transport {settings.DEVICE_TRANSPORT!r} is not implemented")
