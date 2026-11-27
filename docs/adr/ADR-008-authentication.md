# ADR-008: Opaque Session Authentication

Status: Proposed | Date: 2026-11-22 | Author: Vishwa-Pradyumna

## Context

Financial operations require individual user authentication,
ownership checks and administrative role restrictions.

## Decision

- Hash passwords using salted Argon2id.
- Generate opaque bearer tokens with at least 256 bits of randomness.
- Store only SHA-256 token digests.
- Set session expiry to 30 minutes.
- Revoke sessions on logout.
- Public registration creates USER accounts only.
- Validate identity, role and ownership on the server.

## Alternatives considered

- JWT-based authentication.
- Static API keys.
- External authentication providers.

## Consequences

Sessions can be revoked immediately. Protected requests require a
database-backed session check.

## Related Requirements

FR-6, C-7, NFR-9, NFR-10, NFR-13.

## Brain notes cited

[[authentication-sessions]]

## Implementation status

The Phase 3 backend authentication implementation uses
Argon2id, opaque bearer tokens, digest-only session storage
and server-side expiration and revocation.

The Phase 4 browser client uses these existing endpoints
and follows the in-memory session design in ADR-010.