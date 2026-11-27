# ADR-010: Same-Origin UI and In-Memory Session Tokens

Status: Proposed | Date: 2026-11-25 | Author: Vishwa-Pradyumna

## Context

The project requires a basic browser interface for authenticated
wallet management and administrative operations.

The browser must communicate securely with the backend without
persisting sensitive session tokens.

The SRS specifies a same-origin static client and opaque
server-side sessions.

## Decision

- Serve the UI using FastAPI at /app.
- Implement the interface using HTML, CSS and JavaScript.
- Communicate with the API through same-origin requests.
- Store the opaque bearer token only in JavaScript memory.
- Do not store authentication tokens in localStorage,
  sessionStorage or cookies.
- Send the token through the Authorization header.
- Require login after page reload or session expiry.
- Clear the token on logout or an HTTP 401 response.
- Render user-provided content as text instead of HTML.
- Use HTTPS for non-loopback deployments.
- Enforce all role and ownership permissions on the backend.

Logout revokes the server-side session through POST /auth/logout.

## Alternatives considered

### Browser persistent storage

Storing tokens in localStorage or sessionStorage would allow
session information to persist across browser operations but
conflicts with the SRS token storage requirements.

### Cookie-based authentication

Cookies would require a different browser authentication design.
This is not the selected session mechanism for the project.

### Separate frontend server

A separately hosted frontend would introduce additional
configuration and cross-origin communication.

## Consequences

- The UI and API can be deployed together.
- No authentication token is intentionally persisted in
  browser storage.
- Reloading the page requires a new login.
- Expired sessions require reauthentication.
- The server remains responsible for authorization.
- In-memory storage does not eliminate all browser security
  risks, so safe rendering is still necessary.

## Related Requirements

C-6, C-7, A-5, FR-6, FR-7.7, NFR-14, NFR-15, TBD-9.

## References

- [SRS v2.0](../SRS.pdf)
- [UI Design](../ui-design.md)
- [ADR-008](ADR-008-authentication.md)

## Brain notes cited

[[authentication-sessions]]

## Phase 4 implementation

The static application is implemented in
src/ledger_api/static/.

The authentication token is held in JavaScript memory.

The browser uses same-origin REST requests, clears session
state after logout and HTTP 401 responses, and requires
authentication again after page reload.

User-provided content is rendered using textContent.

Frontend linting is included in the CI lint job.

Related requirements: FR-7.1, FR-7.2, FR-7.7, NFR-14, NFR-21.