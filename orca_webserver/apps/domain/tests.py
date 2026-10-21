import hashlib
import io
import tempfile
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta, timezone
from threading import Barrier
try:
    import pytest
except ImportError:  # Django's test runner can run the suite without optional pytest tooling.
    pytest = None
from django.contrib.auth import get_user_model
from django.core.exceptions import SuspiciousFileOperation, ValidationError
from django.core.files.storage import FileSystemStorage
from django.db import DatabaseError, close_old_connections, connection, transaction
from django.test import SimpleTestCase, TestCase, TransactionTestCase, override_settings, tag
from PIL import Image

from apps.accounts.sms import ConsoleSMSBackend, RecordingSMSBackend
from apps.adapters.clock import FrozenClock, SystemClock
from apps.adapters.device import DatabaseQueueDeviceTransport
from apps.adapters.payments import FakeClickPesa
from apps.adapters.storage import InMemoryStorageBackend, LocalFileStorageBackend
from apps.domain.images import ImageAssetValidationError, validate_and_process_image
from apps.domain.models import (
    Agreement,
    AuditEvent,
    Customer,
    Device,
    DeviceCommand,
    Installment,
    PairingCode,
    Partner,
    Payment,
    ProviderWebhookEvent,
    Product,
)
from apps.domain.services import (
    COMMAND_TRANSITIONS,
    PAIRING_TRANSITIONS,
    PAYMENT_TRANSITIONS,
    consume_pairing_code,
    get_or_create_payment,
    record_webhook_event,
    transition_command,
    transition_pairing_code,
    transition_payment,
)
from apps.domain.statuses import CommandStatus, ImageStatus, PairingStatus, PaymentStatus

User = get_user_model()


def requires_postgres(test_class):
    if pytest is not None:
        return pytest.mark.requires_postgres(test_class)
    return test_class


class PaymentProviderContract:
    def run_contract(self, provider):
        fee = provider.preview_fees(1000)
        self.assertEqual(fee.amount_tzs, 1000)
        first = provider.initiate_collection(
            idempotency_key="contract-1", amount_tzs=1000, phone_number="+255700000001"
        )
        repeated = provider.initiate_collection(
            idempotency_key="contract-1", amount_tzs=1000, phone_number="+255700000001"
        )
        self.assertEqual(first, repeated)
        self.assertEqual(provider.query_status(first.provider_reference), first.status)
        body, signature = provider.create_webhook(provider_reference=first.provider_reference)
        self.assertTrue(provider.verify_webhook(body, signature))
        self.assertEqual(provider.parse_webhook(body).provider_reference, first.provider_reference)


class FakeClickPesaContractTests(PaymentProviderContract, SimpleTestCase):
    def test_fake_payment_provider_conforms_to_port(self):
        self.run_contract(FakeClickPesa(fee_bps=250))

    def test_scripted_success_failure_timeout_and_duplicate(self):
        provider = FakeClickPesa(outcomes=("success", "failure", "timeout", "duplicate"))
        self.assertEqual(provider.initiate_collection(idempotency_key="a", amount_tzs=1, phone_number="x").status, "succeeded")
        self.assertEqual(provider.initiate_collection(idempotency_key="b", amount_tzs=1, phone_number="x").status, "failed")
        with self.assertRaises(TimeoutError):
            provider.initiate_collection(idempotency_key="c", amount_tzs=1, phone_number="x")
        self.assertEqual(provider.initiate_collection(idempotency_key="d", amount_tzs=1, phone_number="x").status, "duplicate")

    def test_scripted_webhook_outcomes_are_deterministic_and_forgery_is_detected(self):
        provider = FakeClickPesa()
        for outcome in ("success", "failure", "out_of_order", "amount_mismatch"):
            body, signature = provider.create_webhook(outcome=outcome)
            self.assertTrue(provider.verify_webhook(body, signature))
            self.assertIsInstance(provider.parse_webhook(body).sequence, int)
        body, signature = provider.create_webhook(outcome="forged")
        self.assertFalse(provider.verify_webhook(body, signature))

    def test_fee_and_input_validation(self):
        provider = FakeClickPesa(fee_bps=101)
        self.assertEqual(provider.preview_fees(100).fee_tzs, 2)
        with self.assertRaises(ValueError):
            provider.preview_fees(0)


class StorageContract:
    def run_contract(self, backend):
        key = backend.put("appliances/p1/image1/large.webp", b"image-data", "image/webp")
        self.assertEqual(key, "appliances/p1/image1/large.webp")
        self.assertTrue(backend.exists(key))
        self.assertTrue(backend.url(key))
        signed = backend.signed_url(key, expires_in=60)
        self.assertTrue(signed)
        self.assertEqual(backend.verify_signed_url(signed), key)
        backend.delete(key)
        self.assertFalse(backend.exists(key))


class StorageContractTests(StorageContract, SimpleTestCase):
    def test_memory_adapter_conforms_to_port(self):
        self.run_contract(InMemoryStorageBackend())

    def test_local_file_adapter_conforms_to_port(self):
        with tempfile.TemporaryDirectory() as directory:
            storage = FileSystemStorage(location=directory, base_url="/media/")
            backend = LocalFileStorageBackend(storage=storage)
            self.run_contract(backend)
            signed = backend.signed_url("private/key.webp", expires_in=60)
            self.assertEqual(backend.verify_signed_url(signed), "private/key.webp")

    def test_storage_rejects_traversal_and_invalid_expiry(self):
        backend = InMemoryStorageBackend()
        with self.assertRaises(SuspiciousFileOperation):
            backend.put("../secret", b"x", "image/png")
        with self.assertRaises(ValueError):
            backend.signed_url("missing", expires_in=0)


class SmsBackendContract:
    def run_contract(self, backend, observe, *, phone="+255700000001", message="verification code"):
        backend.send(phone, message)
        self.assertEqual(observe(), (phone, message))


class SmsAdapterContractTests(SmsBackendContract, SimpleTestCase):
    def test_recording_adapter_records_without_network(self):
        backend = RecordingSMSBackend()
        self.run_contract(backend, lambda: (backend.records[0].phone_number, backend.records[0].message))

    @override_settings(DEBUG=True)
    def test_console_adapter_emits_masked_destination(self):
        from contextlib import redirect_stdout
        from io import StringIO

        output = StringIO()
        with redirect_stdout(output):
            self.run_contract(
                ConsoleSMSBackend(),
                lambda: ("+255700123456", "test") if "[DEV SMS to ***3456] test" in output.getvalue() else ("", ""),
                phone="+255700123456",
                message="test",
            )
        self.assertIn("***3456", output.getvalue())
        self.assertNotIn("+255700123456", output.getvalue())


class ClockAdapterTests(SimpleTestCase):
    def test_system_and_frozen_clock_contract(self):
        self.assertIsNotNone(SystemClock().now().tzinfo)
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        clock = FrozenClock(start)
        self.assertEqual(clock.now(), start)
        self.assertEqual(clock.advance(seconds=5), start + timedelta(seconds=5))

    def test_clock_adapters_return_aware_time(self):
        self.assertIsNotNone(SystemClock().now().tzinfo)
        self.assertEqual(FrozenClock(datetime(2026, 1, 1, tzinfo=timezone.utc)).now().utcoffset(), timedelta(0))


class ImageValidationTests(SimpleTestCase):
    @staticmethod
    def png_bytes(size=(640, 480)):
        image = Image.new("RGB", size, "navy")
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return buffer.getvalue()

    def test_detects_bytes_and_emits_three_metadata_free_webp_variants(self):
        result = validate_and_process_image(self.png_bytes())
        self.assertEqual(result.original_content_type, "image/png")
        self.assertEqual((result.original_width, result.original_height), (640, 480))
        self.assertEqual(set(result.variants), {"thumbnail", "medium", "large"})
        for content in result.variants.values():
            with Image.open(io.BytesIO(content)) as image:
                self.assertEqual(image.format, "WEBP")
                self.assertFalse(image.getexif())

    def test_strips_input_exif_metadata(self):
        source = Image.new("RGB", (64, 64), "green")
        exif = Image.Exif()
        exif[270] = "PRIVATE LOCATION METADATA"
        buffer = io.BytesIO()
        source.save(buffer, format="JPEG", exif=exif)
        result = validate_and_process_image(buffer.getvalue())
        self.assertEqual(result.original_content_type, "image/jpeg")
        for content in result.variants.values():
            with Image.open(io.BytesIO(content)) as image:
                self.assertFalse(image.getexif())
            self.assertNotIn(b"PRIVATE LOCATION METADATA", content)

    def test_rejects_non_image_and_configured_size_limit(self):
        with self.assertRaises(ImageAssetValidationError):
            validate_and_process_image(b"not an image")
        with override_settings(IMAGE_MAX_BYTES=4):
            with self.assertRaises(ImageAssetValidationError):
                validate_and_process_image(self.png_bytes())
        with override_settings(IMAGE_MAX_DIMENSION=100):
            with self.assertRaises(ImageAssetValidationError):
                validate_and_process_image(self.png_bytes())


class DomainFixtureMixin:
    def create_domain_graph(self):
        self.partner = Partner.objects.create(name="Demo Partner", slug="demo-partner")
        self.customer = Customer.objects.create(
            partner=self.partner, full_name="Test Customer", phone_number="+255700000001"
        )
        self.product = Product.objects.create(partner=self.partner, sku="TV-001", name="TV", price_tzs=500000)
        self.agreement = Agreement.objects.create(
            partner=self.partner,
            customer=self.customer,
            product=self.product,
            total_tzs=500000,
            starts_on=date(2026, 1, 1),
        )
        self.installment = Installment.objects.create(
            partner=self.partner,
            agreement=self.agreement,
            sequence=1,
            due_date=date(2026, 2, 1),
            amount_tzs=50000,
        )
        self.device = Device.objects.create(partner=self.partner, agreement=self.agreement)
        self.user = User.objects.create_user(email="uploader@example.test", password="unit-test-password")


class DeviceTransportContract:
    def run_contract(self, transport, device, partner, now):
        command = DeviceCommand.objects.create(
            partner=partner,
            device=device,
            command_type="contract.ping",
            payload={"ping": True},
            idempotency_key="contract-device-transport",
            available_at=now,
        )
        transport.queue(command.pk)
        delivered = transport.deliver(device.pk)
        self.assertEqual([item["id"] for item in delivered], [command.pk])
        self.assertEqual(transport.deliver(device.pk), [])


class DomainModelTests(DomainFixtureMixin, DeviceTransportContract, TestCase):
    def setUp(self):
        self.create_domain_graph()

    def test_all_domain_records_are_created_and_tzs_are_integer(self):
        payment = Payment.objects.create(
            partner=self.partner,
            agreement=self.agreement,
            installment=self.installment,
            amount_tzs=50000,
            idempotency_key="pay-1",
        )
        self.assertIsInstance(payment.amount_tzs, int)
        self.assertEqual(self.product.images.count(), 0)

    def test_database_constraints_reject_duplicate_business_keys_and_invalid_money(self):
        from django.db import IntegrityError, transaction

        with self.assertRaises(IntegrityError), transaction.atomic():
            Product.objects.create(partner=self.partner, sku="TV-001", name="Other", price_tzs=1)
        with self.assertRaises(IntegrityError), transaction.atomic():
            Product.objects.create(partner=self.partner, sku="TV-002", name="Free", price_tzs=0)

    def test_model_validation_rejects_cross_partner_relationships_on_sqlite(self):
        other_partner = Partner.objects.create(name="Other Partner", slug="other-partner-clean")
        other_customer = Customer.objects.create(partner=other_partner, full_name="Other Customer")
        agreement = Agreement(
            partner=self.partner,
            customer=other_customer,
            product=self.product,
            total_tzs=1000,
        )
        with self.assertRaises(ValidationError):
            agreement.full_clean()

    def test_audit_events_are_append_only_and_admin_safe(self):
        event = AuditEvent.objects.create(
            partner=self.partner, actor=self.user, action="test.created", entity_type="Product", entity_id="1"
        )
        with self.assertRaises(TypeError):
            event.action = "changed"
            event.save()
        with self.assertRaises(TypeError):
            AuditEvent.objects.filter(pk=event.pk).update(action="changed")
        with self.assertRaises(TypeError):
            event.delete()
        with self.assertRaises(DatabaseError), transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("UPDATE domain_auditevent SET action=%s WHERE id=%s", ["changed", event.pk])
        with self.assertRaises(DatabaseError), transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM domain_auditevent WHERE id=%s", [event.pk])
        self.assertTrue(AuditEvent.objects.filter(pk=event.pk).exists())

    def test_primary_image_is_unique_per_product(self):
        from django.db import IntegrityError, transaction

        common = dict(
            partner=self.partner,
            product=self.product,
            content_type="image/webp",
            byte_size=10,
            width=10,
            height=10,
            sha256="a" * 64,
            alt_text="TV",
            is_primary=True,
            status=ImageStatus.READY,
            uploaded_by=self.user,
        )
        from apps.domain.models import ImageAsset

        ImageAsset.objects.create(storage_key="a.webp", **common)
        with self.assertRaises(IntegrityError), transaction.atomic():
            ImageAsset.objects.create(storage_key="b.webp", **common)

    def test_pairing_code_expiry_and_single_use_state(self):
        now = datetime(2026, 1, 1, tzinfo=timezone.utc)
        expired = PairingCode.objects.create(
            partner=self.partner,
            device=self.device,
            code_hash="hash-expired",
            expires_at=now - timedelta(seconds=1),
        )
        self.assertEqual(consume_pairing_code(expired.pk, now=now).status, PairingStatus.EXPIRED)
        live = PairingCode.objects.create(
            partner=self.partner,
            device=self.device,
            code_hash="hash-live",
            expires_at=now + timedelta(minutes=1),
        )
        consumed = consume_pairing_code(live.pk, now=now)
        self.assertEqual(consumed.status, PairingStatus.CONSUMED)
        with self.assertRaisesMessage(ValueError, "no longer pending"):
            consume_pairing_code(live.pk, now=now)

    def test_database_transport_delivers_queued_commands_and_counts_delivery(self):
        now = datetime(2026, 1, 1, tzinfo=timezone.utc)
        command = DeviceCommand.objects.create(
            partner=self.partner,
            device=self.device,
            command_type="status.poll",
            payload={"request": "status"},
            idempotency_key="command-1",
            available_at=now,
        )
        transport = DatabaseQueueDeviceTransport(clock=FrozenClock(now))
        transport.queue(command.pk)
        result = transport.deliver(self.device.pk)
        self.assertEqual(result[0]["type"], "status.poll")
        command.refresh_from_db()
        self.assertEqual(command.status, CommandStatus.DELIVERED)
        self.assertEqual(command.delivery_count, 1)

    def test_database_device_transport_conforms_to_reusable_contract(self):
        now = datetime(2026, 1, 1, tzinfo=timezone.utc)
        self.run_contract(DatabaseQueueDeviceTransport(clock=FrozenClock(now)), self.device, self.partner, now)

    def test_payment_command_and_pairing_services_cover_legal_and_illegal_transitions(self):
        for current, legal_targets in PAYMENT_TRANSITIONS.items():
            for index, target in enumerate(legal_targets):
                payment = Payment.objects.create(
                    partner=self.partner,
                    agreement=self.agreement,
                    amount_tzs=1000,
                    idempotency_key=f"payment-{current}-{index}",
                    status=current,
                )
                transition_payment(payment, target)
                payment.refresh_from_db()
                self.assertEqual(payment.status, target)
            invalid_target = next((status for status in PaymentStatus.values if status not in legal_targets), None)
            if invalid_target:
                payment = Payment.objects.create(
                    partner=self.partner,
                    agreement=self.agreement,
                    amount_tzs=1000,
                    idempotency_key=f"payment-illegal-{current}",
                    status=current,
                )
                with self.assertRaises(ValueError):
                    transition_payment(payment, invalid_target)

        now = datetime(2026, 1, 1, tzinfo=timezone.utc)
        for current, legal_targets in COMMAND_TRANSITIONS.items():
            for index, target in enumerate(legal_targets):
                command = DeviceCommand.objects.create(
                    partner=self.partner,
                    device=self.device,
                    command_type="matrix.test",
                    idempotency_key=f"command-{current}-{index}",
                    available_at=now,
                    status=current,
                    delivered_at=now if current in {CommandStatus.DELIVERED, CommandStatus.ACKNOWLEDGED} else None,
                    acknowledged_at=now if current == CommandStatus.ACKNOWLEDGED else None,
                )
                transition_command(command, target)
                command.refresh_from_db()
                self.assertEqual(command.status, target)
            invalid_target = next((status for status in CommandStatus.values if status not in legal_targets), None)
            if invalid_target:
                command = DeviceCommand.objects.create(
                    partner=self.partner,
                    device=self.device,
                    command_type="matrix.illegal",
                    idempotency_key=f"command-illegal-{current}",
                    available_at=now,
                    status=current,
                    delivered_at=now if current in {CommandStatus.DELIVERED, CommandStatus.ACKNOWLEDGED} else None,
                    acknowledged_at=now if current == CommandStatus.ACKNOWLEDGED else None,
                )
                with self.assertRaises(ValueError):
                    transition_command(command, invalid_target)

        for current, legal_targets in PAIRING_TRANSITIONS.items():
            for index, target in enumerate(legal_targets):
                expiry = now - timedelta(seconds=1) if target == PairingStatus.EXPIRED else now + timedelta(minutes=5)
                code = PairingCode.objects.create(
                    partner=self.partner,
                    device=self.device,
                    code_hash=f"pair-{current}-{index}",
                    expires_at=expiry,
                    status=current,
                    consumed_at=now if current == PairingStatus.CONSUMED else None,
                )
                transition_pairing_code(code, target, clock=FrozenClock(now))
                code.refresh_from_db()
                self.assertEqual(code.status, target)
            invalid_target = next((status for status in PairingStatus.values if status not in legal_targets), None)
            if invalid_target:
                code = PairingCode.objects.create(
                    partner=self.partner,
                    device=self.device,
                    code_hash=f"pair-illegal-{current}",
                    expires_at=now + timedelta(minutes=5),
                    status=current,
                    consumed_at=now if current == PairingStatus.CONSUMED else None,
                )
                with self.assertRaises(ValueError):
                    transition_pairing_code(code, invalid_target, clock=FrozenClock(now))


class StateTransitionTests(SimpleTestCase):
    def test_every_state_has_an_explicit_transition_set(self):
        self.assertEqual(set(PAYMENT_TRANSITIONS), set(PaymentStatus.values))
        self.assertEqual(set(COMMAND_TRANSITIONS), set(CommandStatus.values))
        self.assertEqual(set(PAIRING_TRANSITIONS), set(PairingStatus.values))
        self.assertTrue(all(isinstance(allowed, set) for allowed in PAYMENT_TRANSITIONS.values()))


@requires_postgres
@tag("requires_postgres")
class PostgreSQLConcurrencyTests(DomainFixtureMixin, TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        if connection.vendor != "postgresql":
            self.skipTest("requires_postgres: run with the PostgreSQL service database to verify row locks/races")
        self.create_domain_graph()

    def _race(self, callback):
        barrier = Barrier(2)

        def worker():
            close_old_connections()
            try:
                barrier.wait(timeout=10)
                return callback()
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as pool:
            return list(pool.map(lambda _index: worker(), range(2)))

    def test_idempotent_payment_creation_has_one_row_under_race(self):
        def create():
            payment, was_created = get_or_create_payment(
                partner_id=self.partner.pk,
                idempotency_key="race-key",
                defaults={"agreement_id": self.agreement.pk, "amount_tzs": 1000},
            )
            return payment.pk, was_created

        results = self._race(create)
        self.assertEqual(len({row_id for row_id, _created in results}), 1)
        self.assertEqual(sum(created for _row_id, created in results), 1)
        self.assertEqual(Payment.objects.filter(partner=self.partner, idempotency_key="race-key").count(), 1)

    def test_duplicate_webhook_delivery_records_one_event(self):
        digest = hashlib.sha256(b"fake event").hexdigest()
        results = self._race(
            lambda: record_webhook_event(
                provider="fake", event_id="same-event", payload_sha256=digest, signature_valid=True
            )[1]
        )
        self.assertEqual(sum(results), 1)
        self.assertEqual(ProviderWebhookEvent.objects.filter(provider="fake", event_id="same-event").count(), 1)

    def test_row_lock_allows_only_one_terminal_payment_transition(self):
        payment = Payment.objects.create(
            partner=self.partner, agreement=self.agreement, amount_tzs=1000, idempotency_key="row-lock"
        )

        def change(target):
            close_old_connections()
            try:
                barrier.wait(timeout=10)
                try:
                    transition_payment(Payment.objects.get(pk=payment.pk), target)
                    return "changed"
                except ValueError:
                    return "rejected"
            finally:
                close_old_connections()

        barrier = Barrier(2)
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(change, (PaymentStatus.FAILED, PaymentStatus.CANCELLED)))
        self.assertEqual(results.count("changed"), 1)
        self.assertEqual(results.count("rejected"), 1)
        payment.refresh_from_db()
        self.assertIn(payment.status, {PaymentStatus.FAILED, PaymentStatus.CANCELLED})

    def test_partner_scope_trigger_rejects_cross_partner_relationship(self):
        from django.db import IntegrityError, transaction

        other_partner = Partner.objects.create(name="Other Partner", slug="other-partner")
        other_customer = Customer.objects.create(partner=other_partner, full_name="Other Customer")
        with self.assertRaises(IntegrityError), transaction.atomic():
            Agreement.objects.create(
                partner=self.partner,
                customer=other_customer,
                product=self.product,
                total_tzs=1000,
            )
