from typing import Protocol


class SmsBackend(Protocol):
    def send(self, phone_number: str, message: str) -> None: ...
