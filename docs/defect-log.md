# Defect log

Record each significant defect with the observed result, expected result, affected
requirement, fix and a regression test that runs in CI. Keep the entry open until
the fix and its test have merged.

## D-001 · Self-transfer returned HTTP 500

**Fixed in [PR #43](https://github.com/Srikar-V06/SE_PROJECT/pull/43), commit `18da745`.**
A transfer between the same wallet IDs raised a service validation error. The API
returned 500 because the handler lacked a mapping for that error. FR-2 and NFR-19
require HTTP 400 for this invalid request. The fix maps `VALIDATION_ERROR` to 400.

Regression check in `tests/test_wallet_operations_api.py`:
`test_transfer_permissions_validation_and_concurrent_idempotent_replay` submits a
self-transfer and checks its status. It also checks the final transaction count
and both balances after the subsequent valid transfer.
