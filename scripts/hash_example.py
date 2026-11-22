import hashlib

GENESIS = "0" * 64

def entry_hash(prev, tx, acct, direction, amount, currency, ts, entry_id):
    s = "|".join([prev, tx, acct, direction, str(amount), currency, ts, str(entry_id)])
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

h1 = entry_hash(GENESIS, "T-1", "ACC-A", "DEBIT", 500, "INR", "2026-11-20T10:00:00Z", 1)
h2 = entry_hash(h1, "T-1", "ACC-B", "CREDIT", 500, "INR", "2026-11-20T10:00:00Z", 2)
print("entry 1:", h1)
print("entry 2:", h2)