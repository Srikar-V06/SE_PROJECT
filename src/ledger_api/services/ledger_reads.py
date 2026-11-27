"""Authorized transaction and ledger read operations."""

from ledger_api.domain.errors import NotFoundError, ValidationError
from ledger_api.providers.protocols import DatabaseProvider
from ledger_api.repositories.ledger_entries import LedgerEntryRepository
from ledger_api.repositories.transactions import TransactionRepository
from ledger_api.repositories.wallets import WalletRepository
from ledger_api.services.transaction_details import transaction_details


class LedgerReads:
    def __init__(self, db: DatabaseProvider) -> None:
        self._db = db

    def get_transaction(
        self,
        *,
        transaction_id: str,
        user_id: str,
        role: str,
    ) -> dict:
        with self._db.connection() as conn:
            transactions = TransactionRepository(conn)

            if role != "ADMIN" and not transactions.is_participant(
                transaction_id, user_id
            ):
                raise NotFoundError("Transaction not found")

            return transaction_details(conn, transaction_id)

    def get_entries(
        self,
        *,
        user_id: str,
        role: str,
        wallet_id: str | None,
        transaction_id: str | None,
        limit: int,
        offset: int,
    ) -> dict:
        if not 1 <= limit <= 100 or not 0 <= offset <= 2**63 - 1:
            raise ValidationError("Invalid pagination parameters")

        if role != "ADMIN" and wallet_id is None:
            raise ValidationError(
                "Users must provide an owned wallet_id"
            )

        with self._db.connection() as conn:
            account_id = None

            if wallet_id is not None:
                wallet = WalletRepository(conn).get(wallet_id)

                if (
                    role != "ADMIN"
                    and wallet["user_id"] != user_id
                ):
                    raise NotFoundError("Wallet not found")

                account_id = wallet["account_id"]

            rows = LedgerEntryRepository(conn).list_entries(
                account_id=account_id,
                transaction_id=transaction_id,
                limit=limit,
                offset=offset,
            )

            return {
                "entries": [dict(row) for row in rows],
                "limit": limit,
                "offset": offset,
            }