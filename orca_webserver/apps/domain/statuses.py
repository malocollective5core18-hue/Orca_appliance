"""Single source of truth for persisted state values."""

from django.db import models


class RecordStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    INACTIVE = "inactive", "Inactive"


class AgreementStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    ACTIVE = "active", "Active"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"


class InstallmentStatus(models.TextChoices):
    DUE = "due", "Due"
    PARTIAL = "partial", "Partially paid"
    PAID = "paid", "Paid"
    WAIVED = "waived", "Waived"


class DeviceStatus(models.TextChoices):
    PROVISIONING = "provisioning", "Provisioning"
    ACTIVE = "active", "Active"
    RESTRICTED = "restricted", "Restricted"
    REPAIR = "repair", "Repair"
    RETIRED = "retired", "Retired"


class PairingStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    CONSUMED = "consumed", "Consumed"
    EXPIRED = "expired", "Expired"
    REVOKED = "revoked", "Revoked"


class PaymentStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PROCESSING = "processing", "Processing"
    SUCCEEDED = "succeeded", "Succeeded"
    FAILED = "failed", "Failed"
    CANCELLED = "cancelled", "Cancelled"
    REVERSED = "reversed", "Reversed"


class PaymentAttemptStatus(models.TextChoices):
    STARTED = "started", "Started"
    SUCCEEDED = "succeeded", "Succeeded"
    FAILED = "failed", "Failed"
    TIMED_OUT = "timed_out", "Timed out"


class WebhookStatus(models.TextChoices):
    RECEIVED = "received", "Received"
    PROCESSED = "processed", "Processed"
    REJECTED = "rejected", "Rejected"


class CommandStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    QUEUED = "queued", "Queued"
    DELIVERED = "delivered", "Delivered"
    ACKNOWLEDGED = "acknowledged", "Acknowledged"
    FAILED = "failed", "Failed"
    CANCELLED = "cancelled", "Cancelled"


class NotificationStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    SENT = "sent", "Sent"
    FAILED = "failed", "Failed"
    CANCELLED = "cancelled", "Cancelled"


class ImageStatus(models.TextChoices):
    UPLOADED = "UPLOADED", "Uploaded"
    PROCESSING = "PROCESSING", "Processing"
    READY = "READY", "Ready"
    REJECTED = "REJECTED", "Rejected"
    DELETED = "DELETED", "Deleted"
