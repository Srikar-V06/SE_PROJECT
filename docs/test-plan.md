# Test Plan

## Objective

Verify all functional and non-functional requirements using automated
unit, integration, system, security and regression tests.

## Test Environment

- Python 3.11 or later.
- Pytest.
- FastAPI TestClient.
- Temporary file-backed SQLite database.
- Test-only credentials and deterministic provider fakes.
- No access to production data.

Every database-dependent test must initialize a fresh isolated database
using the migrations. Pytest temporary-directory fixtures will be used.

## Requirements Mapping

| Requirement | Test coverage | Phase |
|---|---|---|
| TQ-1 | Money arithmetic, double-entry balance, hashing and token validation | 3 |
| TQ-2 | Atomic commit, rollback, ownership and session lifecycle | 4 |
| TQ-3 | Complete API and browser workflows | 5 |
| TQ-4 | Negative, security and concurrency checks | 4-5 |
| TQ-5 | Exact integer monetary representation | 3-5 |
| TQ-6 | CI, isolated tests, regression tests and skill evaluations | 3-6 |

## Unit Tests

- Exact minor-unit arithmetic.
- Invalid monetary input rejection.
- Password hashing and verification.
- Token digest and expiration.
- Ledger hash calculation.
- Database constraints and immutability triggers.

## Integration Tests

- Successful wallet funding and transfers.
- Atomic rollback after a controlled failure.
- Idempotent response replay.
- Reversal restrictions.
- Ownership and session checks.

## System Tests

- Register and log in.
- Create a wallet.
- Admin funds a wallet.
- Perform a transfer and retry it safely.
- View transaction history.
- Reverse a transaction.
- Reconcile the ledger.
- Log out.

## Security Test Plan

These tests are performed only against the isolated test application.

| Test | Expected result |
|---|---|
| Missing or invalid session | 401 |
| Expired or revoked session | 401 |
| USER requests ADMIN operation | 403 |
| Non-owner reads protected wallet | 404 |
| Invalid request fields | 400 |
| Invalid login credentials | Generic 401 |
| Password or token exposure in responses or logs | No exposure |
| UI receives user-supplied text | Displayed safely as text |

## Concurrency Tests

- Verify financial correctness with concurrent requests.
- Verify wallet balances never become negative.
- Verify duplicate requests produce at most one transaction.
- Verify reconciliation remains consistent during writes.

## Regression Tests

Every significant corrected defect must have a regression test.

## Performance Tests

Measure the performance requirements defined by NFR-1 to NFR-3
using a documented local test environment.

## CI Requirements

Every push and pull request must run:

- Build
- Lint
- Automated tests
- Secret scanning
- Brain validation
- Skill validation

## Test Status

Only the GET /health test is introduced by the walking skeleton.

The remaining tests are planned for Phases 3 to 6 and must not be
reported as passed before being implemented and executed.

## References

- [SRS](SRS.pdf)
- [[testing-strategy]]
- [[github-actions]]

## Additional verification required by Final Project Plan v2

| Test area | Requirement |
|---|---|
| Financial request integer boundary validation | TQ-5, NFR-16 |
| Idempotency expiry and replay | FR-2.8, NFR-18 | `tests/test_idempotency.py` |
| Concurrent identical requests | FR-3.4 | `tests/test_idempotency.py` |
| Ledger integrity detection | AC-4.3 |
| Reconciliation mismatch detection | AC-5.2 |
| Restart durability | NFR-7 |
| JavaScript integer conversion | TQ-5 |
| Responsive UI at 360 pixels | FR-7, NFR-22 |
| Cross-platform verification | NFR-22 |
| JSON error format | NFR-19 |
| UI lint | NFR-21 |

## Phase 3 test results

The merged Phase 3 unit testing and CI work in PRs #29-32
reported 45 passing tests and 86% code coverage.

Tests for production helpers that have not yet been implemented
remain pending.

## Phase 4 idempotency verification

PR #40 adds coverage for canonical request
hashing, successful response replay, mismatched-key conflicts, expiration,
rollback on action failure, concurrent identical requests, key validation
and the 24-hour minimum retention period. The branch also verifies that
`IDEMPOTENCY_KEY_REUSED` uses the shared JSON error shape and HTTP 409.

Wallet funding API integration is local work pending review. Endpoint-level
test coverage and verification remain outstanding for this change.
