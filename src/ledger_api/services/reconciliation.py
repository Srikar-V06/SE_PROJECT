"""Read-only ledger reconciliation on a single SQLite snapshot."""

from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Literal

from ledger_api.auth import timestamp
from ledger_api.ledger.verification import verify_entries
from ledger_api.providers.protocols import ClockProvider, DatabaseProvider


@dataclass
class ReconciliationReport:
    overall_status: Literal["PASS", "FAIL"]
    checked_transactions: int
    checked_wallets: int
    checked_entries: int
    failing_transaction_ids: list[str]
    failing_wallet_ids: list[str]
    failing_entry_ids: list[int]
    failing_currencies: list[str]
    generated_at: str


def reconcile(db: DatabaseProvider, clock: ClockProvider) -> ReconciliationReport:
    with db.connection() as conn:
        conn.execute("BEGIN")
        transactions = {
            row[0] for row in conn.execute("SELECT transaction_id FROM transactions")
        }
        wallets = conn.execute("SELECT * FROM wallets ORDER BY wallet_id").fetchall()
        treasuries = conn.execute(
            "SELECT account_id, currency FROM accounts WHERE type = 'SYSTEM_TREASURY'"
        ).fetchall()
        entries = conn.execute("SELECT * FROM ledger_entries ORDER BY entry_id").fetchall()

    # Python integers also handle lifetime turnover beyond SQLite SUM's range.
    accounts = Counter()
    currency_net = Counter()
    transaction_net = defaultdict(Counter)
    for entry in entries:
        currency = entry["currency"]
        delta = entry["amount_minor"]
        if entry["direction"] == "DEBIT":
            delta = -delta
        accounts[entry["account_id"]] += delta
        currency_net[currency] += delta
        transaction_net[entry["transaction_id"]][currency] += delta

    bad_transactions = []
    for tx in sorted(transactions | transaction_net.keys()):
        net = transaction_net[tx]
        if tx not in transactions or len(net) != 1 or any(net.values()):
            bad_transactions.append(tx)
    bad_wallets = []
    cached_net = Counter()
    for wallet in wallets:
        cached_net[wallet["currency"]] += wallet["balance_minor"]
        if wallet["balance_minor"] != accounts[wallet["account_id"]]:
            bad_wallets.append(wallet["wallet_id"])
    for treasury in treasuries:
        cached_net[treasury["currency"]] += accounts[treasury["account_id"]]

    bad_currencies = sorted(
        c for c in currency_net.keys() | cached_net.keys() if currency_net[c] or cached_net[c]
    )
    chain = verify_entries(entries)
    bad_entries = [] if chain.first_failing_entry_id is None else [chain.first_failing_entry_id]
    failed = any((bad_transactions, bad_wallets, bad_entries, bad_currencies))
    return ReconciliationReport(
        overall_status="FAIL" if failed else "PASS",
        checked_transactions=len(transactions),
        checked_wallets=len(wallets),
        checked_entries=len(entries),
        failing_transaction_ids=bad_transactions,
        failing_wallet_ids=bad_wallets,
        failing_entry_ids=bad_entries,
        failing_currencies=bad_currencies,
        generated_at=timestamp(clock.now()),
    )
