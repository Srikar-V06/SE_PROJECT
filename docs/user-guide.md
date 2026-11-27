# User Guide

## Overview

The Financial Ledger and Digital Wallet API supports
authenticated wallets, funding, transfers, transaction
reversals and ledger history.

## Starting the application

From the repository root, install the dependencies and
start the local server:

```bash
python -m pip install -r requirements.txt
python -m uvicorn ledger_api.main:app --host 127.0.0.1 --port 8000
```

Open the browser interface at:

http://127.0.0.1:8000/app/

Open the interactive API documentation at:

http://127.0.0.1:8000/docs

## Registration and login

Select Create account on the login screen.

Enter your name, email address and a password containing
12 to 128 characters.

After registration, sign in using your email and password.

Public registration creates USER accounts only.

The browser stores session tokens in JavaScript memory.
Reloading the page requires a new login.

Sessions expire after 30 minutes.

## Wallet management

After signing in, the dashboard displays your own wallets.

Select INR or USD and choose Create wallet.

A new wallet has a zero balance. Each user can have one
wallet per supported currency.

Use Refresh to retrieve current wallet balances.

## Monetary amounts

The API represents money using integer minor units.

| Display amount | amount_minor |
|---|---:|
| INR 100.50 | 10050 |
| USD 25.00 | 2500 |
| INR 0.01 | 1 |

Financial requests require strict integer amounts between
1 and 1,000,000,000,000 minor units.

## Transfers

The transfer API is implemented in Phase 4.

Endpoint: POST /transfers

The caller must own the sender wallet.

The sender and recipient wallets must use the same currency.
The amount must be positive and the sender must have
sufficient funds.

A successful transfer returns HTTP 201 with the transaction
details and balanced ledger entries.

The request must include an Idempotency-Key header.

Transfer operations are currently available through the
interactive API documentation. The browser transfer screen
will be introduced in Phase 5.

## Wallet funding

Endpoint: POST /wallets/{wallet_id}/fund

Only administrators can fund wallets.

Funding creates a balanced transaction between the
system treasury and the selected wallet.

An Idempotency-Key header is required.

## Transaction history

Endpoint: GET /ledger-entries

Normal users must specify an owned wallet_id.

Administrators can query the global ledger.

The endpoint supports wallet_id, transaction_id,
limit and offset parameters.

Entries appear in ascending entry ID order.

Endpoint: GET /transactions/{transaction_id}

Returns a transaction and its ledger entries.
Only transaction participants and administrators have access.

## Transaction reversals

Endpoint: POST /transactions/{transaction_id}/reverse

Only administrators can reverse transactions.
An Idempotency-Key header is required.

Reversal creates a new compensating transaction rather than
editing or deleting the original entries.

A transaction can be reversed only once. A reversal that
would leave a wallet with a negative balance is rejected.

## Safe retry behavior

Funding, transfers and reversals require idempotency keys.

If a financial request has an uncertain outcome, retry the
same operation using the same idempotency key and identical
request content.

A replay returns the original result.

Do not create a new key for an uncertain retry.

## Administrator provisioning

Administrator accounts are managed through the trusted local
CLI, not through public registration.

Refer to the developer guide and README for the local
administrator provisioning procedure.

## Error handling

| Status | Meaning |
|---|---|
| 400 | Invalid request |
| 401 | Authentication required |
| 403 | Permission denied |
| 404 | Resource not found |
| 409 | Conflict or duplicate operation |
| 422 | Financial business-rule violation |
| 503 | Database temporarily busy |
| 500 | Unexpected internal error |

The API uses a shared JSON error format with code and
message fields.

## Logout

Choose Sign out from the dashboard.

This revokes the active server-side session and clears the
browser's authentication state.

If server-side revocation cannot be confirmed, the browser
clears the local session and displays an appropriate message.

## Phase 5 functionality

The following features remain planned:

- Browser transfer forms and receipts.
- Browser transaction history.
- Browser administrator controls.
- Ledger reconciliation.
- Complete browser system testing.

## References

- [API specification](openapi.yaml)
- [Developer guide](developer-guide.md)
- [UI design](ui-design.md)