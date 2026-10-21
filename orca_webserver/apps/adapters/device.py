"""Database-backed command queue polled over future authenticated HTTPS endpoints."""

from django.db import transaction

from apps.adapters.clock import SystemClock
from apps.domain.models import DeviceCommand
from apps.domain.services import transition_command
from apps.domain.statuses import CommandStatus


class DatabaseQueueDeviceTransport:
    def __init__(self, *, clock=None):
        self.clock = clock or SystemClock()

    def queue(self, command_id: int) -> None:
        with transaction.atomic():
            command = DeviceCommand.objects.select_for_update().get(pk=command_id)
            transition_command(command, CommandStatus.QUEUED)

    def deliver(self, device_id: int, *, limit: int = 20) -> list[dict]:
        if not 1 <= limit <= 100:
            raise ValueError("limit must be between 1 and 100")
        now = self.clock.now()
        delivered = []
        with transaction.atomic():
            commands = list(
                DeviceCommand.objects.select_for_update(skip_locked=True)
                .filter(device_id=device_id, status=CommandStatus.QUEUED, available_at__lte=now)
                .order_by("available_at", "created_at", "id")[:limit]
            )
            for command in commands:
                transition_command(command, CommandStatus.DELIVERED, clock=self.clock, delivered_at=now)
                command.delivery_count += 1
                command.save(update_fields=("delivery_count",))
                delivered.append(
                    {
                        "id": command.pk,
                        "type": command.command_type,
                        "payload": command.payload,
                        "created_at": command.created_at.isoformat(),
                    }
                )
        return delivered
