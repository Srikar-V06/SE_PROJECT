# User Guide

## Overview

The Financial Ledger and Digital Wallet API supports
authenticated wallet management.

This guide documents the currently implemented features.
Additional financial operations will be introduced in
later phases.

## Accessing the application

Start the application according to the README.

Open:

- http://127.0.0.1:8000/app/
- http://127.0.0.1:8000/docs

The browser interface is currently a placeholder.
The implemented API can be exercised through Swagger UI.

## Registration

Register using a name, email address and password.

Endpoint: POST /auth/register

Public registration creates a USER account.

## Login

Endpoint: POST /auth/login

Successful login returns an opaque bearer token with a
30-minute lifetime.

Use the token to authorize protected API requests.
Do not share or log the token.

## Wallet management

Create a wallet in INR or USD.

Endpoints:

- POST /users/{user_id}/wallets
- GET /users/me/wallets
- GET /wallets/{wallet_id}

Wallets start with a zero balance.

Users can create wallets only for their own accounts.
The backend enforces ownership restrictions.

## Logout

Endpoint: POST /auth/logout

Logout revokes the active session.

## Administrator accounts

Administrator accounts are created or granted through the
trusted local provisioning CLI.

Public registration cannot create an ADMIN account.

## Planned functionality

The following features will be completed in Phases 4 and 5:

- Wallet funding.
- Transfers.
- Transaction history.
- Reversals.
- Ledger reconciliation.
- Complete browser interface.

## Error handling

The API returns structured JSON errors containing
code and message fields.

Refer to openapi.yaml for the API contract.