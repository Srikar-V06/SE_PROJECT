import sqlite3

db = sqlite3.connect(":memory:")
db.execute("PRAGMA foreign_keys = ON")
db.executescript(open("docs/schema.sql").read())

def must_fail(label, sql):
    try:
        db.execute(sql)
        print("FAIL (was allowed):", label)
    except sqlite3.Error as e:
        print("PASS:", label, "->", e)

now = "'2026-11-20T10:00:00Z'"
db.execute(f"INSERT INTO users VALUES ('u1','a@x.com','A','h','USER',{now})")
db.execute(f"INSERT INTO accounts VALUES ('a1','WALLET','INR',{now})")
db.execute(f"INSERT INTO accounts VALUES ('a2','WALLET','INR',{now})")
db.execute(f"INSERT INTO wallets VALUES ('w1','u1','a1','INR',0,{now})")
db.execute(f"INSERT INTO transactions VALUES ('t1','FUNDING',NULL,'x',{now})")
db.execute(f"INSERT INTO ledger_entries VALUES (1,'t1','a1','CREDIT',100,'INR','0','h',{now})")

must_fail("second INR wallet for same user", f"INSERT INTO wallets VALUES ('w2','u1','a2','INR',0,{now})")
must_fail("second INR treasury", f"INSERT INTO accounts VALUES ('a3','SYSTEM_TREASURY','INR',{now})")
must_fail("zero amount", f"INSERT INTO ledger_entries VALUES (2,'t1','a1','CREDIT',0,'INR','0','h',{now})")
must_fail("currency mismatch", f"INSERT INTO ledger_entries VALUES (3,'t1','a1','CREDIT',5,'USD','0','h',{now})")
must_fail("negative balance", "UPDATE wallets SET balance_minor = -1")
db.execute(f"INSERT INTO idempotency_keys VALUES ('u1','k1','TRANSFER','h',201,'{{}}',NULL,{now},{now})")
must_fail("duplicate (user_id, key)", f"INSERT INTO idempotency_keys VALUES ('u1','k1','TRANSFER','h',201,'{{}}',NULL,{now},{now})")
must_fail("UPDATE ledger_entries", "UPDATE ledger_entries SET amount_minor = 999")
must_fail("DELETE ledger_entries", "DELETE FROM ledger_entries")
must_fail("UPDATE transactions", "UPDATE transactions SET description = 'y'")
must_fail("DELETE transactions", "DELETE FROM transactions")