"""Verification of the immutable ledger hash chain."""

import sqlite3
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any, Literal

from ledger_api.ledger.hash_chain import GENESIS_HASH, compute_entry_hash


@dataclass(frozen=True, slots=True)
class VerificationReport:
    overall_status: Literal["PASS", "FAIL"]
    entries_checked: int
    first_failing_entry_id: int | None = None
    reason: str | None = None


def verify_entries(
    rows: Iterable[sqlite3.Row | Mapping[str, Any]],
) -> VerificationReport:
    expected_prev = GENESIS_HASH
    checked = 0

    for row in rows:
        checked += 1
        entry_id = int(row["entry_id"])

        if entry_id != checked:
            return VerificationReport(
                "FAIL",
                checked,
                entry_id,
                "Unexpected entry ID sequence",
            )

        if row["prev_hash"] != expected_prev:
            return VerificationReport(
                "FAIL",
                checked,
                entry_id,
                "Previous hash does not match",
            )

        expected_hash = compute_entry_hash(
            row["prev_hash"],
            row["transaction_id"],
            row["account_id"],
            row["direction"],
            row["amount_minor"],
            row["currency"],
            row["created_at"],
            entry_id,
        )

        if row["entry_hash"] != expected_hash:
            return VerificationReport(
                "FAIL",
                checked,
                entry_id,
                "Entry hash does not match stored fields",
            )

        expected_prev = row["entry_hash"]

    return VerificationReport("PASS", checked)