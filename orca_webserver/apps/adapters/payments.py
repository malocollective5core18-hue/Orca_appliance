"""Scriptable fake payment provider; deliberately contains no HTTP client."""

import hashlib
import hmac
import json
from collections import deque

from apps.ports.payment import (
    CollectionResult,
    FeePreview,
    ParsedWebhook,
    PaymentTimeout,
)


class FakeClickPesa:
    """Deterministic local fake with queued outcomes for offline tests."""

    OUTCOMES = {"success", "failure", "timeout", "duplicate"}
    WEBHOOK_OUTCOMES = {"success", "failure", "forged", "out_of_order", "amount_mismatch"}

    def __init__(self, *, outcomes=(), secret: bytes = b"fake-clickpesa-test-key", fee_bps: int = 0):
        if fee_bps < 0:
            raise ValueError("fee_bps cannot be negative")
        self._outcomes = deque(outcomes)
        self._secret = secret
        self._fee_bps = fee_bps
        self._by_idempotency: dict[str, CollectionResult] = {}
        self._statuses: dict[str, str] = {}
        self._counter = 0

    def preview_fees(self, amount_tzs: int) -> FeePreview:
        if amount_tzs <= 0:
            raise ValueError("amount_tzs must be positive")
        fee = (amount_tzs * self._fee_bps + 9999) // 10000
        return FeePreview(amount_tzs=amount_tzs, fee_tzs=fee, total_tzs=amount_tzs + fee)

    def initiate_collection(self, *, idempotency_key: str, amount_tzs: int, phone_number: str) -> CollectionResult:
        if not idempotency_key.strip() or amount_tzs <= 0 or not phone_number.strip():
            raise ValueError("idempotency key, positive amount, and phone are required")
        previous = self._by_idempotency.get(idempotency_key)
        if previous:
            return previous
        outcome = self._outcomes.popleft() if self._outcomes else "success"
        if outcome not in self.OUTCOMES:
            raise ValueError(f"Unsupported collection outcome: {outcome}")
        if outcome == "timeout":
            raise PaymentTimeout("Fake provider timeout")
        self._counter += 1
        reference = f"fake-{self._counter:08d}"
        status = {"success": "succeeded", "duplicate": "duplicate", "failure": "failed"}[outcome]
        result = CollectionResult(reference, status, amount_tzs, idempotency_key)
        self._by_idempotency[idempotency_key] = result
        self._statuses[reference] = status
        return result

    def query_status(self, provider_reference: str) -> str:
        try:
            return self._statuses[provider_reference]
        except KeyError as exc:
            raise LookupError("Unknown fake payment reference") from exc

    def create_webhook(
        self,
        *,
        outcome: str = "success",
        provider_reference: str = "fake-00000001",
        amount_tzs: int = 1000,
        event_id: str = "event-1",
        sequence: int = 1,
    ) -> tuple[bytes, str]:
        if outcome not in self.WEBHOOK_OUTCOMES:
            raise ValueError(f"Unsupported webhook outcome: {outcome}")
        body_obj: dict[str, Any] = {
            "event_id": event_id,
            "provider_reference": provider_reference,
            "status": "failed" if outcome == "failure" else "succeeded",
            "amount_tzs": amount_tzs + 1 if outcome == "amount_mismatch" else amount_tzs,
            "sequence": max(0, sequence - 1) if outcome == "out_of_order" else sequence,
        }
        body = json.dumps(body_obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
        signature = hmac.new(self._secret, body, hashlib.sha256).hexdigest()
        if outcome == "forged":
            signature = "0" * 64 if signature != "0" * 64 else "1" * 64
        return body, signature

    def verify_webhook(self, body: bytes, signature: str) -> bool:
        expected = hmac.new(self._secret, body, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature)

    def parse_webhook(self, body: bytes) -> ParsedWebhook:
        try:
            data = json.loads(body)
            parsed = ParsedWebhook(
                event_id=str(data["event_id"]),
                provider_reference=str(data["provider_reference"]),
                status=str(data["status"]),
                amount_tzs=int(data["amount_tzs"]),
                sequence=int(data["sequence"]),
            )
        except (ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
            raise ValueError("Malformed fake webhook") from exc
        if parsed.status not in {"succeeded", "failed"} or parsed.amount_tzs <= 0 or parsed.sequence < 0:
            raise ValueError("Invalid fake webhook fields")
        return parsed
