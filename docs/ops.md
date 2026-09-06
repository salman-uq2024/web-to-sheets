# Support and recovery runbook

This runbook describes the current CLI. Use synthetic fixtures first; do not include credentials or scraped personal data in tickets.

## Establish the failure boundary

1. Record the command, working directory, Python version, site name, timestamp and exit code.
2. Run `ws validate <site>` to separate configuration faults from network or destination faults.
3. Run `ws run quotes --demo` to check the local extraction/CSV path without external access.
4. Read the corresponding timestamped text log in `logs/`. `LOG_LEVEL=DEBUG` enables debug messages where implemented; stack traces are not guaranteed.
5. Check whether a CSV was written and whether the intended destination actually received the rows.

## Exit codes

| Code | Current meaning | Next action |
| --- | --- | --- |
| 0 | Success, or no new unique rows | Compare expected row count with CSV/logs and destination |
| 1 | No command or no site configurations | Use `ws --help` and `ws list-sites` |
| 2 | Insufficient extracted rows; argparse also uses 2 for invalid syntax | Check command syntax, fixture/selectors and `min_rows` |
| 3 | Configuration or value validation failure | Run `ws validate <site>` and repair the named field |
| 4 | Runtime/network failure or unconfirmed Sheets delivery | Isolate source, filesystem, credentials, worksheet and API availability |

## Common incidents

| Symptom | Diagnosis | Recovery |
| --- | --- | --- |
| No new rows | Records may already be in `dedupe.db` | Verify the destination first; a repeat successful run should not resend them |
| CSV exists but Sheets is empty | Local processing succeeded; remote delivery did not | Check sheet ID, service-account access, credentials path and tab name; fix then retry |
| Authentication/permission failure | Client initialization or sheet access failed | Correct access for the existing service account; keep credentials out of the repo |
| Too few rows | Source layout changed, selector mismatch, or partial retrieval | Compare permitted source HTML with the YAML; reproduce with a local fixture before changing thresholds |
| Output cannot be written | Directory permissions or full disk | Restore writable storage; failed CSV writes do not checkpoint the rows |
| Source rejects collection | Domain/robots policy or remote service refusal | Verify permission and collection policy; do not bypass the restriction |

## Delivery semantics

Live mode extracts, validates, deduplicates and writes CSV, then attempts the Sheets append. Deduplication is committed only after the adapter confirms success. Unconfirmed delivery exits `4` and preserves retry eligibility. Within-batch duplicates are removed before minimum-row validation.

A timeout can be ambiguous: Google may have accepted the append even if the client never received confirmation. Check the sheet before retrying. A crash between append and checkpoint has the same risk. The system does not promise exactly-once delivery or safe concurrent writers; a destination-side idempotency key/upsert would be a future improvement.

Demo mode uses an in-memory deduplication store and never exports to Sheets. It can be repeated without deleting live state.

## Preserve evidence before resetting

Keep the relevant log, CSV and a backup of the SQLite state when investigating an incident. Do not delete `dedupe.db` simply to make a run succeed: that can resend historical rows. `DEDUPE_DB_PATH` selects an isolated state file for a deliberately separate run. Relative CSV/log/state paths resolve from the working directory.

## Optional notifications

If configured, `SLACK_WEBHOOK_URL` receives a failure summary with site name, run ID and exit code. It does not receive a log excerpt. Leave it unset for offline review and tests.

## Regression evidence

- [Processor tests](../tests/test_processor.py): duplicate batch, failed CSV write, deferred delivery.
- [CLI tests](../tests/test_cli.py): failed upload, successful retry, then no resend.
- [Sheets tests](../tests/test_sheets.py): failed sheet open and append return failure.

Local verification on 5 September 2026: 29 tests passed; Ruff passed. Remote Google access was mocked.
