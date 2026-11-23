"""Hash-chain functions for the immutable ledger."""

from __future__ import annotations

import hashlib

GENESIS_HASH = "0" * 64


def compute_entry_hash(
    prev_hash: str,
    transaction_id: str,
    account_id: str,
    direction: str,
    amount_minor: int,
    currency: str,
    created_at: str,
    entry_id: int,
) -> str:
    """Hash the exact persisted field sequence specified by the design."""
    payload = "|".join(
        (
            prev_hash,
            transaction_id,
            account_id,
            direction,
            str(amount_minor),
            currency,
            created_at,
            str(entry_id),
        )
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
