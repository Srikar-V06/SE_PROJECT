import pytest

from ledger_api.domain.errors import (
    InsufficientFundsError,
    ValidationError,
)
from ledger_api.repositories.accounts import AccountRepository
from ledger_api.repositories.ledger_entries import LedgerEntryRepository
from ledger_api.repositories.users import UserRepository
from ledger_api.repositories.wallets import WalletRepository
from ledger_api.services.ledger_posting import (
    PostingEntry,
    post_transaction,
)

TIMESTAMP = "2026-11-26T00:00:00Z"


@pytest.fixture
def posting_accounts(db, fake_ids):
    with db.write_transaction() as conn:
        users = UserRepository(conn)
        accounts = AccountRepository(conn)
        wallets = WalletRepository(conn)

        result = {}

        for name in ("sender", "receiver"):
            user_id = fake_ids.new_id()
            account_id = fake_ids.new_id()
            wallet_id = fake_ids.new_id()

            users.create(
                user_id,
                f"{name}@example.org",
                name,
                "test-only-password-hash",
                "USER",
                TIMESTAMP,
            )

            accounts.create(
                account_id,
                "WALLET",
                "INR",
                TIMESTAMP,
            )

            wallets.create(
                wallet_id,
                user_id,
                account_id,
                "INR",
                TIMESTAMP,
            )

            result[f"{name}_account"] = account_id
            result[f"{name}_wallet"] = wallet_id

        treasury = accounts.get_treasury("INR")
        result["treasury"] = treasury["account_id"]

    return result


def fund_sender(db, fake_ids, posting_accounts):
    with db.write_transaction() as conn:
        return post_transaction(
            conn,
            transaction_id=fake_ids.new_id(),
            transaction_type="FUNDING",
            created_at=TIMESTAMP,
            entries=[
                PostingEntry(
                    posting_accounts["treasury"],
                    "DEBIT",
                    10000,
                    "INR",
                ),
                PostingEntry(
                    posting_accounts["sender_account"],
                    "CREDIT",
                    10000,
                    "INR",
                ),
            ],
        )


def test_funding_updates_balance(db, fake_ids, posting_accounts):
    entry_ids = fund_sender(db, fake_ids, posting_accounts)

    with db.connection() as conn:
        wallet = WalletRepository(conn).get(
            posting_accounts["sender_wallet"]
        )

        assert wallet["balance_minor"] == 10000
        assert len(entry_ids) == 2

        count = conn.execute(
            "SELECT COUNT(*) FROM transactions"
        ).fetchone()[0]

        assert count == 1


def test_transfer_updates_both_wallets(
    db, fake_ids, posting_accounts
):
    fund_sender(db, fake_ids, posting_accounts)

    with db.write_transaction() as conn:
        post_transaction(
            conn,
            transaction_id=fake_ids.new_id(),
            transaction_type="TRANSFER",
            created_at=TIMESTAMP,
            entries=[
                PostingEntry(
                    posting_accounts["sender_account"],
                    "DEBIT",
                    4000,
                    "INR",
                ),
                PostingEntry(
                    posting_accounts["receiver_account"],
                    "CREDIT",
                    4000,
                    "INR",
                ),
            ],
        )

    with db.connection() as conn:
        wallets = WalletRepository(conn)

        sender = wallets.get(posting_accounts["sender_wallet"])
        receiver = wallets.get(posting_accounts["receiver_wallet"])

        assert sender["balance_minor"] == 6000
        assert receiver["balance_minor"] == 4000

        report = LedgerEntryRepository(conn).verify_chain()

        assert report.overall_status == "PASS"
        assert report.entries_checked == 4


def test_unbalanced_entries_rejected(
    db, fake_ids, posting_accounts
):
    with pytest.raises(ValidationError), db.write_transaction() as conn:
        post_transaction(
            conn,
            transaction_id=fake_ids.new_id(),
            transaction_type="FUNDING",
            created_at=TIMESTAMP,
            entries=[
                PostingEntry(
                    posting_accounts["treasury"],
                    "DEBIT",
                    1000,
                    "INR",
                ),
                PostingEntry(
                    posting_accounts["sender_account"],
                    "CREDIT",
                    500,
                    "INR",
                ),
            ],
        )

    with db.connection() as conn:
        assert conn.execute(
            "SELECT COUNT(*) FROM transactions"
        ).fetchone()[0] == 0

        assert conn.execute(
            "SELECT COUNT(*) FROM ledger_entries"
        ).fetchone()[0] == 0


def test_insufficient_balance_rejected(
    db, fake_ids, posting_accounts
):
    with (
        pytest.raises(InsufficientFundsError),
        db.write_transaction() as conn,
    ):
        post_transaction(
            conn,
            transaction_id=fake_ids.new_id(),
            transaction_type="TRANSFER",
            created_at=TIMESTAMP,
            entries=[
                PostingEntry(
                    posting_accounts["sender_account"],
                    "DEBIT",
                    1000,
                    "INR",
                ),
                PostingEntry(
                    posting_accounts["receiver_account"],
                    "CREDIT",
                    1000,
                    "INR",
                ),
            ],
        )

    with db.connection() as conn:
        wallets = WalletRepository(conn)

        assert wallets.get(
            posting_accounts["sender_wallet"]
        )["balance_minor"] == 0

        assert wallets.get(
            posting_accounts["receiver_wallet"]
        )["balance_minor"] == 0

        assert conn.execute(
            "SELECT COUNT(*) FROM transactions"
        ).fetchone()[0] == 0


def test_posting_rolls_back_on_failure(
    db, fake_ids, posting_accounts, monkeypatch
):
    original_append = LedgerEntryRepository.append

    def failing_append(self, **kwargs):
        if kwargs["direction"] == "CREDIT":
            raise RuntimeError("Simulated posting failure")

        return original_append(self, **kwargs)

    monkeypatch.setattr(
        LedgerEntryRepository,
        "append",
        failing_append,
    )

    with pytest.raises(RuntimeError, match="Simulated posting failure"):
        fund_sender(db, fake_ids, posting_accounts)

    with db.connection() as conn:
        assert conn.execute(
            "SELECT COUNT(*) FROM transactions"
        ).fetchone()[0] == 0

        assert conn.execute(
            "SELECT COUNT(*) FROM ledger_entries"
        ).fetchone()[0] == 0

        wallet = WalletRepository(conn).get(
            posting_accounts["sender_wallet"]
        )

        assert wallet["balance_minor"] == 0