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


class RootPageTests(TestCase):
    @override_settings(SERVER_MODE="demo", SECURE_HSTS_SECONDS=31536000)
    def test_root_get_is_a_safe_html_welcome_page_with_request_id(self):
        with self.assertLogs("orca.request", level="INFO") as captured:
            response = self.client.get("/", secure=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/html; charset=utf-8")
        body = response.content.decode()
        self.assertIn("ORCA Cloud", body)
        self.assertIn("demo", body)
        self.assertIn('href="/healthz"', body)
        self.assertIn('href="/readyz"', body)
        for forbidden in (
            "postgresql://",
            "localhost",
            "127.0.0.1",
            "DJANGO_SECRET_KEY",
            "Traceback",
            "Django 5.",
            "Python 3.",
            "@example.test",
        ):
            self.assertNotIn(forbidden, body)
        self.assertEqual(response["X-Content-Type-Options"], "nosniff")
        self.assertEqual(response["X-Frame-Options"], "DENY")
        self.assertIn("max-age=31536000", response["Strict-Transport-Security"])
        self.assertEqual(
            response["Cache-Control"],
            "max-age=0, no-cache, no-store, must-revalidate, private",
        )
        request_id = response["X-Request-ID"]
        self.assertRegex(request_id, r"^[0-9a-f]{32}$")
        formatted = SafeJsonFormatter().format(captured.records[0])
        self.assertIn(request_id, formatted)

    @override_settings(SERVER_MODE="live")
    def test_root_uses_configured_live_mode_without_extra_details(self):
        response = self.client.get("/")
        self.assertContains(response, "live")
        self.assertNotContains(response, "demo")

    def test_root_rejects_methods_other_than_get_and_head(self):
        self.assertEqual(self.client.post("/").status_code, 405)

    def test_root_head_is_200_html_without_a_body(self):
        response = self.client.head("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/html; charset=utf-8")
        self.assertEqual(response.content, b"")
        self.assertRegex(response["X-Request-ID"], r"^[0-9a-f]{32}$")

    def test_unknown_route_still_returns_generic_404_with_request_id_in_log(self):
        with self.assertLogs("orca.request", level="INFO") as captured:
            with self.assertLogs("django.request", level="WARNING") as django_warning:
                response = self.client.get("/not-a-real-route/")

        self.assertEqual(response.status_code, 404)
        self.assertRegex(response["X-Request-ID"], r"^[0-9a-f]{32}$")
        self.assertNotIn(b"Traceback", response.content)
        self.assertNotIn(b"settings.py", response.content)
        formatted_completion = SafeJsonFormatter().format(captured.records[0])
        formatted_warning = SafeJsonFormatter().format(django_warning.records[0])
        self.assertIn(response["X-Request-ID"], formatted_completion)
        self.assertIn(response["X-Request-ID"], formatted_warning)
        self.assertNotIn("/not-a-real-route/", formatted_warning)

    def test_healthz_remains_empty_204(self):
        response = self.client.get("/healthz")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content, b"")


class SafeLoggingTests(TestCase):
    def test_formatter_uses_request_id_attached_to_django_404_record(self):
        from types import SimpleNamespace

        record = logging.LogRecord(
            name="django.request",
            level=logging.WARNING,
            pathname=__file__,
            lineno=1,
            msg="Not Found: /private?phone=secret",
            args=(),
            exc_info=None,
        )
        record.request = SimpleNamespace(request_id="a" * 32)

        rendered = SafeJsonFormatter().format(record)

        self.assertIn('"request_id":"' + "a" * 32 + '"', rendered)
        self.assertIn("unstructured_log_suppressed", rendered)
        self.assertNotIn("private", rendered)
        self.assertNotIn("phone=secret", rendered)

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
