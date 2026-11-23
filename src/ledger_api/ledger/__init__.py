"""Append-only ledger support and hash-chain verification."""

from ledger_api.ledger.hash_chain import GENESIS_HASH, compute_entry_hash

__all__ = ["GENESIS_HASH", "compute_entry_hash"]
