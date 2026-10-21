from django.contrib import admin

from .models import (
    Agreement,
    AuditEvent,
    Customer,
    Device,
    DeviceCommand,
    DeviceStatusHistory,
    IdempotencyRecord,
    ImageAsset,
    Installment,
    Notification,
    PairingCode,
    Partner,
    Payment,
    PaymentAttempt,
    Product,
    ProviderWebhookEvent,
)


class ProtectedDeleteAdmin(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        return False


class ReadOnlyAuditAdmin(admin.ModelAdmin):
    list_display = ("created_at", "partner", "actor", "action", "entity_type", "entity_id")
    list_filter = ("action", "entity_type")
    search_fields = ("entity_id", "action")
    readonly_fields = tuple(field.name for field in AuditEvent._meta.fields)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class ReadOnlyDomainAdmin(admin.ModelAdmin):
    readonly_fields = ()

    def get_readonly_fields(self, request, obj=None):
        return tuple(field.name for field in self.model._meta.fields)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


for model in (
    Partner,
    Customer,
    Product,
    Agreement,
    Device,
):
    admin.site.register(model, ProtectedDeleteAdmin)

admin.site.register(AuditEvent, ReadOnlyAuditAdmin)
for model in (
    Installment,
    PairingCode,
    Payment,
    PaymentAttempt,
    ProviderWebhookEvent,
    DeviceCommand,
    DeviceStatusHistory,
    Notification,
    IdempotencyRecord,
    ImageAsset,
):
    admin.site.register(model, ReadOnlyDomainAdmin)
