"""Idempotent funding and transfer operations backed by ledger posting."""

from __future__ import annotations

from ledger_api.auth import timestamp
from ledger_api.providers.protocols import (
    ClockProvider,
    DatabaseProvider,
    IdProvider,
)
from ledger_api.repositories.accounts import AccountRepository
from ledger_api.repositories.ledger_entries import LedgerEntryRepository
from ledger_api.repositories.transactions import TransactionRepository
from ledger_api.repositories.wallets import WalletRepository
from ledger_api.services.idempotency import (
    IdempotencyService,
    IdempotentResponse,
    OperationResponse,
)
from ledger_api.services.ledger_posting import PostingEntry, post_transaction


class WalletOperations:
    """Run wallet operations through the shared posting and retry services."""

    def __init__(
        self,
        db: DatabaseProvider,
        clock: ClockProvider,
        ids: IdProvider,
    ) -> None:
        self._clock = clock
        self._ids = ids
        self._idempotency = IdempotencyService(db, clock)

    def fund(
        self,
        *,
        actor_user_id: str,
        wallet_id: str,
        key: str,
        amount_minor: int,
        description: str | None,
    ) -> IdempotentResponse:
        body = {"amount_minor": amount_minor, "description": description}

        def action(conn):
            wallet = WalletRepository(conn).get(wallet_id)
            treasury = AccountRepository(conn).get_treasury(wallet["currency"])
            if treasury is None:
                raise RuntimeError("system treasury is missing for wallet currency")

            transaction_id = self._ids.new_id()
            created_at = timestamp(self._clock.now())
            post_transaction(
                conn,
                transaction_id=transaction_id,
                transaction_type="FUNDING",
                created_at=created_at,
                description=description,
                entries=(
                    PostingEntry(
                        treasury["account_id"], "DEBIT", amount_minor, wallet["currency"]
                    ),
                    PostingEntry(
                        wallet["account_id"], "CREDIT", amount_minor, wallet["currency"]
                    ),
                ),
            )
            return self._created_response(conn, transaction_id)

        return self._idempotency.execute(
            user_id=actor_user_id,
            key=key,
            operation="wallet.fund",
            path_params={"wallet_id": wallet_id},
            request_body=body,
            action=action,
        )

    @staticmethod
    def _created_response(conn, transaction_id: str) -> OperationResponse:
        transaction = dict(TransactionRepository(conn).get(transaction_id))
        entries = [
            dict(row)
            for row in LedgerEntryRepository(conn).get_for_transaction(transaction_id)
        ]
        return OperationResponse(
            status_code=201,
            body={**transaction, "entries": entries},
            transaction_id=transaction_id,
        )
