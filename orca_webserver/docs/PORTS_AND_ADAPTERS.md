# Ports and adapters

**Phase:** 2 foundation only. **No real provider adapter exists.** Everything described here runs
without a network connection; the fake adapters are not payment or messaging integrations.

## Selection and safety

Select adapters with `PAYMENTS_PROVIDER`, `STORAGE_BACKEND`, `SMS_BACKEND`, and
`DEVICE_TRANSPORT`. Current allowed values are `fake_clickpesa`, `local`, `console`/`recording`, and
`database`. Unknown values raise `ImproperlyConfigured` during Django settings import. Do not add a
provider name until its adapter and conformance tests exist.

The selected fake/local/console adapters set `SERVER_MODE=demo`. Production settings refuse to start
with a demo/local adapter unless `ALLOW_DEMO_BACKENDS=true` is explicitly set. That escape hatch is
for an owner-designated demo/staging service only; never set it for a service presented as live.
`/readyz` returns `{"server_mode":"demo"}` after its database check. `/healthz` remains empty and
data-free. Phase 2 adds no client status API; Phase 3 must return this same server-derived mode to
clients so they never guess from local configuration.

## PaymentProvider

Contract: `apps/ports/payment.py`. `FakeClickPesa` is in `apps/adapters/payments.py`; it has no
HTTP client, credentials, or network path. It previews integer TZS fees, initiates a deterministic
collection, queries its local status map, verifies HMAC test webhooks, and parses normalized fields.
Queue `success`, `failure`, `timeout`, or `duplicate` outcomes for collections. Call
`create_webhook(outcome=...)` for `success`, `failure`, `forged`, `out_of_order`, and
`amount_mismatch` webhook fixtures. Do not interpret this fake signature or result as ClickPesa
compatibility evidence.

Reusable contract tests live in `apps/domain/tests.py` (`PaymentProviderContract`). A future adapter
must run the same contract plus provider-specific sandbox/contract tests. A real ClickPesa adapter
is explicitly out of Phase 2.

## StorageBackend

Contract: `apps/ports/storage.py`. `LocalFileStorageBackend` uses Django's `STORAGES` default and
`MEDIA_ROOT`; it is development/test only. `InMemoryStorageBackend` is an in-memory test double.
Both implement put/delete/exists/public URL/expiring signed URL and reject path traversal. The local
signed URL is a signed development token only; Phase 2 has no private-file HTTP serving route.

The conformance tests are the `StorageContract` in `apps/domain/tests.py`; both adapters run it. Plan
an S3-compatible adapter through `django-storages` for Cloudflare R2, Supabase Storage, or AWS S3.
Do not install `django-storages`, configure a bucket, or enable a remote adapter in this phase. A real
adapter must pass this same storage contract and tests for privacy, expiry, overwrite, deletion and
network failure before use.

## SmsBackend

Contract: `apps/ports/sms.py`; implementations are `ConsoleSMSBackend` and `RecordingSMSBackend` in
`apps/accounts/sms.py`. Console output masks the destination and refuses to send unless `DEBUG=True`.
Recording keeps messages in process memory and never sends or logs them. Existing tests and new
adapter contract tests cover both. Do not generate OTPs or select a vendor in Phase 2.

## DeviceTransport

Contract: `apps/ports/device.py`; `DatabaseQueueDeviceTransport` queues and delivers database
`DeviceCommand` rows using polling semantics. A future authenticated HTTPS poll endpoint belongs to
Phase 3. No MQTT client, broker, socket, or mobile/TV copy is included. Use
`apps/domain/services.py` state transitions and a fake clock in tests.

The reusable transport contract should assert that queueing is idempotent at the domain layer,
delivery orders by availability/creation, and delivered commands are not returned twice unless an
explicit retry transition requeues them. Future real transports must run that contract before use.

## Clock

Contract: `apps/ports/clock.py`; `SystemClock` and mutable `FrozenClock` are in
`apps/adapters/clock.py`. Pass a clock into expiry/due/queue services. Avoid direct wall-clock calls
inside transitions so expiry and grace-period boundary tests use fixed instants.

## Adding an adapter later

1. Add an adapter that implements the matching `apps/ports/` Protocol.
2. Add an explicit setting value and factory branch; keep unknown values fail-closed.
3. Add the same conformance test suite without weakening its assertions.
4. Add adapter-specific timeout, retry, idempotency, signature and failure tests.
5. Add redacted operational logging and document all data sent to the provider.
6. Keep credentials in secret environment variables, never source or logs.
7. Demonstrate offline tests first. Obtain separate owner authorization before enabling a live
   provider or touching a live account.
