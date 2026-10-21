from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class FeePreview:
    amount_tzs: int
    fee_tzs: int
    total_tzs: int


@dataclass(frozen=True)
class CollectionResult:
    provider_reference: str
    status: str
    amount_tzs: int
    idempotency_key: str


@dataclass(frozen=True)
class ParsedWebhook:
    event_id: str
    provider_reference: str
    status: str
    amount_tzs: int
    sequence: int


class PaymentProvider(Protocol):
    def initiate_collection(
        self, *, idempotency_key: str, amount_tzs: int, phone_number: str
    ) -> CollectionResult: ...

    def preview_fees(self, amount_tzs: int) -> FeePreview: ...

    def query_status(self, provider_reference: str) -> str: ...

    def verify_webhook(self, body: bytes, signature: str) -> bool: ...

    def parse_webhook(self, body: bytes) -> ParsedWebhook: ...


class PaymentProviderError(Exception):
    """Base exception for provider-port failures; callers must not expose details."""


class PaymentTimeout(PaymentProviderError, TimeoutError):
    pass
