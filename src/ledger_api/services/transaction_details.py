"""Build the response for a stored transaction."""

import sqlite3

from ledger_api.repositories.ledger_entries import LedgerEntryRepository
from ledger_api.repositories.transactions import TransactionRepository


def transaction_details(
    connection: sqlite3.Connection,
    transaction_id: str,
) -> dict:
    transaction = dict(
        TransactionRepository(connection).get(transaction_id)
    )

    entries = [
        dict(row)
        for row in LedgerEntryRepository(
            connection
        ).get_for_transaction(transaction_id)
    ]

    return {**transaction, "entries": entries}