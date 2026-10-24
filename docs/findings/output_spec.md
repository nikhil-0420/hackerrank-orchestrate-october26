# Ghost Data Still Exists: Output Specification & Ground Truth Reference

This document records the exact output specification, field definitions, legal operations, ordering constraints, sample baseline rows, and ambiguities extracted directly from `problem_statement.md` and participant dataset files.

---

## 1. Output CSV Specification

*Source: `problem_statement.md` Lines 61-75*

The required submission file is `output.csv` (written at repository root).

### 1.1 Header
```text
case_id,deletion_status,steps_json
```
- Exactly 3 columns in this exact order.

### 1.2 Row Count & Order
- Exactly 518 data rows (one row for every `case_id` in `dataset/deletion_requests.csv`).
- Rows must be sorted by `case_id`.
  - In `dataset/deletion_requests.csv`, rows are naturally ordered: `case_33` through `case_550`.
  - In `dataset/sample_deletion_requests.csv`, rows are two-digit padded (`case_01` to `case_32`), where natural and lexical order coincide.

### 1.3 Allowed `deletion_status` Values
*Source: `problem_statement.md` Lines 70, 91-97*
- `COMPLETE`: Deletion is fully verified at `audit_at`.
  - Contains **only** `VERIFICATION` steps.
  - Every step must have a non-empty `evidence_id` citing proof captured on or before `audit_at`.
- `INCOMPLETE`: Unremediated data or active recreation risks remain at `audit_at`.
  - Must have at least 1 `FINDING` step.
  - Contains findings, complete ordered remediation plan, and post-remediation verification checks.
  - Remediation and future verification steps have `evidence_id = ""`.
- `NOT_APPLICABLE`: The request did not authorize deletion (e.g. data access, export, opt-out).
  - Must have `steps_json = []` (empty JSON array).

---

## 2. Step Object Specification

*Source: `problem_statement.md` Lines 77-87*

Each object in the `steps_json` array contains exactly these 7 fields (no missing fields, no extra fields):

```json
{
  "step_no": 1,
  "phase": "FINDING",
  "system_id": "account_service",
  "resource_id": "account_005",
  "operation": "REPORT_REMAINING_RECORD",
  "state": "PRESENT",
  "evidence_id": "evidence_01"
}
```

| Field Name | Type | Allowed Values / Constraints |
|---|---|---|
| `step_no` | integer | Strictly sequential 1..N starting at 1 with no gaps. |
| `phase` | string | `FINDING`, `REMEDIATION`, `VERIFICATION` (strictly monotonic). |
| `system_id` | string | System identifier (e.g., `account_service`, `security_service`). |
| `resource_id` | string | Target resource identifier. |
| `operation` | string | One of the 15 allowed operations listed in §3. |
| `state` | string | Exactly the legal state mapped to the operation in §3. |
| `evidence_id` | string | Empty `""` or existing `file_id` in `dataset/evidence_files.csv` captured `<= audit_at`. |

---

## 3. Allowed Operations, Legal States, and Ordering

*Source: `problem_statement.md` Lines 103-120, 126*

Phases must appear in strict order: `FINDING` < `REMEDIATION` < `VERIFICATION`.
Within each phase, steps are ordered by:
1. Operation order as defined in the table below;
2. `system_id` ascending;
3. `resource_id` ascending.

| Phase | Operation | State | Meaning |
|---|---|---|---|
| `FINDING` | `REPORT_REMAINING_RECORD` | `PRESENT` | A record that should have been deleted still exists. |
| `FINDING` | `REPORT_EXPOSED_PII` | `PRESENT` | A record may remain, but it still contains identifiers that should have been redacted or anonymized. |
| `FINDING` | `REPORT_ACTIVE_DATA_FLOW` | `ACTIVE` | An active process can copy or recreate the user's data. |
| `FINDING` | `REPORT_RESTORE_RISK` | `ACTIVE` | A backup or restore path can bring deleted data back. |
| `REMEDIATION` | `DISABLE_DATA_FLOW` | `DISABLED` | Stop the process that can copy or recreate the data. |
| `REMEDIATION` | `BLOCK_RESTORE` | `BLOCKED` | Prevent the affected backup from restoring the user's data. |
| `REMEDIATION` | `DELETE_RECORD` | `ABSENT` | Remove the entire record. |
| `REMEDIATION` | `REDACT_RECORD` | `REDACTED` | Keep the record but remove the identifying fields required by policy. |
| `REMEDIATION` | `ANONYMIZE_RECORD` | `ANONYMIZED` | Keep the record after irreversibly unlinking it from the user. |
| `VERIFICATION` | `VERIFY_RECORD_ABSENT` | `ABSENT` | Confirm that a record no longer exists. |
| `VERIFICATION` | `VERIFY_RECORD_PRESENT` | `PRESENT` | Confirm that a policy-required retained record still exists. |
| `VERIFICATION` | `VERIFY_RECORD_REDACTED` | `REDACTED` | Confirm that required identifying fields have been removed. |
| `VERIFICATION` | `VERIFY_RECORD_ANONYMIZED` | `ANONYMIZED` | Confirm that the record can no longer be linked to the user. |
| `VERIFICATION` | `VERIFY_DATA_FLOW_DISABLED` | `DISABLED` | Confirm that the relevant data flow is inactive. |
| `VERIFICATION` | `VERIFY_RESTORE_BLOCKED` | `BLOCKED` | Confirm that the affected data cannot be restored. |

---

## 4. Operation Pairing / Triad Chains (Conventions)

Inferred from `problem_statement.md` rules and verified across the 32 samples in `dataset/sample_output.csv`:

| Finding Operation | Remediation Operation | Verification Operation |
|---|---|---|
| `REPORT_ACTIVE_DATA_FLOW` | `DISABLE_DATA_FLOW` | `VERIFY_DATA_FLOW_DISABLED` |
| `REPORT_RESTORE_RISK` | `BLOCK_RESTORE` | `VERIFY_RESTORE_BLOCKED` |
| `REPORT_REMAINING_RECORD` | `DELETE_RECORD` | `VERIFY_RECORD_ABSENT` |
| `REPORT_EXPOSED_PII` | `REDACT_RECORD` | `VERIFY_RECORD_REDACTED` |
| `REPORT_EXPOSED_PII` | `ANONYMIZE_RECORD` | `VERIFY_RECORD_ANONYMIZED` |

*Note on Retained Records*: `VERIFY_RECORD_PRESENT` verifies that policy-mandated records (e.g. `SECURITY_AUDIT_LOG`) remain present and intact. Because retaining required records is compliant, there is no corresponding `FINDING` or `REMEDIATION` step.

---

## 5. Header and Sample Data Rows

### 5.1 `dataset/deletion_requests.csv`
```text
Header: ['case_id', 'email', 'requested_at', 'reported_status', 'reported_at', 'audit_at', 'request_text']
Row 1: ['case_33', 'ingrid.dahl@outlook.com', '2026-07-16T08:00:00Z', 'COMPLETE', '2026-07-18T02:00:00Z', '2026-07-19T13:00:00Z', 'Please close my account and process the associated personal-data deletion...']
Row 2: ['case_34', 'haruka.s1838@zoho.com', '2026-09-24T08:00:00Z', 'COMPLETE', '2026-09-26T02:00:00Z', '2026-09-27T13:00:00Z', 'I would like the account associated with this address to be erased...']
Row 3: ['case_35', 'g.silva76@gmail.com', '2026-08-30T03:00:00Z', 'NOT_STARTED', '2026-08-31T21:00:00Z', '2026-09-02T08:00:00Z', 'Please close my account and process the associated personal-data deletion...']
```

### 5.2 `dataset/sample_deletion_requests.csv`
```text
Header: ['case_id', 'email', 'requested_at', 'reported_status', 'reported_at', 'audit_at', 'request_text']
Row 1: ['case_01', 'amina.elmasri@gmail.com', '2026-08-18T09:14:00Z', 'COMPLETE', '2026-08-20T16:42:00Z', '2026-09-03T11:30:00Z', 'Hi, I haven’t used this account in years and would like it closed...']
Row 2: ['case_02', 'mateo.rios@outlook.com', '2026-08-21T18:06:00Z', 'PARTIALLY_COMPLETE', '2026-08-22T07:25:00Z', '2026-09-04T15:00:00Z', 'Intenté eliminar mi cuenta ayer, pero la página terminó mostrando un error...']
Row 3: ['case_03', 'l.fontaine46@yahoo.com', '2026-09-13T11:00:00Z', 'COMPLETE', '2026-09-15T11:00:00Z', '2026-09-26T11:00:00Z', 'Je demande la suppression définitive du compte associé à cette adresse e-mail...']
```

### 5.3 `dataset/evidence_files.csv`
```text
Header: ['file_id', 'file_path', 'origin', 'captured_at']
Row 1: ['evidence_01', 'evidence/logs/service_events_ap_south_20260915.log', 'central_observability_export', '2026-09-15T11:59:39Z']
Row 2: ['evidence_02', 'evidence/records/customer_data_snapshot_bundle_20260917.json', 'records_assurance_snapshot_bundle', '2026-09-17T12:00:00Z']
Row 3: ['evidence_03', 'evidence/records/customer_account_handover_20261001.txt', 'customer_account_service', '2026-10-01T12:00:00Z']
```

### 5.4 `dataset/sample_output.csv`
```text
Header: ['case_id', 'deletion_status', 'steps_json']
Row 1: ['case_01', 'COMPLETE', '[{"evidence_id":"evidence_54","operation":"VERIFY_RECORD_ABSENT","phase":"VERIFICATION","resource_id":"account_001","state":"ABSENT","step_no":1,"system_id":"account_service"}]']
Row 2: ['case_02', 'COMPLETE', '[{"evidence_id":"evidence_54","operation":"VERIFY_RECORD_ABSENT","phase":"VERIFICATION","resource_id":"account_002","state":"ABSENT","step_no":1,"system_id":"account_service"}]']
Row 3: ['case_03', 'COMPLETE', '[{"step_no":1,"phase":"VERIFICATION","system_id":"account_service","resource_id":"account_7566","operation":"VERIFY_RECORD_ABSENT","state":"ABSENT","evidence_id":"evidence_94"},{"step_no":2,"phase":"VERIFICATION","system_id":"security_service","resource_id":"audit_record_2016","operation":"VERIFY_RECORD_PRESENT","state":"PRESENT","evidence_id":"evidence_94"},{"step_no":3,"phase":"VERIFICATION","system_id":"analytics_platform","resource_id":"analytics_9406","operation":"VERIFY_RECORD_ANONYMIZED","state":"ANONYMIZED","evidence_id":"evidence_94"}]']
```

---

## 6. Ambiguities & Convention Decisions

Any rule not strictly required by `problem_statement.md` is treated as a `WARN`, never an `ERROR`.

1. **Case ID and Resource ID Sorting (Lexical vs Natural)**:
   - `problem_statement.md` line 73 requires rows "sorted by `case_id`".
   - In `dataset/sample_output.csv`, case IDs have fixed 2-digit padding (`case_01`..`case_32`), making lexical and natural sorting identical.
   - Across all 32 samples, no two steps share the same `(phase, operation, system_id)`, so no sample step decides between lexical and natural resource ID ordering.
   - In `dataset/deletion_requests.csv`, case IDs span `case_33` to `case_550` without padding, which is in natural order.
   - *Decision*: Support both `--id-sort lexical` and `--id-sort natural` in `validate.py`, defaulting to `lexical` as specified by prompt.
2. **Matching Chain for Retained Records**:
   - `VERIFY_RECORD_PRESENT` steps are verification checks confirming retained compliance, not remediations of prior violations. Rule W02 therefore verifies that every `FINDING` has a `REMEDIATION` and every `REMEDIATION` has a `VERIFICATION`, without requiring `VERIFY_RECORD_PRESENT` to have a predecessor.
3. **Deriving Policy Retention (W05)**:
   - `deletion_rules.csv` specifies rules by category (`SECURITY_AUDIT_LOG`, `LEGAL_HOLD_RECORD`, `BACKUP_ARCHIVE`).
   - If a step's category cannot be unambiguously deduced from `system_id` and `resource_id` alone, W05 skips the check and logs `SKIPPED` rather than generating false warnings.
4. **Account Tombstone Verification (W06)**:
   - For an INCOMPLETE case, verification should include `system_id="account_service"` with `operation="VERIFY_RECORD_ABSENT"`. If the operation or account record is absent, W06 warns.

---

## 7. Developer Notes: How to Run Checks

Run all validation, testing, and integrity checks from the repository root:

```bash
# 1. Run all checks end-to-end (unit tests, validation, evaluation, log check)
python tools/run_checks.py

# 2. Run output validator on sample ground truth
python -m ghost_audit.validate \
  --output dataset/sample_output.csv \
  --requests dataset/sample_deletion_requests.csv \
  --manifest dataset/evidence_files.csv \
  --expected-rows 32 \
  --id-sort lexical

# 3. Run validator mutation tests
python -m unittest tests/test_validate_mutations.py

# 4. Run validator unit tests
python -m unittest tests/test_validate.py

# 5. Run evaluation metrics on samples vs samples
python code/evaluation/main.py \
  --pred dataset/sample_output.csv \
  --truth dataset/sample_output.csv \
  --requests dataset/sample_deletion_requests.csv \
  --out code/evaluation/evaluation_report.md

# 6. Run metamorphic tests
python -m unittest tests/test_metamorphic.py

# 7. Check chat transcript log integrity
python tools/check_log.py
```
