---
title: Authentication and Sessions
type: resource
status: active
created: 2026-11-19
updated: 2026-11-22
author: BharathVikas-T
tags: [security, authentication, sessions]
sources:
  - docs/SRS.pdf
  - https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html
  - https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html
links: ["[[rest-api-design]]", "[[ai-policy]]"]
requirements: [FR-6.1, FR-6.2, FR-6.3, FR-6.4, FR-6.5, C-7, NFR-9, NFR-10]
---

## Summary
Authentication establishes a user identity, while a session carries that identity across later API requests. The SRS requires email and password registration, Argon2id password hashes, opaque bearer tokens, server-side session records, and ownership and role checks on protected routes.

## Key points
- The SRS requires passwords between 12 and 128 characters and Argon2id password hashing. OWASP recommends a unique salt and a memory-hard password hashing algorithm; its current minimum Argon2id profile is 19 MiB of memory, two iterations, and parallelism one.
- The login response issues an opaque random bearer token with a 30-minute lifetime. The SRS sequence specifies 256 bits of randomness. Store only the token's SHA-256 digest, and check expiry and revocation on every protected request.
- Logout must revoke the server-side session. Clearing a token in a client does not invalidate a copied token; server-side expiry and revocation are the controls that stop its later use.
- OWASP recommends a cryptographically secure random generator for session secrets and explains that storing a one-way verifier can reduce the impact of read-only disclosure of session records. It does not protect against a stolen live token or an attacker who can modify the session store.
- Never log bearer tokens or plaintext passwords. Use HTTPS outside loopback development, as required by the SRS.
- The SRS contains a wording conflict to resolve: FR-6.2 and the login sequence require returning the bearer token to the client, while FR-6.3 says tokens are never returned or logged. Preserve the explicit login response requirement and clarify FR-6.3 before implementation; do not silently reinterpret it.

## Relevance to this project
The API authenticates before ownership and role checks. Session lookup supplies the current user and role; wallet queries must use that identity rather than a user ID supplied by the caller. These decisions support [[rest-api-design]] and the AI review rules in [[ai-policy]].
