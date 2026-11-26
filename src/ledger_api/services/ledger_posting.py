"""Atomic double-entry transaction posting."""

import sqlite3
from collections.abc import Sequence
from dataclasses import dataclass

from ledger_api.domain.errors import (
    InsufficientFundsError,
    NotFoundError,
    ValidationError,
)
from ledger_api.repositories.accounts import AccountRepository
from ledger_api.repositories.ledger_entries import LedgerEntryRepository
from ledger_api.repositories.transactions import TransactionRepository
from ledger_api.repositories.wallets import WalletRepository

MAX_POSTING_AMOUNT = 10**12
MAX_SQLITE_INTEGER = 2**63 - 1


@dataclass(frozen=True, slots=True)
class PostingEntry:
    account_id: str
    direction: str
    amount_minor: int
    currency: str


def validate_balanced_entries(
    entries: Sequence[PostingEntry],
) -> None:
    """Validate double-entry rules before writing anything."""

    if len(entries) < 2:
        raise ValidationError(
            "A transaction must contain at least two entries"
        )

    currency = entries[0].currency
    total_debits = 0
    total_credits = 0

    for entry in entries:
        if entry.direction not in {"DEBIT", "CREDIT"}:
            raise ValidationError("Invalid entry direction")

        if (
            isinstance(entry.amount_minor, bool)
            or not isinstance(entry.amount_minor, int)
            or not 1 <= entry.amount_minor <= MAX_POSTING_AMOUNT
        ):
            raise ValidationError(
                "Posting amount must be an integer between 1 and 10^12"
            )

        if entry.currency not in {"INR", "USD"}:
            raise ValidationError("Unsupported currency")

        if entry.currency != currency:
            raise ValidationError(
                "Transaction entries must use the same currency"
            )

        if entry.direction == "DEBIT":
            total_debits += entry.amount_minor
        else:
            total_credits += entry.amount_minor

    if total_debits != total_credits:
        raise ValidationError("Total debits must equal total credits")


def post_transaction(
    connection: sqlite3.Connection,
    *,
    transaction_id: str,
    transaction_type: str,
    entries: Sequence[PostingEntry],
    created_at: str,
    description: str | None = None,
    reversal_of_transaction_id: str | None = None,
) -> tuple[int, ...]:
    """Post entries using the caller's active write transaction.

    The caller must hold a BEGIN IMMEDIATE transaction and
    allow exceptions to propagate so failures are rolled back.
    This function never commits independently.
    """

    if not connection.in_transaction:
        raise RuntimeError(
            "Posting requires an active write transaction"
        )

    if transaction_type not in {"FUNDING", "TRANSFER", "REVERSAL"}:
        raise ValidationError("Invalid transaction type")

    if transaction_type == "REVERSAL":
        if not reversal_of_transaction_id:
            raise ValidationError("Original transaction is required")
    elif reversal_of_transaction_id is not None:
        raise ValidationError(
            "Only reversals may reference an original transaction"
        )

    entries = tuple(entries)
    validate_balanced_entries(entries)

    accounts = AccountRepository(connection)
    wallets = WalletRepository(connection)
    transactions = TransactionRepository(connection)
    ledger = LedgerEntryRepository(connection)

    wallet_deltas: dict[str, int] = {}

    # Validate accounts and calculate each wallet's net change.
    for entry in entries:
        account = accounts.get(entry.account_id)

        if account is None:
            raise NotFoundError("Ledger account not found")

        if account["currency"] != entry.currency:
            raise ValidationError("Entry and account currencies must match")

        # Treasury balances are derived from the ledger.
        if account["type"] == "SYSTEM_TREASURY":
            continue

        wallet = wallets.get_by_account(entry.account_id)

        if wallet is None:
            raise NotFoundError("Wallet account not found")

        if wallet["currency"] != entry.currency:
            raise ValidationError("Wallet currency mismatch")

        wallet_id = wallet["wallet_id"]
        delta = entry.amount_minor

        if entry.direction == "DEBIT":
            delta = -delta

        wallet_deltas[wallet_id] = (
            wallet_deltas.get(wallet_id, 0) + delta
        )

    # Check final balances before inserting any records.
    for wallet_id, delta in wallet_deltas.items():
        wallet = wallets.get(wallet_id)
        new_balance = wallet["balance_minor"] + delta

        if new_balance < 0:
            raise InsufficientFundsError(
                "Posting would result in a negative wallet balance"
            )

        if new_balance > MAX_SQLITE_INTEGER:
            raise ValidationError("Wallet balance exceeds storage limit")

    transactions.create(
        transaction_id,
        transaction_type,
        created_at,
        description=description,
        reversal_of_transaction_id=reversal_of_transaction_id,
    )

    entry_ids = []

    # Existing repository assigns entry IDs and computes hashes.
    for entry in entries:
        entry_id = ledger.append(
            transaction_id=transaction_id,
            account_id=entry.account_id,
            direction=entry.direction,
            amount_minor=entry.amount_minor,
            currency=entry.currency,
            created_at=created_at,
        )

        entry_ids.append(entry_id)

    for wallet_id, delta in wallet_deltas.items():
        wallets.apply_delta(wallet_id, delta)

    return tuple(entry_ids)