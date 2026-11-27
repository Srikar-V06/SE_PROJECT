"""Idempotent reversals using compensating ledger entries."""

from ledger_api.auth import timestamp
from ledger_api.domain.errors import (
    AlreadyReversedError,
    InsufficientFundsError,
    ReversalOfReversalError,
    ReversalOverdrawError,
)
from ledger_api.providers.protocols import (
    ClockProvider,
    DatabaseProvider,
    IdProvider,
)
from ledger_api.repositories.ledger_entries import LedgerEntryRepository
from ledger_api.repositories.transactions import TransactionRepository
from ledger_api.services.idempotency import (
    IdempotencyService,
    IdempotentResponse,
    OperationResponse,
)
from ledger_api.services.ledger_posting import PostingEntry, post_transaction
from ledger_api.services.transaction_details import transaction_details


class ReversalService:
    def __init__(
        self,
        db: DatabaseProvider,
        clock: ClockProvider,
        ids: IdProvider,
    ) -> None:
        self._clock = clock
        self._ids = ids
        self._idempotency = IdempotencyService(db, clock)

    def reverse(
        self,
        *,
        actor_user_id: str,
        transaction_id: str,
        key: str,
        description: str | None,
    ) -> IdempotentResponse:

        def action(conn):
            transactions = TransactionRepository(conn)
            original = transactions.get(transaction_id)

            if original["type"] == "REVERSAL":
                raise ReversalOfReversalError(
                    "A reversal cannot be reversed"
                )

            if transactions.get_reversal(transaction_id) is not None:
                raise AlreadyReversedError(
                    "Transaction has already been reversed"
                )

            original_entries = LedgerEntryRepository(
                conn
            ).get_for_transaction(transaction_id)

            opposite = {
                "DEBIT": "CREDIT",
                "CREDIT": "DEBIT",
            }

            reversal_entries = [
                PostingEntry(
                    account_id=row["account_id"],
                    direction=opposite[row["direction"]],
                    amount_minor=row["amount_minor"],
                    currency=row["currency"],
                )
                for row in original_entries
            ]

            reversal_id = self._ids.new_id()

            try:
                post_transaction(
                    conn,
                    transaction_id=reversal_id,
                    transaction_type="REVERSAL",
                    created_at=timestamp(self._clock.now()),
                    description=description,
                    reversal_of_transaction_id=transaction_id,
                    entries=reversal_entries,
                )
            except InsufficientFundsError as exc:
                raise ReversalOverdrawError(
                    "Reversal would make a wallet balance negative"
                ) from exc

            return OperationResponse(
                status_code=201,
                body=transaction_details(conn, reversal_id),
                transaction_id=reversal_id,
            )

        return self._idempotency.execute(
            user_id=actor_user_id,
            key=key,
            operation="transaction.reverse",
            path_params={"transaction_id": transaction_id},
            request_body={"description": description},
            action=action,
        )