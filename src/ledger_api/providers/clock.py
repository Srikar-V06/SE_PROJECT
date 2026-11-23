"""System UTC clock provider."""

from datetime import UTC, datetime


class SystemClock:
    def now(self) -> datetime:
        return datetime.now(UTC)

    def timestamp(self) -> str:
        """Return a stable ISO-8601 UTC timestamp for persisted records."""
        return self.now().isoformat(timespec="seconds").replace("+00:00", "Z")
