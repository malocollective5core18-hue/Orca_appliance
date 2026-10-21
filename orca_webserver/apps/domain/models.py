"""Relational domain records. Monetary amounts are integer TZS, never floats."""

import uuid

from django.conf import settings
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.db.models import Q

from .statuses import (
    AgreementStatus,
    CommandStatus,
    DeviceStatus,
    ImageStatus,
    InstallmentStatus,
    NotificationStatus,
    PairingStatus,
    PaymentAttemptStatus,
    PaymentStatus,
    RecordStatus,
    WebhookStatus,
)


class Partner(models.Model):
    name = models.CharField(max_length=160)
    slug = models.SlugField(max_length=80, unique=True)
    status = models.CharField(max_length=16, choices=RecordStatus.choices, default=RecordStatus.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("name", "id")
        constraints = [models.CheckConstraint(condition=Q(status__in=RecordStatus.values), name="domain_partner_status_valid")]
        indexes = [models.Index(fields=("status", "name"), name="domain_partner_status_name_idx")]

    def __str__(self):
        return self.name


class Customer(models.Model):
    partner = models.ForeignKey(Partner, on_delete=models.PROTECT, related_name="customers")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="customer_profiles",
    )
    full_name = models.CharField(max_length=160)
    phone_number = models.CharField(max_length=32, blank=True)
    email = models.EmailField(blank=True)
    status = models.CharField(max_length=16, choices=RecordStatus.choices, default=RecordStatus.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("full_name", "id")
        constraints = [models.CheckConstraint(condition=Q(status__in=RecordStatus.values), name="domain_customer_status_valid")]
        indexes = [
            models.Index(fields=("partner", "status", "full_name"), name="domain_cust_partner_name_idx"),
            models.Index(fields=("partner", "phone_number"), name="domain_cust_partner_phone_idx"),
        ]

    def __str__(self):
        return self.full_name


class Product(models.Model):
    partner = models.ForeignKey(Partner, on_delete=models.PROTECT, related_name="products")
    sku = models.CharField(max_length=64)
    name = models.CharField(max_length=160)
    model_number = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    price_tzs = models.PositiveBigIntegerField(validators=[MinValueValidator(1)])
    status = models.CharField(max_length=16, choices=RecordStatus.choices, default=RecordStatus.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("name", "id")
        constraints = [
            models.UniqueConstraint(fields=("partner", "sku"), name="d_product_partner_sku_u"),
            models.CheckConstraint(condition=Q(price_tzs__gt=0), name="domain_product_price_positive"),
            models.CheckConstraint(condition=Q(status__in=RecordStatus.values), name="domain_product_status_valid"),
        ]
        indexes = [models.Index(fields=("partner", "status", "name"), name="domain_product_list_idx")]

    def __str__(self):
        return f"{self.sku} — {self.name}"


class Agreement(models.Model):
    partner = models.ForeignKey(Partner, on_delete=models.PROTECT, related_name="agreements")
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name="agreements")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="agreements")
    reference = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    status = models.CharField(max_length=16, choices=AgreementStatus.choices, default=AgreementStatus.DRAFT)
    total_tzs = models.PositiveBigIntegerField(validators=[MinValueValidator(1)])
    down_payment_tzs = models.PositiveBigIntegerField(default=0)
    starts_on = models.DateField(null=True, blank=True)
    ends_on = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at", "id")
        constraints = [
            models.CheckConstraint(condition=Q(status__in=AgreementStatus.values), name="domain_agreement_status_valid"),
            models.CheckConstraint(condition=Q(total_tzs__gt=0), name="d_agreement_total_positive"),
            models.CheckConstraint(condition=Q(down_payment_tzs__lte=models.F("total_tzs")), name="domain_agreement_down_le_total"),
            models.CheckConstraint(condition=Q(ends_on__isnull=True) | Q(starts_on__isnull=True) | Q(ends_on__gte=models.F("starts_on")), name="domain_agreement_dates_ordered"),
        ]
        indexes = [models.Index(fields=("partner", "status", "created_at"), name="domain_agreement_list_idx")]

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.customer_id and self.customer.partner_id != self.partner_id:
            raise ValidationError({"customer": "Customer must belong to the agreement partner."})
        if self.product_id and self.product.partner_id != self.partner_id:
            raise ValidationError({"product": "Product must belong to the agreement partner."})

    def __str__(self):
        return str(self.reference)


class Installment(models.Model):
    partner = models.ForeignKey(Partner, on_delete=models.PROTECT, related_name="installments")
    agreement = models.ForeignKey(Agreement, on_delete=models.PROTECT, related_name="installments")
    sequence = models.PositiveSmallIntegerField()
    due_date = models.DateField()
    amount_tzs = models.PositiveBigIntegerField(validators=[MinValueValidator(1)])
    paid_tzs = models.PositiveBigIntegerField(default=0)
    status = models.CharField(max_length=16, choices=InstallmentStatus.choices, default=InstallmentStatus.DUE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("due_date", "sequence")
        constraints = [
            models.CheckConstraint(condition=Q(status__in=InstallmentStatus.values), name="domain_inst_status_valid"),
            models.UniqueConstraint(fields=("agreement", "sequence"), name="d_inst_sequence_uniq"),
            models.CheckConstraint(condition=Q(sequence__gt=0), name="d_inst_sequence_positive"),
            models.CheckConstraint(condition=Q(amount_tzs__gt=0), name="d_inst_amount_positive"),
            models.CheckConstraint(condition=Q(paid_tzs__lte=models.F("amount_tzs")), name="d_inst_paid_le_amount"),
            models.CheckConstraint(
                condition=(
                    Q(status=InstallmentStatus.PAID, paid_tzs=models.F("amount_tzs"))
                    | Q(status=InstallmentStatus.PARTIAL, paid_tzs__gt=0, paid_tzs__lt=models.F("amount_tzs"))
                    | Q(status__in=(InstallmentStatus.DUE, InstallmentStatus.WAIVED), paid_tzs=0)
                ),
                name="d_inst_status_amount",
            ),
        ]
        indexes = [models.Index(fields=("status", "due_date"), name="domain_installment_due_idx")]

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.agreement_id and self.agreement.partner_id != self.partner_id:
            raise ValidationError({"agreement": "Installment and agreement must share a partner."})

    def __str__(self):
        return f"{self.agreement_id}:{self.sequence}"


class Device(models.Model):
    partner = models.ForeignKey(Partner, on_delete=models.PROTECT, related_name="devices")
    agreement = models.ForeignKey(Agreement, null=True, blank=True, on_delete=models.PROTECT, related_name="devices")
    device_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    serial_number = models.CharField(max_length=128, blank=True)
    status = models.CharField(max_length=20, choices=DeviceStatus.choices, default=DeviceStatus.PROVISIONING)
    last_seen_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at", "id")
        constraints = [
            models.CheckConstraint(condition=Q(status__in=DeviceStatus.values), name="domain_device_status_valid"),
            models.UniqueConstraint(fields=("partner", "serial_number"), condition=~Q(serial_number=""), name="domain_device_serial_uniq"),
        ]
        indexes = [models.Index(fields=("partner", "status", "last_seen_at"), name="domain_device_status_seen_idx")]

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.agreement_id and self.agreement.partner_id != self.partner_id:
            raise ValidationError({"agreement": "Device and agreement must share a partner."})

    def __str__(self):
        return str(self.device_id)


class PairingCode(models.Model):
    partner = models.ForeignKey(Partner, on_delete=models.PROTECT, related_name="pairing_codes")
    device = models.ForeignKey(Device, on_delete=models.PROTECT, related_name="pairing_codes")
    code_hash = models.CharField(max_length=128, unique=True)
    status = models.CharField(max_length=16, choices=PairingStatus.choices, default=PairingStatus.PENDING)
    expires_at = models.DateTimeField()
    consumed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at", "id")
        constraints = [
            models.CheckConstraint(condition=Q(status__in=PairingStatus.values), name="domain_pairing_status_valid"),
            models.CheckConstraint(condition=(Q(status=PairingStatus.CONSUMED, consumed_at__isnull=False) | (~Q(status=PairingStatus.CONSUMED) & Q(consumed_at__isnull=True))), name="d_pair_consumed_time"),
        ]
        indexes = [models.Index(fields=("device", "status", "expires_at"), name="domain_pairing_lookup_idx")]

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.device_id and self.device.partner_id != self.partner_id:
            raise ValidationError({"device": "Pairing code and device must share a partner."})

    def __str__(self):
        return f"Pairing {self.pk} ({self.status})"


class Payment(models.Model):
    partner = models.ForeignKey(Partner, on_delete=models.PROTECT, related_name="payments")
    agreement = models.ForeignKey(Agreement, on_delete=models.PROTECT, related_name="payments")
    installment = models.ForeignKey(Installment, null=True, blank=True, on_delete=models.PROTECT, related_name="payments")
    amount_tzs = models.PositiveBigIntegerField(validators=[MinValueValidator(1)])
    status = models.CharField(max_length=16, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    provider_reference = models.CharField(max_length=128, null=True, blank=True, unique=True)
    idempotency_key = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at", "id")
        constraints = [
            models.CheckConstraint(condition=Q(status__in=PaymentStatus.values), name="domain_payment_status_valid"),
            models.UniqueConstraint(fields=("partner", "idempotency_key"), name="d_payment_idem_uniq"),
            models.CheckConstraint(condition=Q(amount_tzs__gt=0), name="domain_payment_amount_positive"),
        ]
        indexes = [models.Index(fields=("partner", "status", "created_at"), name="domain_payment_list_idx")]

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.agreement_id and self.agreement.partner_id != self.partner_id:
            raise ValidationError({"agreement": "Payment and agreement must share a partner."})
        if self.installment_id and (
            self.installment.partner_id != self.partner_id
            or self.installment.agreement_id != self.agreement_id
        ):
            raise ValidationError({"installment": "Payment installment must belong to this agreement and partner."})

    def __str__(self):
        return f"Payment {self.pk} ({self.status})"


class PaymentAttempt(models.Model):
    partner = models.ForeignKey(Partner, on_delete=models.PROTECT, related_name="payment_attempts")
    payment = models.ForeignKey(Payment, on_delete=models.PROTECT, related_name="attempts")
    attempt_number = models.PositiveSmallIntegerField()
    status = models.CharField(max_length=16, choices=PaymentAttemptStatus.choices, default=PaymentAttemptStatus.STARTED)
    outcome_code = models.CharField(max_length=64, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("attempt_number",)
        constraints = [
            models.CheckConstraint(condition=Q(status__in=PaymentAttemptStatus.values), name="domain_attempt_status_valid"),
            models.UniqueConstraint(fields=("payment", "attempt_number"), name="domain_pay_attempt_number_uniq"),
            models.CheckConstraint(condition=Q(attempt_number__gt=0), name="domain_pay_attempt_positive"),
            models.CheckConstraint(
                condition=(Q(status=PaymentAttemptStatus.STARTED, finished_at__isnull=True) | (~Q(status=PaymentAttemptStatus.STARTED) & Q(finished_at__isnull=False))),
                name="d_attempt_finish_consistent",
            ),
        ]
        indexes = [models.Index(fields=("status", "started_at"), name="domain_pay_attempt_status_idx")]

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.payment_id and self.payment.partner_id != self.partner_id:
            raise ValidationError({"payment": "Payment attempt and payment must share a partner."})


class ProviderWebhookEvent(models.Model):
    provider = models.CharField(max_length=48)
    event_id = models.CharField(max_length=128)
    payload_sha256 = models.CharField(max_length=64, validators=[RegexValidator(r"^[0-9a-f]{64}$")])
    status = models.CharField(max_length=16, choices=WebhookStatus.choices, default=WebhookStatus.RECEIVED)
    signature_valid = models.BooleanField(null=True, blank=True, default=None)
    received_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-received_at", "id")
        constraints = [
            models.CheckConstraint(condition=Q(status__in=WebhookStatus.values), name="domain_webhook_status_valid"),
            models.UniqueConstraint(fields=("provider", "event_id"), name="domain_webhook_event_uniq"),
            models.CheckConstraint(
                condition=(Q(status=WebhookStatus.PROCESSED, processed_at__isnull=False, signature_valid=True) | Q(status=WebhookStatus.RECEIVED, processed_at__isnull=True) | Q(status=WebhookStatus.REJECTED, processed_at__isnull=True, signature_valid=False)),
                name="d_webhook_state_consistent",
            ),
        ]
        indexes = [models.Index(fields=("status", "received_at"), name="domain_webhook_status_idx")]


class DeviceCommand(models.Model):
    partner = models.ForeignKey(Partner, on_delete=models.PROTECT, related_name="device_commands")
    device = models.ForeignKey(Device, on_delete=models.PROTECT, related_name="commands")
    command_type = models.CharField(max_length=64)
    payload = models.JSONField(default=dict)
    idempotency_key = models.CharField(max_length=128)
    status = models.CharField(max_length=16, choices=CommandStatus.choices, default=CommandStatus.PENDING)
    available_at = models.DateTimeField()
    delivered_at = models.DateTimeField(null=True, blank=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    delivery_count = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("available_at", "created_at", "id")
        constraints = [
            models.CheckConstraint(condition=Q(status__in=CommandStatus.values), name="domain_command_status_valid"),
            models.UniqueConstraint(fields=("device", "idempotency_key"), name="d_command_idem_uniq"),
            models.CheckConstraint(condition=Q(delivery_count__gte=0), name="d_command_count_nonnegative"),
            models.CheckConstraint(condition=(~Q(status__in=(CommandStatus.DELIVERED, CommandStatus.ACKNOWLEDGED)) | Q(delivered_at__isnull=False)), name="d_command_delivery_time"),
            models.CheckConstraint(condition=(~Q(status=CommandStatus.ACKNOWLEDGED) | Q(acknowledged_at__isnull=False)), name="domain_command_ack_time_check"),
        ]
        indexes = [models.Index(fields=("device", "status", "available_at"), name="domain_command_queue_idx")]

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.device_id and self.device.partner_id != self.partner_id:
            raise ValidationError({"device": "Command and device must share a partner."})


class DeviceStatusHistory(models.Model):
    partner = models.ForeignKey(Partner, on_delete=models.PROTECT, related_name="device_status_history")
    device = models.ForeignKey(Device, on_delete=models.PROTECT, related_name="status_history")
    status = models.CharField(max_length=20, choices=DeviceStatus.choices)
    observed_at = models.DateTimeField()
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-observed_at", "-id")
        constraints = [models.CheckConstraint(condition=Q(status__in=DeviceStatus.values), name="domain_history_status_valid")]
        indexes = [models.Index(fields=("device", "-observed_at"), name="domain_device_history_idx")]

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.device_id and self.device.partner_id != self.partner_id:
            raise ValidationError({"device": "Status history and device must share a partner."})


class Notification(models.Model):
    partner = models.ForeignKey(Partner, on_delete=models.PROTECT, related_name="notifications")
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name="notifications")
    channel = models.CharField(max_length=16, choices=(("sms", "SMS"), ("email", "Email"), ("in_app", "In app")))
    template_key = models.CharField(max_length=80)
    status = models.CharField(max_length=16, choices=NotificationStatus.choices, default=NotificationStatus.PENDING)
    provider_reference = models.CharField(max_length=128, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at", "id")
        constraints = [
            models.CheckConstraint(condition=Q(status__in=NotificationStatus.values), name="domain_notify_status_valid"),
            models.CheckConstraint(condition=Q(channel__in=("sms", "email", "in_app")), name="domain_notify_channel_valid"),
            models.CheckConstraint(
                condition=(Q(status=NotificationStatus.SENT, sent_at__isnull=False) | (~Q(status=NotificationStatus.SENT) & Q(sent_at__isnull=True))),
                name="d_notify_sent_time",
            ),
        ]
        indexes = [models.Index(fields=("partner", "status", "created_at"), name="domain_notify_status_idx")]

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.customer_id and self.customer.partner_id != self.partner_id:
            raise ValidationError({"customer": "Notification and customer must share a partner."})


class IdempotencyRecord(models.Model):
    partner = models.ForeignKey(Partner, on_delete=models.PROTECT, related_name="idempotency_records")
    scope = models.CharField(max_length=80)
    key = models.CharField(max_length=128)
    request_sha256 = models.CharField(max_length=64, validators=[RegexValidator(r"^[0-9a-f]{64}$")])
    resource_type = models.CharField(max_length=64, blank=True)
    resource_id = models.CharField(max_length=64, blank=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=("partner", "scope", "key"), name="d_idem_scope_key_uniq")]
        indexes = [models.Index(fields=("expires_at",), name="domain_idempotency_expiry_idx")]


class AuditEventQuerySet(models.QuerySet):
    def update(self, **kwargs):
        raise TypeError("Audit events are append-only")

    def delete(self):
        raise TypeError("Audit events are append-only")


class AuditEvent(models.Model):
    partner = models.ForeignKey(Partner, null=True, blank=True, on_delete=models.PROTECT, related_name="audit_events")
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT, related_name="audit_events")
    action = models.CharField(max_length=100)
    entity_type = models.CharField(max_length=80)
    entity_id = models.CharField(max_length=64, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = AuditEventQuerySet.as_manager()

    class Meta:
        ordering = ("-created_at", "-id")
        indexes = [
            models.Index(fields=("partner", "-created_at"), name="domain_audit_partner_time_idx"),
            models.Index(fields=("entity_type", "entity_id"), name="domain_audit_entity_idx"),
        ]

    def save(self, *args, **kwargs):
        if self.pk and type(self).objects.filter(pk=self.pk).exists():
            raise TypeError("Audit events are append-only")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise TypeError("Audit events are append-only")


class ImageAsset(models.Model):
    partner = models.ForeignKey(Partner, on_delete=models.PROTECT, related_name="image_assets")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="images")
    storage_key = models.CharField(max_length=512, unique=True)
    content_type = models.CharField(max_length=32, choices=(("image/jpeg", "JPEG"), ("image/png", "PNG"), ("image/webp", "WebP")))
    byte_size = models.PositiveBigIntegerField()
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()
    sha256 = models.CharField(max_length=64, validators=[RegexValidator(r"^[0-9a-f]{64}$")])
    alt_text = models.CharField(max_length=250)
    is_primary = models.BooleanField(default=False)
    sort_order = models.PositiveSmallIntegerField(default=0)
    status = models.CharField(max_length=16, choices=ImageStatus.choices, default=ImageStatus.UPLOADED)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="uploaded_appliance_images")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("sort_order", "created_at", "id")
        constraints = [
            models.CheckConstraint(condition=Q(status__in=ImageStatus.values), name="domain_image_status_valid"),
            models.CheckConstraint(condition=Q(content_type__in=("image/jpeg", "image/png", "image/webp")), name="d_image_content_type_valid"),
            models.CheckConstraint(condition=Q(byte_size__gt=0), name="domain_image_size_positive"),
            models.CheckConstraint(condition=Q(width__gt=0), name="domain_image_width_positive"),
            models.CheckConstraint(condition=Q(height__gt=0), name="domain_image_height_positive"),
            models.CheckConstraint(condition=(~Q(is_primary=True) | Q(status=ImageStatus.READY)), name="d_image_primary_ready"),
            models.UniqueConstraint(fields=("product",), condition=Q(is_primary=True), name="d_image_primary_uniq"),
        ]
        indexes = [models.Index(fields=("product", "status", "sort_order"), name="domain_image_product_list_idx")]

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.product_id and self.product.partner_id != self.partner_id:
            raise ValidationError({"product": "Image and product must share a partner."})
