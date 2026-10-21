"""Small state transition functions; providers and HTTP views stay outside the domain."""

from django.db import transaction
from django.utils import timezone

from .models import DeviceCommand, PairingCode, Payment, ProviderWebhookEvent
from .statuses import CommandStatus, PairingStatus, PaymentStatus


PAYMENT_TRANSITIONS = {
    PaymentStatus.PENDING: {PaymentStatus.PROCESSING, PaymentStatus.FAILED, PaymentStatus.CANCELLED},
    PaymentStatus.PROCESSING: {PaymentStatus.SUCCEEDED, PaymentStatus.FAILED, PaymentStatus.CANCELLED},
    PaymentStatus.SUCCEEDED: {PaymentStatus.REVERSED},
    PaymentStatus.FAILED: set(),
    PaymentStatus.CANCELLED: set(),
    PaymentStatus.REVERSED: set(),
}
COMMAND_TRANSITIONS = {
    CommandStatus.PENDING: {CommandStatus.QUEUED, CommandStatus.CANCELLED},
    CommandStatus.QUEUED: {CommandStatus.DELIVERED, CommandStatus.CANCELLED},
    CommandStatus.DELIVERED: {CommandStatus.ACKNOWLEDGED, CommandStatus.FAILED},
    CommandStatus.ACKNOWLEDGED: set(),
    CommandStatus.FAILED: {CommandStatus.QUEUED},
    CommandStatus.CANCELLED: set(),
}
PAIRING_TRANSITIONS = {
    PairingStatus.PENDING: {PairingStatus.CONSUMED, PairingStatus.EXPIRED, PairingStatus.REVOKED},
    PairingStatus.CONSUMED: set(),
    PairingStatus.EXPIRED: set(),
    PairingStatus.REVOKED: set(),
}


def _transition(instance, target, allowed, *, update_fields=()):
    if target not in allowed[instance.status]:
        raise ValueError(f"Illegal {type(instance).__name__} transition: {instance.status} -> {target}")
    instance.status = target
    fields = {"status", "updated_at"} if hasattr(instance, "updated_at") else {"status"}
    fields.update(update_fields)
    instance.save(update_fields=tuple(fields))
    return instance


def transition_payment(payment: Payment, target: str) -> Payment:
    with transaction.atomic():
        locked = Payment.objects.select_for_update().get(pk=payment.pk)
        _transition(locked, target, PAYMENT_TRANSITIONS)
        payment.status = locked.status
        payment.updated_at = locked.updated_at
        return payment


def transition_command(command, target: str, *, clock=None, **fields):
    now = clock.now() if clock else timezone.now()
    with transaction.atomic():
        locked = DeviceCommand.objects.select_for_update().get(pk=command.pk)
        if target == CommandStatus.DELIVERED and "delivered_at" not in fields:
            fields["delivered_at"] = now
        if target == CommandStatus.ACKNOWLEDGED and "acknowledged_at" not in fields:
            fields["acknowledged_at"] = now
        for field, value in fields.items():
            setattr(locked, field, value)
        _transition(locked, target, COMMAND_TRANSITIONS, update_fields=tuple(fields))
        command.status = locked.status
        for field in fields:
            setattr(command, field, getattr(locked, field))
        return command


@transaction.atomic
def transition_pairing_code(pairing_code: PairingCode, target: str, *, clock=None, now=None) -> PairingCode:
    if clock is not None and now is not None:
        raise ValueError("Pass either now or clock, not both")
    now = clock.now() if clock else now or timezone.now()
    with transaction.atomic():
        code = PairingCode.objects.select_for_update().get(pk=pairing_code.pk)
        if target == PairingStatus.CONSUMED:
            if code.expires_at <= now:
                _transition(code, PairingStatus.EXPIRED, PAIRING_TRANSITIONS)
                pairing_code.status = code.status
                return pairing_code
            code.consumed_at = now
            _transition(code, target, PAIRING_TRANSITIONS, update_fields=("consumed_at",))
        elif target == PairingStatus.EXPIRED and code.expires_at > now:
            raise ValueError("Pairing code cannot expire before its expiry time")
        else:
            _transition(code, target, PAIRING_TRANSITIONS)
        pairing_code.status = code.status
        pairing_code.consumed_at = code.consumed_at
        return pairing_code


def consume_pairing_code(pairing_code_id: int, *, now=None, clock=None) -> PairingCode:
    if clock is not None and now is not None:
        raise ValueError("Pass either now or clock, not both")
    code = PairingCode.objects.get(pk=pairing_code_id)
    if code.status != PairingStatus.PENDING:
        raise ValueError("Pairing code is no longer pending")
    return transition_pairing_code(code, PairingStatus.CONSUMED, clock=clock, now=now)


@transaction.atomic
def record_webhook_event(*, provider: str, event_id: str, payload_sha256: str, signature_valid: bool):
    """Idempotently record webhook metadata; never store raw provider payloads."""
    from .statuses import WebhookStatus

    event, created = ProviderWebhookEvent.objects.get_or_create(
        provider=provider,
        event_id=event_id,
        defaults={
            "payload_sha256": payload_sha256,
            "signature_valid": signature_valid,
            "status": WebhookStatus.RECEIVED if signature_valid else WebhookStatus.REJECTED,
        },
    )
    if not created and event.payload_sha256 != payload_sha256:
        raise ValueError("Provider reused a webhook event ID with a different payload")
    return event, created


@transaction.atomic
def get_or_create_payment(*, partner_id: int, idempotency_key: str, defaults: dict):
    """Use the database uniqueness constraint as the final race-safe idempotency guard."""
    from .models import Agreement, Installment

    agreement_id = defaults.get("agreement_id") or getattr(defaults.get("agreement"), "pk", None)
    if not Agreement.objects.filter(pk=agreement_id, partner_id=partner_id).exists():
        raise ValueError("Payment agreement does not belong to this partner")
    installment_id = defaults.get("installment_id") or getattr(defaults.get("installment"), "pk", None)
    if installment_id and not Installment.objects.filter(
        pk=installment_id, partner_id=partner_id, agreement_id=agreement_id
    ).exists():
        raise ValueError("Payment installment does not belong to this agreement and partner")
    payment, created = Payment.objects.get_or_create(
        partner_id=partner_id,
        idempotency_key=idempotency_key,
        defaults=defaults,
    )
    for field in ("agreement_id", "installment_id", "amount_tzs"):
        expected = defaults.get(field)
        if expected is None and field.endswith("_id") and defaults.get(field.removesuffix("_id")) is not None:
            expected = getattr(defaults[field.removesuffix("_id")], "pk", None)
        if expected is not None and getattr(payment, field) != expected:
            raise ValueError("Idempotency key was already used for a different payment request")
    return payment, created
