# Phase 4 Step 0: Measurement & Error Diagnosis

## 1. Baseline Evaluation Report (Samples)

- **Cases Evaluated**: 32
- **Case Status Accuracy**: 1.0000 (32 / 32 cases correct)
- **Row Exact-Match Rate**: 0.9375 (30 / 32 cases identical)
- **Step Multiset Micro F1**: 0.9948 (Micro Precision: 1.0000, Micro Recall: 0.9896)
- **Step Multiset Macro F1**: 0.9968 (Macro Precision: 1.0000, Macro Recall: 0.9939)
- **Sequence Exact-Order Rate**: 0.9375 (30 / 32 exact sequence match)
- **Sequence Mean LCS Ratio**: 0.9968
- **Truth Steps Aligned**: 191 / 193 (Coverage: 0.9896)
- **Pred Steps Aligned**: 191 / 191 (Coverage: 1.0000)

### Field-Level Accuracy on Aligned Steps
- `phase`: 1.0000 (191 / 191)
- `operation`: 1.0000 (191 / 191)
- `system_id`: 1.0000 (191 / 191)
- `resource_id`: 1.0000 (191 / 191)
- `state`: 1.0000 (191 / 191)
- `evidence_id`: 1.0000 (191 / 191)
- `step_no`: 0.9791 (187 / 191)

---

## 2. Non-Exact Match Cases Analysis

### `case_18`
- **Truth Status**: `INCOMPLETE` | **Pred Status**: `INCOMPLETE`
- **First Differing Step**: Step 11
- **Expected Step**: `{"step_no": 11, "phase": "VERIFICATION", "system_id": "security_service", "resource_id": "audit_record_6645", "operation": "VERIFY_RECORD_PRESENT", "state": "PRESENT", "evidence_id": ""}`
- **Predicted Step**: `{"step_no": 11, "phase": "VERIFICATION", "system_id": "support_platform", "resource_id": "support_5569", "operation": "VERIFY_RECORD_REDACTED", "state": "REDACTED", "evidence_id": ""}`
- **One-line Cause**: `missing`: Expected `VERIFY_RECORD_PRESENT` for `security_service` audit log (`audit_record_6645`), which was omitted because the audit record was not captured in citable evidence.
- **Error Category**: Missing verification step for uncaptured audit log.

### `case_20`
- **Truth Status**: `INCOMPLETE` | **Pred Status**: `INCOMPLETE`
- **First Differing Step**: Step 7
- **Expected Step**: `{"step_no": 7, "phase": "VERIFICATION", "system_id": "security_service", "resource_id": "audit_record_5569", "operation": "VERIFY_RECORD_PRESENT", "state": "PRESENT", "evidence_id": ""}`
- **Predicted Step**: `{"step_no": 7, "phase": "VERIFICATION", "system_id": "integration_service", "resource_id": "data_flow_1770", "operation": "VERIFY_DATA_FLOW_DISABLED", "state": "DISABLED", "evidence_id": ""}`
- **One-line Cause**: `missing`: Expected `VERIFY_RECORD_PRESENT` for `security_service` audit log (`audit_record_5569`), which was omitted because the audit record was not captured in citable evidence.
- **Error Category**: Missing verification step for uncaptured audit log.

---

## 3. Errors Grouped by Module

| Module | Error Count | Impacted Cases | Root Cause Summary |
|---|---|---|---|
| **Identity** (`ghost_audit.identity`) | 0 | None | All 32 request emails resolved to unique, correct `user_id`s. |
| **Linkage** (`ghost_audit.linker`) | 0 | None | 109/109 sample resources correctly linked with 100% precision. |
| **State** (`ghost_audit.state`) | 0 | None | Presence and absence accurately determined across all covering and non-covering files. |
| **Rules** (`ghost_audit.rules`) | 0 | None | Rule evaluations and category treatments conform to policy. |
| **Emit / Planner** (`ghost_audit.planner`, `emit`) | 2 | `case_18`, `case_20` | `planner.py` only emits a verification step for `security_service` when an audit record already exists in `treatments`. For incomplete cases where the audit record was not yet generated/captured at audit time, a pending verification step with `evidence_id=""` was omitted. |
| **Citation** (`ghost_audit.citation`) | 0 | None | All 191 aligned steps have 100% accurate `evidence_id`s against sample ground truth. |
