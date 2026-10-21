"""Local-only storage adapters for development and deterministic tests."""

from dataclasses import dataclass

from django.core.exceptions import SuspiciousFileOperation
from django.core import signing
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


def _validate_key(key: str) -> str:
    normalized = key.replace("\\", "/").strip("/")
    parts = normalized.split("/")
    if not normalized or any(part in {"", ".", ".."} for part in parts):
        raise SuspiciousFileOperation("Storage keys must be safe relative paths")
    return normalized


class LocalFileStorageBackend:
    """Uses Django's configured default STORAGES backend and local MEDIA_ROOT."""

    def __init__(self, storage=None):
        self.storage = storage or default_storage

    def put(self, key: str, content: bytes, content_type: str) -> str:
        del content_type  # validated by the image validation service before this boundary
        safe_key = _validate_key(key)
        saved = self.storage.save(safe_key, ContentFile(content))
        return saved

    def delete(self, key: str) -> None:
        self.storage.delete(_validate_key(key))

    def exists(self, key: str) -> bool:
        return self.storage.exists(_validate_key(key))

    def url(self, key: str) -> str:
        return self.storage.url(_validate_key(key))

    def signed_url(self, key: str, *, expires_in: int) -> str:
        if not 1 <= expires_in <= 86400:
            raise ValueError("expires_in must be between 1 second and 24 hours")
        token = signing.TimestampSigner(salt="orca.local-private-storage").sign(_validate_key(key))
        return f"local-private://{token}?max_age={expires_in}"

    @staticmethod
    def verify_signed_url(url: str) -> str:
        if not url.startswith("local-private://"):
            raise ValueError("Not a local private storage URL")
        token, _, query = url.removeprefix("local-private://").partition("?")
        parameters = dict(item.split("=", 1) for item in query.split("&") if "=" in item)
        max_age = int(parameters.get("max_age", "0"))
        if max_age < 1:
            raise signing.SignatureExpired("Missing or invalid local URL expiry")
        return signing.TimestampSigner(salt="orca.local-private-storage").unsign(token, max_age=max_age)


@dataclass
class MemoryObject:
    content: bytes
    content_type: str


class InMemoryStorageBackend:
    def __init__(self):
        self.objects: dict[str, MemoryObject] = {}

    def put(self, key: str, content: bytes, content_type: str) -> str:
        key = _validate_key(key)
        self.objects[key] = MemoryObject(bytes(content), content_type)
        return key

    def delete(self, key: str) -> None:
        self.objects.pop(_validate_key(key), None)

    def exists(self, key: str) -> bool:
        return _validate_key(key) in self.objects

    def url(self, key: str) -> str:
        key = _validate_key(key)
        if not self.exists(key):
            raise FileNotFoundError(key)
        return f"memory-public://{key}"

    def signed_url(self, key: str, *, expires_in: int) -> str:
        if not 1 <= expires_in <= 86400:
            raise ValueError("expires_in must be between 1 second and 24 hours")
        if not self.exists(key):
            raise FileNotFoundError(key)
        token = signing.TimestampSigner(salt="orca.memory-private-storage").sign(_validate_key(key))
        return f"memory-private://{token}?max_age={expires_in}"

    @staticmethod
    def verify_signed_url(url: str) -> str:
        if not url.startswith("memory-private://"):
            raise ValueError("Not an in-memory private storage URL")
        token, _, query = url.removeprefix("memory-private://").partition("?")
        parameters = dict(item.split("=", 1) for item in query.split("&") if "=" in item)
        max_age = int(parameters.get("max_age", "0"))
        if max_age < 1:
            raise signing.SignatureExpired("Missing or invalid in-memory URL expiry")
        return signing.TimestampSigner(salt="orca.memory-private-storage").unsign(token, max_age=max_age)
