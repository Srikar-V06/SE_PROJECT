# Traceability Matrix

SRS version: v2.0

Pending entries represent work that has not yet been implemented
or linked to its GitHub Issue.

| Requirement | Issue | PR | Test | Skill | Brain note |
|---|---|---|---|---|---|
| FR-1 Wallet initialization | Pending | #17, #21, #27 | test_auth_wallets.py | local-check | double-entry-bookkeeping |
| FR-2 Idempotent transfers | Pending | #19, #22 | Planned Phase 4 | simulate-transfer (planned) | idempotency-keys |
| FR-3 Concurrency | Pending | #17, #21 | test_database.py; concurrency tests planned | local-check | race-conditions, sqlite-acid-wal |
| FR-4 Audit trail | #12 (design) | #17, #21, #23, #30 | test_hash_chain.py | local-check | double-entry-bookkeeping |
| FR-5 Reconciliation | Pending | #19 (design) | Planned Phase 5 | simulate-transfer (planned) | double-entry-bookkeeping |
| FR-6 Authentication | Pending | #27, #31 | test_auth_wallets.py, test_auth_unit.py | local-check | authentication-sessions |
| FR-7 Web UI | Pending | #28 | Browser tests planned | local-check | authentication-sessions |
| NFR-1 to NFR-3 | Pending | Planned | Performance tests planned | simulate-transfer (planned) | race-conditions |
| NFR-4 to NFR-8 | Pending | #21, #23 | test_database.py; further tests planned | local-check | sqlite-acid-wal |
| NFR-9 to NFR-15 | Pending | #27, #31 | test_auth_unit.py, test_auth_wallets.py | local-check | authentication-sessions |
| NFR-16 to NFR-19 | Pending | #22, #30, #31 | test_money.py, test_error_responses.py | local-check | integer-minor-units |
| NFR-20 to NFR-23 | Pending | #26, #29-32 | Unit suite and CI | local-check | testing-strategy |
| BR-1 to BR-9 | Pending | #17, #19 | Unit and financial tests | local-check | double-entry-bookkeeping |
| DR-1 to DR-13 | #12 (design) | #17, #21-23 | test_database.py, test_hash_chain.py | local-check | sqlite-acid-wal |
| C-1 to C-8 | Pending | #17, #19, #28 | Architecture and implementation checks | local-check | integer-minor-units |
| A-1 to A-7 | Pending | #19, #27, #28 | Relevant implementation tests | local-check | authentication-sessions |
| SK-1 Brain ingest | Pending | Initial work | Skill evaluation | brain-ingest | second-brain |
| SK-2 Brain refine | Pending | #13, #20 | Brain refine evaluation | brain-refine | second-brain |
| SK-3 Brain query | Pending | #14, #20 | Brain query evaluation | brain-query | agent-skills |
| SK-4 Local check | Pending | #26 | Local verification | local-check | testing-strategy |
| SK-5 Simulate transfer | Pending | Planned | Planned Phase 5 | simulate-transfer (planned) | idempotency-keys |
| SB-1 to SB-3 | Pending | Brain PRs | Brain validators and reviews | brain-refine | second-brain, ai-policy |
| SE-1 to SE-4 | Pending | #17, #19, #26, #28 | Documentation review | brain-query | rest-api-design |
| TQ-1 Unit testing | Pending | #29-31 | Unit suite | local-check | testing-strategy |
| TQ-2 Integration testing | Pending | #27 (initial) | Authentication and wallet tests; further tests planned | local-check | testing-strategy |
| TQ-3 System testing | Pending | Planned | Planned Phase 5 | simulate-transfer (planned) | testing-strategy |
| TQ-4 Negative and security testing | Pending | #27, #30, #31 | Existing negative tests; further tests planned | local-check | authentication-sessions |
| TQ-5 Money precision | Pending | #30 | test_money.py; UI tests planned | local-check | integer-minor-units |
| TQ-6 CI and regression | Pending | #26, #32 | CI and coverage | local-check | github-actions |
| P-1 to P-4 | Pending | #26, #32, #33 | CI, project records and review | local-check | ai-policy |

## Current verification

45 automated tests passed with 86% code coverage
in the Phase 3 CI run.

The ledger engine, transfers, reconciliation and completed
web interface are future implementation tasks.