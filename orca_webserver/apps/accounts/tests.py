import logging
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
from django.db import OperationalError
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse

from apps.accounts.sms import ConsoleSMSBackend
from config.logging import SafeJsonFormatter

User = get_user_model()


class UserModelTests(TestCase):
    def test_customer_can_be_created_with_phone_and_no_password(self):
        user = User.objects.create_user(phone_number="+255700000001")
        self.assertEqual(user.role, "customer")
        self.assertFalse(user.has_usable_password())

    def test_staff_can_be_created_with_email_and_password(self):
        user = User.objects.create_user(email="STAFF@example.test", password="test-password")
        self.assertEqual(user.email, "staff@example.test")
        self.assertTrue(user.check_password("test-password"))

    def test_user_requires_email_or_phone(self):
        with self.assertRaisesMessage(ValueError, "email address or phone number"):
            User.objects.create_user()


class HealthEndpointTests(TestCase):
    def test_healthz_returns_empty_no_content_response_and_request_id(self):
        response = self.client.get(reverse("healthz"))
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content, b"")
        self.assertRegex(response["X-Request-ID"], r"^[0-9a-f]{32}$")

    def test_readyz_returns_empty_response_when_database_is_available(self):
        response = self.client.get(reverse("readyz"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"server_mode": "demo"})

    @patch(
        "config.health.connection.ensure_connection",
        side_effect=OperationalError("private db detail"),
    )
    def test_readyz_hides_database_error_details(self, _ensure_connection):
        response = self.client.get(reverse("readyz"))
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.content, b"")

    def test_health_endpoints_are_get_only(self):
        self.assertEqual(self.client.post(reverse("healthz")).status_code, 405)
        self.assertEqual(self.client.post(reverse("readyz")).status_code, 405)


class SafeLoggingTests(TestCase):
    def test_formatter_does_not_emit_arbitrary_message_or_url_fields(self):
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname=__file__,
            lineno=1,
            msg="sentinel-phone-token https://example.test/private?phone=secret",
            args=(),
            exc_info=None,
        )
        record.event = "untrusted-event sentinel-phone-token"
        record.method = "GET"
        record.status_code = 200

        rendered = SafeJsonFormatter().format(record)

        self.assertNotIn("sentinel-phone-token", rendered)
        self.assertNotIn("example.test", rendered)
        self.assertNotIn("phone=secret", rendered)
        self.assertIn("unstructured_log_suppressed", rendered)
        self.assertIn('"method":"GET"', rendered)


class DatabaseUrlTests(SimpleTestCase):
    def test_supabase_transaction_pooler_port_is_rejected(self):
        from config.settings.base import database_from_url

        with self.assertRaisesMessage(ImproperlyConfigured, "transaction pooler port 6543"):
            database_from_url("postgresql://user:secret@pooler.example.test:6543/orca")

    def test_production_database_url_requires_ssl(self):
        from config.settings.base import database_from_url

        with self.assertRaisesMessage(ImproperlyConfigured, "must require SSL"):
            database_from_url(
                "postgresql://user:secret@db.example.test:5432/orca?sslmode=disable",
                require_ssl=True,
            )


class ConsoleSmsTests(SimpleTestCase):
    @override_settings(DEBUG=True)
    def test_console_backend_masks_phone_and_is_explicitly_development_only(self):
        output = StringIO()
        with redirect_stdout(output):
            ConsoleSMSBackend().send("+255700123456", "Test code 123456")

        self.assertIn("***3456", output.getvalue())
        self.assertNotIn("+255700123456", output.getvalue())
        self.assertIn("Test code 123456", output.getvalue())

    @override_settings(DEBUG=False)
    def test_console_backend_refuses_to_send_when_debug_is_off(self):
        with self.assertRaisesMessage(ImproperlyConfigured, "only when DEBUG=True"):
            ConsoleSMSBackend().send("+255700123456", "Test code 123456")
