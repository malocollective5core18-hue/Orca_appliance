from dataclasses import dataclass
from datetime import datetime, timezone


class SystemClock:
    def now(self) -> datetime:
        return datetime.now(timezone.utc)


@dataclass
class FrozenClock:
    current: datetime

    def now(self) -> datetime:
        return self.current

    def advance(self, **delta):
        from datetime import timedelta

        self.current += timedelta(**delta)
        return self.current
