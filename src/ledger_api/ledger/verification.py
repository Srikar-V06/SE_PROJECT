"""Result type for ledger integrity checks."""

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True, slots=True)
class VerificationReport:
    overall_status: Literal["PASS", "FAIL"]
    entries_checked: int
    first_failing_entry_id: int | None = None
    reason: str | None = None
