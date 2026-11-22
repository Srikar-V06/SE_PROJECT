PRAGMA foreign_keys = ON;

CREATE TABLE users (
  user_id TEXT PRIMARY KEY,
  normalized_email TEXT NOT NULL UNIQUE,
  name TEXT NOT NULL,
  password_hash TEXT NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('USER','ADMIN')),
  created_at TEXT NOT NULL
);

CREATE TABLE auth_sessions (
  session_id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES users(user_id),
  token_digest TEXT NOT NULL UNIQUE,
  created_at TEXT NOT NULL,
  expires_at TEXT NOT NULL,
  revoked_at TEXT
);

CREATE TABLE accounts (
  account_id TEXT PRIMARY KEY,
  type TEXT NOT NULL CHECK (type IN ('WALLET','SYSTEM_TREASURY')),
  currency TEXT NOT NULL CHECK (currency IN ('INR','USD')),
  created_at TEXT NOT NULL
);
-- exactly one treasury account per currency
CREATE UNIQUE INDEX ux_one_treasury_per_currency
  ON accounts(currency) WHERE type = 'SYSTEM_TREASURY';

CREATE TABLE wallets (
  wallet_id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL REFERENCES users(user_id),
  account_id TEXT NOT NULL UNIQUE REFERENCES accounts(account_id),
  currency TEXT NOT NULL CHECK (currency IN ('INR','USD')),
  balance_minor INTEGER NOT NULL DEFAULT 0 CHECK (balance_minor >= 0),
  created_at TEXT NOT NULL,
  UNIQUE (user_id, currency)
);

CREATE TABLE transactions (
  transaction_id TEXT PRIMARY KEY,
  type TEXT NOT NULL CHECK (type IN ('FUNDING','TRANSFER','REVERSAL')),
  reversal_of_transaction_id TEXT UNIQUE REFERENCES transactions(transaction_id),
  description TEXT,
  created_at TEXT NOT NULL
);

CREATE TABLE ledger_entries (
  entry_id INTEGER PRIMARY KEY,
  transaction_id TEXT NOT NULL REFERENCES transactions(transaction_id),
  account_id TEXT NOT NULL REFERENCES accounts(account_id),
  direction TEXT NOT NULL CHECK (direction IN ('CREDIT','DEBIT')),
  amount_minor INTEGER NOT NULL CHECK (amount_minor > 0),
  currency TEXT NOT NULL CHECK (currency IN ('INR','USD')),
  prev_hash TEXT NOT NULL,
  entry_hash TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE idempotency_keys (
  user_id TEXT NOT NULL REFERENCES users(user_id),
  key TEXT NOT NULL CHECK (length(key) BETWEEN 1 AND 128),
  operation TEXT NOT NULL,
  request_hash TEXT NOT NULL,
  response_status INTEGER NOT NULL,
  response_body TEXT NOT NULL,
  transaction_id TEXT REFERENCES transactions(transaction_id),
  created_at TEXT NOT NULL,
  expires_at TEXT NOT NULL,
  PRIMARY KEY (user_id, key)
);

-- entry currency must equal its account's currency (DR-8)
CREATE TRIGGER ledger_entries_currency_match
BEFORE INSERT ON ledger_entries
WHEN NEW.currency <> (SELECT currency FROM accounts WHERE account_id = NEW.account_id)
BEGIN
  SELECT RAISE(ABORT, 'entry currency must match account currency');
END;

-- seed one treasury per currency
INSERT INTO accounts (account_id, type, currency, created_at) VALUES
  (lower(hex(randomblob(16))), 'SYSTEM_TREASURY', 'INR', strftime('%Y-%m-%dT%H:%M:%SZ','now')),
  (lower(hex(randomblob(16))), 'SYSTEM_TREASURY', 'USD', strftime('%Y-%m-%dT%H:%M:%SZ','now'));

CREATE TRIGGER ledger_entries_no_update BEFORE UPDATE ON ledger_entries
BEGIN SELECT RAISE(ABORT, 'ledger_entries is append-only'); END;

CREATE TRIGGER ledger_entries_no_delete BEFORE DELETE ON ledger_entries
BEGIN SELECT RAISE(ABORT, 'ledger_entries is append-only'); END;

CREATE TRIGGER transactions_no_update BEFORE UPDATE ON transactions
BEGIN SELECT RAISE(ABORT, 'transactions is append-only'); END;

CREATE TRIGGER transactions_no_delete BEFORE DELETE ON transactions
BEGIN SELECT RAISE(ABORT, 'transactions is append-only'); END;