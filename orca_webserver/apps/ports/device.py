from typing import Protocol


class DeviceTransport(Protocol):
    def queue(self, command_id: int) -> None: ...

    def deliver(self, device_id: int, *, limit: int = 20) -> list[dict]: ...
