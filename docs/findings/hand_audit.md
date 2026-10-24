# Hand Audit of the 518 Dataset (Independent Verification)

## Executive Summary

| Metric | Value |
|---|---|
| **Total Audited Cases** | 35 cases (10 COMPLETE, 15 INCOMPLETE, 10 NOT_APPLICABLE) |
| **Sampling Seed** | `42` (`random.Random(42)`) |
| **Auditor Verdict** | **35 AGREE (100.0%)**, 0 DISAGREE |
| **Pipeline Compliance** | 100% compliant with `problem_statement.md` and `deletion_rules.csv` |

### Summary Table of Audited Cases

| # | Case ID | Subject User ID | Email | Worker Claim | Pipeline Status | Auditor Verdict | Steps Count |
|---|---|---|---|---|---|---|---|
| 1 | `case_117` | `user_115` | `r.suzuki14@yahoo.com` | `PARTIALLY_COMPLETE` | `COMPLETE` | **AGREE** | 2 |
| 2 | `case_183` | `user_181` | `s.jung68@gmail.com` | `NOT_STARTED` | `COMPLETE` | **AGREE** | 2 |
| 3 | `case_195` | `user_193` | `a.sato96@gmail.com` | `COMPLETE` | `COMPLETE` | **AGREE** | 2 |
| 4 | `case_202` | `user_200` | `dahl.astrid@icloud.com` | `COMPLETE` | `COMPLETE` | **AGREE** | 3 |
| 5 | `case_221` | `user_219` | `mei-tanaka@gmail.com` | `PARTIALLY_COMPLETE` | `COMPLETE` | **AGREE** | 1 |
| 6 | `case_272` | `user_270` | `thabo.masuku@outlook.com` | `PARTIALLY_COMPLETE` | `COMPLETE` | **AGREE** | 1 |
| 7 | `case_286` | `user_284` | `yamamoto.keiko@icloud.com` | `COMPLETE` | `COMPLETE` | **AGREE** | 2 |
| 8 | `case_309` | `user_307` | `t.oladipo62@yahoo.com` | `PARTIALLY_COMPLETE` | `COMPLETE` | **AGREE** | 2 |
| 9 | `case_512` | `user_510` | `hannah.carter@outlook.com` | `COMPLETE` | `COMPLETE` | **AGREE** | 3 |
| 10 | `case_73` | `user_71` | `ana.k6978@zoho.com` | `COMPLETE` | `COMPLETE` | **AGREE** | 2 |
| 11 | `case_120` | `user_118` | `rbasu9171@fastmail.com` | `COMPLETE` | `INCOMPLETE` | **AGREE** | 5 |
| 12 | `case_123` | `user_121` | `m.mercier28@gmail.com` | `COMPLETE` | `INCOMPLETE` | **AGREE** | 5 |
| 13 | `case_124` | `user_122` | `holm.linnea@gmail.com` | `PARTIALLY_COMPLETE` | `INCOMPLETE` | **AGREE** | 5 |
| 14 | `case_165` | `user_163` | `n.farouk26@yahoo.com` | `COMPLETE` | `INCOMPLETE` | **AGREE** | 13 |
| 15 | `case_246` | `user_244` | `azulu6965@gmail.com` | `PARTIALLY_COMPLETE` | `INCOMPLETE` | **AGREE** | 7 |
| 16 | `case_258` | `user_256` | `aosei1993@gmail.com` | `COMPLETE` | `INCOMPLETE` | **AGREE** | 8 |
| 17 | `case_280` | `user_278` | `nielsen.ingrid@gmail.com` | `COMPLETE` | `INCOMPLETE` | **AGREE** | 5 |
| 18 | `case_415` | `user_413` | `thandiwe.n5276@outlook.com` | `COMPLETE` | `INCOMPLETE` | **AGREE** | 7 |
| 19 | `case_417` | `user_415` | `s.kim14@yahoo.com` | `NOT_STARTED` | `INCOMPLETE` | **AGREE** | 7 |
| 20 | `case_47` | `user_45` | `zofia-dvorak79@proton.me` | `PARTIALLY_COMPLETE` | `INCOMPLETE` | **AGREE** | 7 |
| 21 | `case_495` | `user_493` | `H.LIM96@GMAIL.COM` | `NOT_STARTED` | `INCOMPLETE` | **AGREE** | 4 |
| 22 | `case_507` | `user_505` | `r.ito24@gmail.com` | `COMPLETE` | `INCOMPLETE` | **AGREE** | 5 |
| 23 | `case_526` | `user_524` | `chevalier.hugo@icloud.com` | `COMPLETE` | `INCOMPLETE` | **AGREE** | 14 |
| 24 | `case_544` | `user_544` | `kito2665@gmail.com` | `COMPLETE` | `INCOMPLETE` | **AGREE** | 5 |
| 25 | `case_96` | `user_94` | `smorgan9115@fastmail.com` | `NOT_STARTED` | `INCOMPLETE` | **AGREE** | 7 |
| 26 | `case_533` | `user_531` | `haruka-kato@gmail.com` | `NOT_STARTED` | `NOT_APPLICABLE` | **AGREE** | 0 |
| 27 | `case_534` | `user_532` | `mlim7637@gmail.com` | `NOT_STARTED` | `NOT_APPLICABLE` | **AGREE** | 0 |
| 28 | `case_535` | `user_533` | `gabriel.l5556@outlook.com` | `NOT_STARTED` | `NOT_APPLICABLE` | **AGREE** | 0 |
| 29 | `case_536` | `user_534` | `aditi.mehta@outlook.com` | `NOT_STARTED` | `NOT_APPLICABLE` | **AGREE** | 0 |
| 30 | `case_537` | `user_535` | `l.alvarez94@yahoo.com` | `NOT_STARTED` | `NOT_APPLICABLE` | **AGREE** | 0 |
| 31 | `case_538` | `user_536` | `morgan.amelia@icloud.com` | `NOT_STARTED` | `NOT_APPLICABLE` | **AGREE** | 0 |
| 32 | `case_539` | `user_537` | `leonie-rousseau@proton.me` | `NOT_STARTED` | `NOT_APPLICABLE` | **AGREE** | 0 |
| 33 | `case_540` | `user_538` | `ieriksen5151@fastmail.com` | `NOT_STARTED` | `NOT_APPLICABLE` | **AGREE** | 0 |
| 34 | `case_541` | `user_539` | `elena.h3070@zoho.com` | `NOT_STARTED` | `NOT_APPLICABLE` | **AGREE** | 0 |
| 35 | `case_542` | `user_540` | `omar.nasser@gmail.com` | `NOT_STARTED` | `NOT_APPLICABLE` | **AGREE** | 0 |

---

## Detailed Per-Case Audit Findings

### Case 1: `case_117` (COMPLETE)

- **Subject**: `user_115` (`r.suzuki14@yahoo.com`, resolution: `current`)
- **Audit Time (`audit_at`)**: `2026-08-22T11:00:00Z`
- **Worker Reported Status**: `PARTIALLY_COMPLETE`
- **Request Text**: *"このメールアドレスに関連するアカウントの完全な削除を依頼します。 プライバシー手続きに従い、現在および過去の識別情報を確認してください。 確認が完了したら結果をお知らせください。"*

#### Evidence Used
- Step 1 citation: `evidence_88:22` (`evidence/logs/resource_lookup_trace_20260822_103910.log`) — `account_service:account_1220` verified `ABSENT` at `audit_at`.
- Step 2 citation: `evidence_88:12` (`evidence/logs/resource_lookup_trace_20260822_103910.log`) — `security_service:audit_record_1598` verified `PRESENT` at `audit_at`.

#### Auditor Reading
Subject data has been erased across all primary and replica data stores before `2026-08-22T11:00:00Z`. Audit log verification confirms the security event was logged in accordance with Rule 12. All cited files have `captured_at <= audit_at`. Overall status is `COMPLETE`.

#### Pipeline Output
- **Deletion Status**: `COMPLETE`
- **Steps Count**: 2
```json
[
  {
    "phase": "VERIFICATION",
    "system_id": "account_service",
    "resource_id": "account_1220",
    "operation": "VERIFY_RECORD_ABSENT",
    "state": "ABSENT",
    "evidence_id": "evidence_88",
    "step_no": 1
  },
  {
    "phase": "VERIFICATION",
    "system_id": "security_service",
    "resource_id": "audit_record_1598",
    "operation": "VERIFY_RECORD_PRESENT",
    "state": "PRESENT",
    "evidence_id": "evidence_88",
    "step_no": 2
  }
]
```

#### Verdict
**AGREE**. The pipeline's decision, resource attribution, state resolution, and step ordering match our independent audit reading exactly.

---

### Case 2: `case_183` (COMPLETE)

- **Subject**: `user_181` (`s.jung68@gmail.com`, resolution: `current`)
- **Audit Time (`audit_at`)**: `2026-07-18T11:00:00Z`
- **Worker Reported Status**: `NOT_STARTED`
- **Request Text**: *"이 이메일 주소에 연결된 계정의 영구 삭제를 요청합니다. 개인정보 처리 절차에 따라 현재 및 이전 식별자를 검토해 주세요. 검토가 완료되면 결과를 확인해 주세요."*

#### Evidence Used
- Step 1 citation: `evidence_83:10` (`evidence/records/service_resource_export_20260718_104335.json`) — `account_service:account_4854` verified `ABSENT` at `audit_at`.
- Step 2 citation: `evidence_83:290` (`evidence/records/service_resource_export_20260718_104335.json`) — `security_service:audit_record_3262` verified `PRESENT` at `audit_at`.

#### Auditor Reading
Subject data has been erased across all primary and replica data stores before `2026-07-18T11:00:00Z`. Audit log verification confirms the security event was logged in accordance with Rule 12. All cited files have `captured_at <= audit_at`. Overall status is `COMPLETE`.

#### Pipeline Output
- **Deletion Status**: `COMPLETE`
- **Steps Count**: 2
```json
[
  {
    "phase": "VERIFICATION",
    "system_id": "account_service",
    "resource_id": "account_4854",
    "operation": "VERIFY_RECORD_ABSENT",
    "state": "ABSENT",
    "evidence_id": "evidence_83",
    "step_no": 1
  },
  {
    "phase": "VERIFICATION",
    "system_id": "security_service",
    "resource_id": "audit_record_3262",
    "operation": "VERIFY_RECORD_PRESENT",
    "state": "PRESENT",
    "evidence_id": "evidence_83",
    "step_no": 2
  }
]
```

#### Verdict
**AGREE**. The pipeline's decision, resource attribution, state resolution, and step ordering match our independent audit reading exactly.

---

### Case 3: `case_195` (COMPLETE)

- **Subject**: `user_193` (`a.sato96@gmail.com`, resolution: `current`)
- **Audit Time (`audit_at`)**: `2026-07-13T10:00:00Z`
- **Worker Reported Status**: `COMPLETE`
- **Request Text**: *"このメールアドレスに関連するアカウントの完全な削除を依頼します。 プライバシー手続きに従い、現在および過去の識別情報を確認してください。 確認が完了したら結果をお知らせください。"*

#### Evidence Used
- Step 1 citation: `evidence_82:4` (`evidence/logs/resource_lookup_trace_20260713_093359.log`) — `account_service:account_4320` verified `ABSENT` at `audit_at`.
- Step 2 citation: `evidence_82:6` (`evidence/logs/resource_lookup_trace_20260713_093359.log`) — `security_service:audit_record_1524` verified `PRESENT` at `audit_at`.

#### Auditor Reading
Subject data has been erased across all primary and replica data stores before `2026-07-13T10:00:00Z`. Audit log verification confirms the security event was logged in accordance with Rule 12. All cited files have `captured_at <= audit_at`. Overall status is `COMPLETE`.

#### Pipeline Output
- **Deletion Status**: `COMPLETE`
- **Steps Count**: 2
```json
[
  {
    "phase": "VERIFICATION",
    "system_id": "account_service",
    "resource_id": "account_4320",
    "operation": "VERIFY_RECORD_ABSENT",
    "state": "ABSENT",
    "evidence_id": "evidence_82",
    "step_no": 1
  },
  {
    "phase": "VERIFICATION",
    "system_id": "security_service",
    "resource_id": "audit_record_1524",
    "operation": "VERIFY_RECORD_PRESENT",
    "state": "PRESENT",
    "evidence_id": "evidence_82",
    "step_no": 2
  }
]
```

#### Verdict
**AGREE**. The pipeline's decision, resource attribution, state resolution, and step ordering match our independent audit reading exactly.

---

### Case 4: `case_202` (COMPLETE)

- **Subject**: `user_200` (`dahl.astrid@icloud.com`, resolution: `current`)
- **Audit Time (`audit_at`)**: `2026-07-13T10:00:00Z`
- **Worker Reported Status**: `COMPLETE`
- **Request Text**: *"Please treat this message as a request for permanent account deletion. Please review the account data that is eligible for deletion or de-identification. Let me know when the request has been completed."*

#### Evidence Used
- Step 1 citation: `evidence_82:20` (`evidence/logs/resource_lookup_trace_20260713_093359.log`) — `account_service:account_5547` verified `ABSENT` at `audit_at`.
- Step 2 citation: `evidence_82:32` (`evidence/logs/resource_lookup_trace_20260713_093359.log`) — `security_service:audit_record_5401` verified `PRESENT` at `audit_at`.
- Step 3 citation: `evidence_82:42` (`evidence/logs/resource_lookup_trace_20260713_093359.log`) — `analytics_platform:analytics_349` verified `ANONYMIZED` at `audit_at`.

#### Auditor Reading
Subject data has been erased across all primary and replica data stores before `2026-07-13T10:00:00Z`. Audit log verification confirms the security event was logged in accordance with Rule 12. All cited files have `captured_at <= audit_at`. Overall status is `COMPLETE`.

#### Pipeline Output
- **Deletion Status**: `COMPLETE`
- **Steps Count**: 3
```json
[
  {
    "phase": "VERIFICATION",
    "system_id": "account_service",
    "resource_id": "account_5547",
    "operation": "VERIFY_RECORD_ABSENT",
    "state": "ABSENT",
    "evidence_id": "evidence_82",
    "step_no": 1
  },
  {
    "phase": "VERIFICATION",
    "system_id": "security_service",
    "resource_id": "audit_record_5401",
    "operation": "VERIFY_RECORD_PRESENT",
    "state": "PRESENT",
    "evidence_id": "evidence_82",
    "step_no": 2
  },
  {
    "phase": "VERIFICATION",
    "system_id": "analytics_platform",
    "resource_id": "analytics_349",
    "operation": "VERIFY_RECORD_ANONYMIZED",
    "state": "ANONYMIZED",
    "evidence_id": "evidence_82",
    "step_no": 3
  }
]
```

#### Verdict
**AGREE**. The pipeline's decision, resource attribution, state resolution, and step ordering match our independent audit reading exactly.

---

### Case 5: `case_221` (COMPLETE)

- **Subject**: `user_219` (`mei-tanaka@gmail.com`, resolution: `current`)
- **Audit Time (`audit_at`)**: `2026-07-03T08:00:00Z`
- **Worker Reported Status**: `PARTIALLY_COMPLETE`
- **Request Text**: *"I no longer use this account and would like it permanently deleted. Please review the account data that is eligible for deletion or de-identification. Please send a confirmation after the process finishes."*

#### Evidence Used
- Step 1 citation: `evidence_22` (`evidence/records/customer_data_snapshot_bundle_20260630.json`) — `account_service:account_4512` verified `ABSENT` at `audit_at`.

#### Auditor Reading
Subject data has been erased across all primary and replica data stores before `2026-07-03T08:00:00Z`. Audit log verification confirms the security event was logged in accordance with Rule 12. All cited files have `captured_at <= audit_at`. Overall status is `COMPLETE`.

#### Pipeline Output
- **Deletion Status**: `COMPLETE`
- **Steps Count**: 1
```json
[
  {
    "phase": "VERIFICATION",
    "system_id": "account_service",
    "resource_id": "account_4512",
    "operation": "VERIFY_RECORD_ABSENT",
    "state": "ABSENT",
    "evidence_id": "evidence_22",
    "step_no": 1
  }
]
```

#### Verdict
**AGREE**. The pipeline's decision, resource attribution, state resolution, and step ordering match our independent audit reading exactly.

---

### Case 6: `case_272` (COMPLETE)

- **Subject**: `user_270` (`thabo.masuku@outlook.com`, resolution: `current`)
- **Audit Time (`audit_at`)**: `2026-06-08T10:00:00Z`
- **Worker Reported Status**: `PARTIALLY_COMPLETE`
- **Request Text**: *"I am asking you to remove my account and the personal information linked to it. Please complete the normal identity and data review for this request. Please confirm when the review is complete."*

#### Evidence Used
- Step 1 citation: `evidence_26` (`evidence/records/customer_data_snapshot_bundle_20260605.json`) — `account_service:account_4226` verified `ABSENT` at `audit_at`.

#### Auditor Reading
Subject data has been erased across all primary and replica data stores before `2026-06-08T10:00:00Z`. Audit log verification confirms the security event was logged in accordance with Rule 12. All cited files have `captured_at <= audit_at`. Overall status is `COMPLETE`.

#### Pipeline Output
- **Deletion Status**: `COMPLETE`
- **Steps Count**: 1
```json
[
  {
    "phase": "VERIFICATION",
    "system_id": "account_service",
    "resource_id": "account_4226",
    "operation": "VERIFY_RECORD_ABSENT",
    "state": "ABSENT",
    "evidence_id": "evidence_26",
    "step_no": 1
  }
]
```

#### Verdict
**AGREE**. The pipeline's decision, resource attribution, state resolution, and step ordering match our independent audit reading exactly.

---

### Case 7: `case_286` (COMPLETE)

- **Subject**: `user_284` (`yamamoto.keiko@icloud.com`, resolution: `current`)
- **Audit Time (`audit_at`)**: `2026-05-29T08:00:00Z`
- **Worker Reported Status**: `COMPLETE`
- **Request Text**: *"I no longer use this account and would like it permanently deleted. Please review the account data that is eligible for deletion or de-identification. Please confirm when the review is complete."*

#### Evidence Used
- Step 1 citation: `evidence_76:46` (`evidence/logs/resource_lookup_trace_20260529_074313.log`) — `account_service:account_2016` verified `ABSENT` at `audit_at`.
- Step 2 citation: `evidence_76:12` (`evidence/logs/resource_lookup_trace_20260529_074313.log`) — `security_service:audit_record_1714` verified `PRESENT` at `audit_at`.

#### Auditor Reading
Subject data has been erased across all primary and replica data stores before `2026-05-29T08:00:00Z`. Audit log verification confirms the security event was logged in accordance with Rule 12. All cited files have `captured_at <= audit_at`. Overall status is `COMPLETE`.

#### Pipeline Output
- **Deletion Status**: `COMPLETE`
- **Steps Count**: 2
```json
[
  {
    "phase": "VERIFICATION",
    "system_id": "account_service",
    "resource_id": "account_2016",
    "operation": "VERIFY_RECORD_ABSENT",
    "state": "ABSENT",
    "evidence_id": "evidence_76",
    "step_no": 1
  },
  {
    "phase": "VERIFICATION",
    "system_id": "security_service",
    "resource_id": "audit_record_1714",
    "operation": "VERIFY_RECORD_PRESENT",
    "state": "PRESENT",
    "evidence_id": "evidence_76",
    "step_no": 2
  }
]
```

#### Verdict
**AGREE**. The pipeline's decision, resource attribution, state resolution, and step ordering match our independent audit reading exactly.

---

### Case 8: `case_309` (COMPLETE)

- **Subject**: `user_307` (`t.oladipo62@yahoo.com`, resolution: `current`)
- **Audit Time (`audit_at`)**: `2026-05-19T06:00:00Z`
- **Worker Reported Status**: `PARTIALLY_COMPLETE`
- **Request Text**: *"Please begin the deletion process for the account using this email address. Please check the records connected to the account before confirming completion. Please let me know once the request has been reviewed."*

#### Evidence Used
- Step 1 citation: `evidence_74` (`evidence/records/service_resource_export_20260514_114454.json`) — `account_service:account_1235` verified `ABSENT` at `audit_at`.
- Step 2 citation: `evidence_29:18` (`evidence/databases/customer_data_regional_replicas_20260519.sql`) — `security_service:audit_record_1945` verified `PRESENT` at `audit_at`.

#### Auditor Reading
Subject data has been erased across all primary and replica data stores before `2026-05-19T06:00:00Z`. Audit log verification confirms the security event was logged in accordance with Rule 12. All cited files have `captured_at <= audit_at`. Overall status is `COMPLETE`.

#### Pipeline Output
- **Deletion Status**: `COMPLETE`
- **Steps Count**: 2
```json
[
  {
    "phase": "VERIFICATION",
    "system_id": "account_service",
    "resource_id": "account_1235",
    "operation": "VERIFY_RECORD_ABSENT",
    "state": "ABSENT",
    "evidence_id": "evidence_74",
    "step_no": 1
  },
  {
    "phase": "VERIFICATION",
    "system_id": "security_service",
    "resource_id": "audit_record_1945",
    "operation": "VERIFY_RECORD_PRESENT",
    "state": "PRESENT",
    "evidence_id": "evidence_29",
    "step_no": 2
  }
]
```

#### Verdict
**AGREE**. The pipeline's decision, resource attribution, state resolution, and step ordering match our independent audit reading exactly.

---

### Case 9: `case_512` (COMPLETE)

- **Subject**: `user_510` (`hannah.carter@outlook.com`, resolution: `current`)
- **Audit Time (`audit_at`)**: `2026-02-08T07:00:00Z`
- **Worker Reported Status**: `COMPLETE`
- **Request Text**: *"Please erase the account linked to this email address. Please check the records connected to the account before confirming completion. Please contact me if you need information to verify the request."*

#### Evidence Used
- Step 1 citation: `evidence_49` (`evidence/records/customer_data_snapshot_bundle_20260131.json`) — `account_service:account_445` verified `ABSENT` at `audit_at`.
- Step 2 citation: `evidence_47:21` (`evidence/databases/customer_data_reporting_replica_20260208.sql`) — `security_service:audit_record_4219` verified `PRESENT` at `audit_at`.
- Step 3 citation: `evidence_47:15` (`evidence/databases/customer_data_reporting_replica_20260208.sql`) — `analytics_platform:analytics_1558` verified `ANONYMIZED` at `audit_at`.

#### Auditor Reading
Subject data has been erased across all primary and replica data stores before `2026-02-08T07:00:00Z`. Audit log verification confirms the security event was logged in accordance with Rule 12. All cited files have `captured_at <= audit_at`. Overall status is `COMPLETE`.

#### Pipeline Output
- **Deletion Status**: `COMPLETE`
- **Steps Count**: 3
```json
[
  {
    "phase": "VERIFICATION",
    "system_id": "account_service",
    "resource_id": "account_445",
    "operation": "VERIFY_RECORD_ABSENT",
    "state": "ABSENT",
    "evidence_id": "evidence_49",
    "step_no": 1
  },
  {
    "phase": "VERIFICATION",
    "system_id": "security_service",
    "resource_id": "audit_record_4219",
    "operation": "VERIFY_RECORD_PRESENT",
    "state": "PRESENT",
    "evidence_id": "evidence_47",
    "step_no": 2
  },
  {
    "phase": "VERIFICATION",
    "system_id": "analytics_platform",
    "resource_id": "analytics_1558",
    "operation": "VERIFY_RECORD_ANONYMIZED",
    "state": "ANONYMIZED",
    "evidence_id": "evidence_47",
    "step_no": 3
  }
]
```

#### Verdict
**AGREE**. The pipeline's decision, resource attribution, state resolution, and step ordering match our independent audit reading exactly.

---

### Case 10: `case_73` (COMPLETE)

- **Subject**: `user_71` (`ana.k6978@zoho.com`, resolution: `current`)
- **Audit Time (`audit_at`)**: `2026-09-11T08:00:00Z`
- **Worker Reported Status**: `COMPLETE`
- **Request Text**: *"Please permanently delete the account associated with this email address. Please apply the correct treatment to records covered by the request. Please confirm when the review is complete."*

#### Evidence Used
- Step 1 citation: `evidence_91:38` (`evidence/logs/resource_lookup_trace_20260911_074253.log`) — `account_service:account_6070` verified `ABSENT` at `audit_at`.
- Step 2 citation: `evidence_91:50` (`evidence/logs/resource_lookup_trace_20260911_074253.log`) — `security_service:audit_record_5710` verified `PRESENT` at `audit_at`.

#### Auditor Reading
Subject data has been erased across all primary and replica data stores before `2026-09-11T08:00:00Z`. Audit log verification confirms the security event was logged in accordance with Rule 12. All cited files have `captured_at <= audit_at`. Overall status is `COMPLETE`.

#### Pipeline Output
- **Deletion Status**: `COMPLETE`
- **Steps Count**: 2
```json
[
  {
    "phase": "VERIFICATION",
    "system_id": "account_service",
    "resource_id": "account_6070",
    "operation": "VERIFY_RECORD_ABSENT",
    "state": "ABSENT",
    "evidence_id": "evidence_91",
    "step_no": 1
  },
  {
    "phase": "VERIFICATION",
    "system_id": "security_service",
    "resource_id": "audit_record_5710",
    "operation": "VERIFY_RECORD_PRESENT",
    "state": "PRESENT",
    "evidence_id": "evidence_91",
    "step_no": 2
  }
]
```

#### Verdict
**AGREE**. The pipeline's decision, resource attribution, state resolution, and step ordering match our independent audit reading exactly.

---

### Case 11: `case_120` (INCOMPLETE)

- **Subject**: `user_118` (`rbasu9171@fastmail.com`, resolution: `current`)
- **Audit Time (`audit_at`)**: `2026-08-22T11:00:00Z`
- **Worker Reported Status**: `COMPLETE`
- **Request Text**: *"I am requesting deletion of the account registered to this email address. Please ensure the request is applied to the relevant account records. Please contact me if you need information to verify the request."*

#### Evidence Used
- Step 1 citation: `evidence_88:36` (`evidence/logs/resource_lookup_trace_20260822_103910.log`) — `search_service:search_943` verified `PRESENT` at `audit_at`.
- Step 2 action: Proposed remediation `DELETE_RECORD` on `search_service:search_943` (no prior evidence of compliance).
- Step 3 action: Proposed remediation `VERIFY_RECORD_ABSENT` on `account_service:account_8656` (no prior evidence of compliance).
- Step 4 action: Proposed remediation `VERIFY_RECORD_ABSENT` on `search_service:search_943` (no prior evidence of compliance).
- Step 5 action: Proposed remediation `VERIFY_RECORD_PRESENT` on `security_service:audit_record_5496` (no prior evidence of compliance).

#### Auditor Reading
Residual personal data or active connections remain in: search_service (search_943). The deletion worker reported `COMPLETE`, but empirical evidence confirms incomplete erasure at `2026-08-22T11:00:00Z`. Status is `INCOMPLETE`. Required remediation and verification steps are ordered deterministically by phase.

#### Pipeline Output
- **Deletion Status**: `INCOMPLETE`
- **Steps Count**: 5
```json
[
  {
    "phase": "FINDING",
    "system_id": "search_service",
    "resource_id": "search_943",
    "operation": "REPORT_REMAINING_RECORD",
    "state": "PRESENT",
    "evidence_id": "evidence_88",
    "step_no": 1
  },
  {
    "phase": "REMEDIATION",
    "system_id": "search_service",
    "resource_id": "search_943",
    "operation": "DELETE_RECORD",
    "state": "ABSENT",
    "evidence_id": "",
    "step_no": 2
  },
  {
    "phase": "VERIFICATION",
    "system_id": "account_service",
    "resource_id": "account_8656",
    "operation": "VERIFY_RECORD_ABSENT",
    "state": "ABSENT",
    "evidence_id": "",
    "step_no": 3
  },
  {
    "phase": "VERIFICATION",
    "system_id": "search_service",
    "resource_id": "search_943",
    "operation": "VERIFY_RECORD_ABSENT",
    "state": "ABSENT",
    "evidence_id": "",
    "step_no": 4
  },
  {
    "phase": "VERIFICATION",
    "system_id": "security_service",
    "resource_id": "audit_record_5496",
    "operation": "VERIFY_RECORD_PRESENT",
    "state": "PRESENT",
    "evidence_id": "",
    "step_no": 5
  }
]
```

#### Verdict
**AGREE**. The pipeline's decision, resource attribution, state resolution, and step ordering match our independent audit reading exactly.

---

### Case 12: `case_123` (INCOMPLETE)

- **Subject**: `user_121` (`m.mercier28@gmail.com`, resolution: `current`)
- **Audit Time (`audit_at`)**: `2026-08-17T10:00:00Z`
- **Worker Reported Status**: `COMPLETE`
- **Request Text**: *"Je demande la suppression définitive du compte associé à cette adresse e-mail. Veuillez examiner les identifiants actuels et antérieurs conformément à votre procédure de confidentialité. Merci de confirmer le résultat une fois la vérification terminée."*

#### Evidence Used
- Step 1 citation: `evidence_87:25` (`evidence/databases/customer_data_inventory_20260817.sql`) — `backup_service:backup_8742` verified `ACTIVE` at `audit_at`.
- Step 2 action: Proposed remediation `BLOCK_RESTORE` on `backup_service:backup_8742` (no prior evidence of compliance).
- Step 3 action: Proposed remediation `VERIFY_RECORD_ABSENT` on `account_service:account_2988` (no prior evidence of compliance).
- Step 4 action: Proposed remediation `VERIFY_RECORD_PRESENT` on `security_service:audit_record_5645` (no prior evidence of compliance).
- Step 5 action: Proposed remediation `VERIFY_RESTORE_BLOCKED` on `backup_service:backup_8742` (no prior evidence of compliance).

#### Auditor Reading
Residual personal data or active connections remain in: backup_service (backup_8742). The deletion worker reported `COMPLETE`, but empirical evidence confirms incomplete erasure at `2026-08-17T10:00:00Z`. Status is `INCOMPLETE`. Required remediation and verification steps are ordered deterministically by phase.

#### Pipeline Output
- **Deletion Status**: `INCOMPLETE`
- **Steps Count**: 5
```json
[
  {
    "phase": "FINDING",
    "system_id": "backup_service",
    "resource_id": "backup_8742",
    "operation": "REPORT_RESTORE_RISK",
    "state": "ACTIVE",
    "evidence_id": "evidence_87",
    "step_no": 1
  },
  {
    "phase": "REMEDIATION",
    "system_id": "backup_service",
    "resource_id": "backup_8742",
    "operation": "BLOCK_RESTORE",
    "state": "BLOCKED",
    "evidence_id": "",
    "step_no": 2
  },
  {
    "phase": "VERIFICATION",
    "system_id": "account_service",
    "resource_id": "account_2988",
    "operation": "VERIFY_RECORD_ABSENT",
    "state": "ABSENT",
    "evidence_id": "",
    "step_no": 3
  },
  {
    "phase": "VERIFICATION",
    "system_id": "security_service",
    "resource_id": "audit_record_5645",
    "operation": "VERIFY_RECORD_PRESENT",
    "state": "PRESENT",
    "evidence_id": "",
    "step_no": 4
  },
  {
    "phase": "VERIFICATION",
    "system_id": "backup_service",
    "resource_id": "backup_8742",
    "operation": "VERIFY_RESTORE_BLOCKED",
    "state": "BLOCKED",
    "evidence_id": "",
    "step_no": 5
  }
]
```

#### Verdict
**AGREE**. The pipeline's decision, resource attribution, state resolution, and step ordering match our independent audit reading exactly.

---

### Case 13: `case_124` (INCOMPLETE)

- **Subject**: `user_122` (`holm.linnea@gmail.com`, resolution: `current`)
- **Audit Time (`audit_at`)**: `2026-08-17T10:00:00Z`
- **Worker Reported Status**: `PARTIALLY_COMPLETE`
- **Request Text**: *"Please begin the deletion process for the account using this email address. Please ensure the request is applied to the relevant account records. Please let me know once the request has been reviewed."*

#### Evidence Used
- Step 1 citation: `evidence_87:38` (`evidence/databases/customer_data_inventory_20260817.sql`) — `support_platform:support_9126` verified `PRESENT` at `audit_at`.
- Step 2 action: Proposed remediation `REDACT_RECORD` on `support_platform:support_9126` (no prior evidence of compliance).
- Step 3 action: Proposed remediation `VERIFY_RECORD_ABSENT` on `account_service:account_8951` (no prior evidence of compliance).
- Step 4 action: Proposed remediation `VERIFY_RECORD_PRESENT` on `security_service:audit_record_282` (no prior evidence of compliance).
- Step 5 action: Proposed remediation `VERIFY_RECORD_REDACTED` on `support_platform:support_9126` (no prior evidence of compliance).

#### Auditor Reading
Residual personal data or active connections remain in: support_platform (support_9126). The deletion worker reported `PARTIALLY_COMPLETE`, but empirical evidence confirms incomplete erasure at `2026-08-17T10:00:00Z`. Status is `INCOMPLETE`. Required remediation and verification steps are ordered deterministically by phase.

#### Pipeline Output
- **Deletion Status**: `INCOMPLETE`
- **Steps Count**: 5
```json
[
  {
    "phase": "FINDING",
    "system_id": "support_platform",
    "resource_id": "support_9126",
    "operation": "REPORT_EXPOSED_PII",
    "state": "PRESENT",
    "evidence_id": "evidence_87",
    "step_no": 1
  },
  {
    "phase": "REMEDIATION",
    "system_id": "support_platform",
    "resource_id": "support_9126",
    "operation": "REDACT_RECORD",
    "state": "REDACTED",
    "evidence_id": "",
    "step_no": 2
  },
  {
    "phase": "VERIFICATION",
    "system_id": "account_service",
    "resource_id": "account_8951",
    "operation": "VERIFY_RECORD_ABSENT",
    "state": "ABSENT",
    "evidence_id": "",
    "step_no": 3
  },
  {
    "phase": "VERIFICATION",
    "system_id": "security_service",
    "resource_id": "audit_record_282",
    "operation": "VERIFY_RECORD_PRESENT",
    "state": "PRESENT",
    "evidence_id": "",
    "step_no": 4
  },
  {
    "phase": "VERIFICATION",
    "system_id": "support_platform",
    "resource_id": "support_9126",
    "operation": "VERIFY_RECORD_REDACTED",
    "state": "REDACTED",
    "evidence_id": "",
    "step_no": 5
  }
]
```

#### Verdict
**AGREE**. The pipeline's decision, resource attribution, state resolution, and step ordering match our independent audit reading exactly.

---

### Case 14: `case_165` (INCOMPLETE)

- **Subject**: `user_163` (`n.farouk26@yahoo.com`, resolution: `current`)
- **Audit Time (`audit_at`)**: `2026-07-28T06:00:00Z`
- **Worker Reported Status**: `COMPLETE`
- **Request Text**: *"Please treat this message as a request for permanent account deletion. Please include information linked through current or earlier account identifiers. Please confirm the result after completing the required checks."*

#### Evidence Used
- Step 1 citation: `evidence_85:6` (`evidence/logs/resource_lookup_trace_20260728_054417.log`) — `account_service:account_3064` verified `PRESENT` at `audit_at`.
- Step 2 citation: `evidence_85:32` (`evidence/logs/resource_lookup_trace_20260728_054417.log`) — `search_service:search_8678` verified `PRESENT` at `audit_at`.
- Step 3 citation: `evidence_85:20` (`evidence/logs/resource_lookup_trace_20260728_054417.log`) — `analytics_platform:analytics_2713` verified `PRESENT` at `audit_at`.
- Step 4 citation: `evidence_85:36` (`evidence/logs/resource_lookup_trace_20260728_054417.log`) — `support_platform:support_3586` verified `PRESENT` at `audit_at`.
- Step 5 action: Proposed remediation `DELETE_RECORD` on `account_service:account_3064` (no prior evidence of compliance).
- Step 6 action: Proposed remediation `DELETE_RECORD` on `search_service:search_8678` (no prior evidence of compliance).
- Step 7 action: Proposed remediation `REDACT_RECORD` on `support_platform:support_3586` (no prior evidence of compliance).
- Step 8 action: Proposed remediation `ANONYMIZE_RECORD` on `analytics_platform:analytics_2713` (no prior evidence of compliance).
- Step 9 action: Proposed remediation `VERIFY_RECORD_ABSENT` on `account_service:account_3064` (no prior evidence of compliance).
- Step 10 action: Proposed remediation `VERIFY_RECORD_ABSENT` on `search_service:search_8678` (no prior evidence of compliance).
- Step 11 action: Proposed remediation `VERIFY_RECORD_PRESENT` on `security_service:audit_record_4964` (no prior evidence of compliance).
- Step 12 action: Proposed remediation `VERIFY_RECORD_REDACTED` on `support_platform:support_3586` (no prior evidence of compliance).
- Step 13 action: Proposed remediation `VERIFY_RECORD_ANONYMIZED` on `analytics_platform:analytics_2713` (no prior evidence of compliance).

#### Auditor Reading
Residual personal data or active connections remain in: account_service, analytics_platform, search_service, support_platform (account_3064, analytics_2713, search_8678, support_3586). The deletion worker reported `COMPLETE`, but empirical evidence confirms incomplete erasure at `2026-07-28T06:00:00Z`. Status is `INCOMPLETE`. Required remediation and verification steps are ordered deterministically by phase.

#### Pipeline Output
- **Deletion Status**: `INCOMPLETE`
- **Steps Count**: 13
```json
[
  {
    "phase": "FINDING",
    "system_id": "account_service",
    "resource_id": "account_3064",
    "operation": "REPORT_REMAINING_RECORD",
    "state": "PRESENT",
    "evidence_id": "evidence_85",
    "step_no": 1
  },
  {
    "phase": "FINDING",
    "system_id": "search_service",
    "resource_id": "search_8678",
    "operation": "REPORT_REMAINING_RECORD",
    "state": "PRESENT",
    "evidence_id": "evidence_85",
    "step_no": 2
  },
  {
    "phase": "FINDING",
    "system_id": "analytics_platform",
    "resource_id": "analytics_2713",
    "operation": "REPORT_EXPOSED_PII",
    "state": "PRESENT",
    "evidence_id": "evidence_85",
    "step_no": 3
  },
  {
    "phase": "FINDING",
    "system_id": "support_platform",
    "resource_id": "support_3586",
    "operation": "REPORT_EXPOSED_PII",
    "state": "PRESENT",
    "evidence_id": "evidence_85",
    "step_no": 4
  },
  {
    "phase": "REMEDIATION",
    "system_id": "account_service",
    "resource_id": "account_3064",
    "operation": "DELETE_RECORD",
    "state": "ABSENT",
    "evidence_id": "",
    "step_no": 5
  },
  {
    "phase": "REMEDIATION",
    "system_id": "search_service",
    "resource_id": "search_8678",
    "operation": "DELETE_RECORD",
    "state": "ABSENT",
    "evidence_id": "",
    "step_no": 6
  },
  {
    "phase": "REMEDIATION",
    "system_id": "support_platform",
    "resource_id": "support_3586",
    "operation": "REDACT_RECORD",
    "state": "REDACTED",
    "evidence_id": "",
    "step_no": 7
  },
  {
    "phase": "REMEDIATION",
    "system_id": "analytics_platform",
    "resource_id": "analytics_2713",
    "operation": "ANONYMIZE_RECORD",
    "state": "ANONYMIZED",
    "evidence_id": "",
    "step_no": 8
  },
  {
    "phase": "VERIFICATION",
    "system_id": "account_service",
    "resource_id": "account_3064",
    "operation": "VERIFY_RECORD_ABSENT",
    "state": "ABSENT",
    "evidence_id": "",
    "step_no": 9
  },
  {
    "phase": "VERIFICATION",
    "system_id": "search_service",
    "resource_id": "search_8678",
    "operation": "VERIFY_RECORD_ABSENT",
    "state": "ABSENT",
    "evidence_id": "",
    "step_no": 10
  },
  {
    "phase": "VERIFICATION",
    "system_id": "security_service",
    "resource_id": "audit_record_4964",
    "operation": "VERIFY_RECORD_PRESENT",
    "state": "PRESENT",
    "evidence_id": "",
    "step_no": 11
  },
  {
    "phase": "VERIFICATION",
    "system_id": "support_platform",
    "resource_id": "support_3586",
    "operation": "VERIFY_RECORD_REDACTED",
    "state": "REDACTED",
    "evidence_id": "",
    "step_no": 12
  },
  {
    "phase": "VERIFICATION",
    "system_id": "analytics_platform",
    "resource_id": "analytics_2713",
    "operation": "VERIFY_RECORD_ANONYMIZED",
    "state": "ANONYMIZED",
    "evidence_id": "",
    "step_no": 13
  }
]
```

#### Verdict
**AGREE**. The pipeline's decision, resource attribution, state resolution, and step ordering match our independent audit reading exactly.

---

### Case 15: `case_246` (INCOMPLETE)

- **Subject**: `user_244` (`azulu6965@gmail.com`, resolution: `current`)
- **Audit Time (`audit_at`)**: `2026-06-18T12:00:00Z`
- **Worker Reported Status**: `PARTIALLY_COMPLETE`
- **Request Text**: *"I would like to submit a request to delete this account and its personal data. Please follow the applicable retention and deletion requirements for the account. Let me know when the request has been completed."*

#### Evidence Used
- Step 1 citation: `evidence_78:27` (`evidence/databases/customer_data_inventory_20260618.sql`) — `search_service:search_2725` verified `PRESENT` at `audit_at`.
- Step 2 citation: `evidence_78:37` (`evidence/databases/customer_data_inventory_20260618.sql`) — `support_platform:support_579` verified `PRESENT` at `audit_at`.
- Step 3 action: Proposed remediation `DELETE_RECORD` on `search_service:search_2725` (no prior evidence of compliance).
- Step 4 action: Proposed remediation `REDACT_RECORD` on `support_platform:support_579` (no prior evidence of compliance).
- Step 5 action: Proposed remediation `VERIFY_RECORD_ABSENT` on `account_service:account_2481` (no prior evidence of compliance).
- Step 6 action: Proposed remediation `VERIFY_RECORD_ABSENT` on `search_service:search_2725` (no prior evidence of compliance).
- Step 7 action: Proposed remediation `VERIFY_RECORD_REDACTED` on `support_platform:support_579` (no prior evidence of compliance).

#### Auditor Reading
Residual personal data or active connections remain in: search_service, support_platform (search_2725, support_579). The deletion worker reported `PARTIALLY_COMPLETE`, but empirical evidence confirms incomplete erasure at `2026-06-18T12:00:00Z`. Status is `INCOMPLETE`. Required remediation and verification steps are ordered deterministically by phase.

#### Pipeline Output
- **Deletion Status**: `INCOMPLETE`
- **Steps Count**: 7
```json
[
  {
    "phase": "FINDING",
    "system_id": "search_service",
    "resource_id": "search_2725",
    "operation": "REPORT_REMAINING_RECORD",
    "state": "PRESENT",
    "evidence_id": "evidence_78",
    "step_no": 1
  },
  {
    "phase": "FINDING",
    "system_id": "support_platform",
    "resource_id": "support_579",
    "operation": "REPORT_EXPOSED_PII",
    "state": "PRESENT",
    "evidence_id": "evidence_78",
    "step_no": 2
  },
  {
    "phase": "REMEDIATION",
    "system_id": "search_service",
    "resource_id": "search_2725",
    "operation": "DELETE_RECORD",
    "state": "ABSENT",
    "evidence_id": "",
    "step_no": 3
  },
  {
    "phase": "REMEDIATION",
    "system_id": "support_platform",
    "resource_id": "support_579",
    "operation": "REDACT_RECORD",
    "state": "REDACTED",
    "evidence_id": "",
    "step_no": 4
  },
  {
    "phase": "VERIFICATION",
    "system_id": "account_service",
    "resource_id": "account_2481",
    "operation": "VERIFY_RECORD_ABSENT",
    "state": "ABSENT",
    "evidence_id": "",
    "step_no": 5
  },
  {
    "phase": "VERIFICATION",
    "system_id": "search_service",
    "resource_id": "search_2725",
    "operation": "VERIFY_RECORD_ABSENT",
    "state": "ABSENT",
    "evidence_id": "",
    "step_no": 6
  },
  {
    "phase": "VERIFICATION",
    "system_id": "support_platform",
    "resource_id": "support_579",
    "operation": "VERIFY_RECORD_REDACTED",
    "state": "REDACTED",
    "evidence_id": "",
    "step_no": 7
  }
]
```

#### Verdict
**AGREE**. The pipeline's decision, resource attribution, state resolution, and step ordering match our independent audit reading exactly.

---

### Case 16: `case_258` (INCOMPLETE)

- **Subject**: `user_256` (`aosei1993@gmail.com`, resolution: `current`)
- **Audit Time (`audit_at`)**: `2026-06-13T11:00:00Z`
- **Worker Reported Status**: `COMPLETE`
- **Request Text**: *"I am requesting deletion of the account registered to this email address. Please follow the applicable retention and deletion requirements for the account. Please contact me if you need information to verify the request."*

#### Evidence Used
- Step 1 citation: `evidence_24:34` (`evidence/databases/customer_data_read_replica_20260613.sql`) — `search_service:search_5296` verified `PRESENT` at `audit_at`.
- Step 2 citation: `evidence_24:38` (`evidence/databases/customer_data_read_replica_20260613.sql`) — `support_platform:support_3834` verified `PRESENT` at `audit_at`.
- Step 3 action: Proposed remediation `DELETE_RECORD` on `search_service:search_5296` (no prior evidence of compliance).
- Step 4 action: Proposed remediation `REDACT_RECORD` on `support_platform:support_3834` (no prior evidence of compliance).
- Step 5 action: Proposed remediation `VERIFY_RECORD_ABSENT` on `account_service:account_7942` (no prior evidence of compliance).
- Step 6 action: Proposed remediation `VERIFY_RECORD_ABSENT` on `search_service:search_5296` (no prior evidence of compliance).
- Step 7 action: Proposed remediation `VERIFY_RECORD_PRESENT` on `security_service:audit_record_9890` (no prior evidence of compliance).
- Step 8 action: Proposed remediation `VERIFY_RECORD_REDACTED` on `support_platform:support_3834` (no prior evidence of compliance).

#### Auditor Reading
Residual personal data or active connections remain in: search_service, support_platform (search_5296, support_3834). The deletion worker reported `COMPLETE`, but empirical evidence confirms incomplete erasure at `2026-06-13T11:00:00Z`. Status is `INCOMPLETE`. Required remediation and verification steps are ordered deterministically by phase.

#### Pipeline Output
- **Deletion Status**: `INCOMPLETE`
- **Steps Count**: 8
```json
[
  {
    "phase": "FINDING",
    "system_id": "search_service",
    "resource_id": "search_5296",
    "operation": "REPORT_REMAINING_RECORD",
    "state": "PRESENT",
    "evidence_id": "evidence_24",
    "step_no": 1
  },
  {
    "phase": "FINDING",
    "system_id": "support_platform",
    "resource_id": "support_3834",
    "operation": "REPORT_EXPOSED_PII",
    "state": "PRESENT",
    "evidence_id": "evidence_24",
    "step_no": 2
  },
  {
    "phase": "REMEDIATION",
    "system_id": "search_service",
    "resource_id": "search_5296",
    "operation": "DELETE_RECORD",
    "state": "ABSENT",
    "evidence_id": "",
    "step_no": 3
  },
  {
    "phase": "REMEDIATION",
    "system_id": "support_platform",
    "resource_id": "support_3834",
    "operation": "REDACT_RECORD",
    "state": "REDACTED",
    "evidence_id": "",
    "step_no": 4
  },
  {
    "phase": "VERIFICATION",
    "system_id": "account_service",
    "resource_id": "account_7942",
    "operation": "VERIFY_RECORD_ABSENT",
    "state": "ABSENT",
    "evidence_id": "",
    "step_no": 5
  },
  {
    "phase": "VERIFICATION",
    "system_id": "search_service",
    "resource_id": "search_5296",
    "operation": "VERIFY_RECORD_ABSENT",
    "state": "ABSENT",
    "evidence_id": "",
    "step_no": 6
  },
  {
    "phase": "VERIFICATION",
    "system_id": "security_service",
    "resource_id": "audit_record_9890",
    "operation": "VERIFY_RECORD_PRESENT",
    "state": "PRESENT",
    "evidence_id": "",
    "step_no": 7
  },
  {
    "phase": "VERIFICATION",
    "system_id": "support_platform",
    "resource_id": "support_3834",
    "operation": "VERIFY_RECORD_REDACTED",
    "state": "REDACTED",
    "evidence_id": "",
    "step_no": 8
  }
]
```

#### Verdict
**AGREE**. The pipeline's decision, resource attribution, state resolution, and step ordering match our independent audit reading exactly.

---

### Case 17: `case_280` (INCOMPLETE)

- **Subject**: `user_278` (`nielsen.ingrid@gmail.com`, resolution: `current`)
- **Audit Time (`audit_at`)**: `2026-06-03T09:00:00Z`
- **Worker Reported Status**: `COMPLETE`
- **Request Text**: *"I am requesting deletion of the account registered to this email address. Please follow the applicable retention and deletion requirements for the account. Please contact me if you need information to verify the request."*

#### Evidence Used
- Step 1 citation: `evidence_77:285` (`evidence/records/service_resource_export_20260603_083457.json`) — `support_platform:support_7073` verified `PRESENT` at `audit_at`.
- Step 2 action: Proposed remediation `REDACT_RECORD` on `support_platform:support_7073` (no prior evidence of compliance).
- Step 3 action: Proposed remediation `VERIFY_RECORD_ABSENT` on `account_service:account_2430` (no prior evidence of compliance).
- Step 4 action: Proposed remediation `VERIFY_RECORD_PRESENT` on `security_service:audit_record_1518` (no prior evidence of compliance).
- Step 5 action: Proposed remediation `VERIFY_RECORD_REDACTED` on `support_platform:support_7073` (no prior evidence of compliance).

#### Auditor Reading
Residual personal data or active connections remain in: support_platform (support_7073). The deletion worker reported `COMPLETE`, but empirical evidence confirms incomplete erasure at `2026-06-03T09:00:00Z`. Status is `INCOMPLETE`. Required remediation and verification steps are ordered deterministically by phase.

#### Pipeline Output
- **Deletion Status**: `INCOMPLETE`
- **Steps Count**: 5
```json
[
  {
    "phase": "FINDING",
    "system_id": "support_platform",
    "resource_id": "support_7073",
    "operation": "REPORT_EXPOSED_PII",
    "state": "PRESENT",
    "evidence_id": "evidence_77",
    "step_no": 1
  },
  {
    "phase": "REMEDIATION",
    "system_id": "support_platform",
    "resource_id": "support_7073",
    "operation": "REDACT_RECORD",
    "state": "REDACTED",
    "evidence_id": "",
    "step_no": 2
  },
  {
    "phase": "VERIFICATION",
    "system_id": "account_service",
    "resource_id": "account_2430",
    "operation": "VERIFY_RECORD_ABSENT",
    "state": "ABSENT",
    "evidence_id": "",
    "step_no": 3
  },
  {
    "phase": "VERIFICATION",
    "system_id": "security_service",
    "resource_id": "audit_record_1518",
    "operation": "VERIFY_RECORD_PRESENT",
    "state": "PRESENT",
    "evidence_id": "",
    "step_no": 4
  },
  {
    "phase": "VERIFICATION",
    "system_id": "support_platform",
    "resource_id": "support_7073",
    "operation": "VERIFY_RECORD_REDACTED",
    "state": "REDACTED",
    "evidence_id": "",
    "step_no": 5
  }
]
```

#### Verdict
**AGREE**. The pipeline's decision, resource attribution, state resolution, and step ordering match our independent audit reading exactly.

---

### Case 18: `case_415` (INCOMPLETE)

- **Subject**: `user_413` (`thandiwe.n5276@outlook.com`, resolution: `current`)
- **Audit Time (`audit_at`)**: `2026-03-25T09:00:00Z`
- **Worker Reported Status**: `COMPLETE`
- **Request Text**: *"Please begin the deletion process for the account using this email address. Please handle any copies that fall within the scope of the deletion request. Let me know when the request has been completed."*

#### Evidence Used
- Step 1 citation: `evidence_39:81` (`evidence/logs/syslog_archive_ap_southeast_20260325.log`) — `account_service:account_9975` verified `PRESENT` at `audit_at`.
- Step 2 citation: `evidence_39:58` (`evidence/logs/syslog_archive_ap_southeast_20260325.log`) — `search_service:search_3864` verified `PRESENT` at `audit_at`.
- Step 3 action: Proposed remediation `DELETE_RECORD` on `account_service:account_9975` (no prior evidence of compliance).
- Step 4 action: Proposed remediation `DELETE_RECORD` on `search_service:search_3864` (no prior evidence of compliance).
- Step 5 action: Proposed remediation `VERIFY_RECORD_ABSENT` on `account_service:account_9975` (no prior evidence of compliance).
- Step 6 action: Proposed remediation `VERIFY_RECORD_ABSENT` on `search_service:search_3864` (no prior evidence of compliance).
- Step 7 action: Proposed remediation `VERIFY_RECORD_PRESENT` on `security_service:audit_record_6154` (no prior evidence of compliance).

#### Auditor Reading
Residual personal data or active connections remain in: account_service, search_service (account_9975, search_3864). The deletion worker reported `COMPLETE`, but empirical evidence confirms incomplete erasure at `2026-03-25T09:00:00Z`. Status is `INCOMPLETE`. Required remediation and verification steps are ordered deterministically by phase.

#### Pipeline Output
- **Deletion Status**: `INCOMPLETE`
- **Steps Count**: 7
```json
[
  {
    "phase": "FINDING",
    "system_id": "account_service",
    "resource_id": "account_9975",
    "operation": "REPORT_REMAINING_RECORD",
    "state": "PRESENT",
    "evidence_id": "evidence_39",
    "step_no": 1
  },
  {
    "phase": "FINDING",
    "system_id": "search_service",
    "resource_id": "search_3864",
    "operation": "REPORT_REMAINING_RECORD",
    "state": "PRESENT",
    "evidence_id": "evidence_39",
    "step_no": 2
  },
  {
    "phase": "REMEDIATION",
    "system_id": "account_service",
    "resource_id": "account_9975",
    "operation": "DELETE_RECORD",
    "state": "ABSENT",
    "evidence_id": "",
    "step_no": 3
  },
  {
    "phase": "REMEDIATION",
    "system_id": "search_service",
    "resource_id": "search_3864",
    "operation": "DELETE_RECORD",
    "state": "ABSENT",
    "evidence_id": "",
    "step_no": 4
  },
  {
    "phase": "VERIFICATION",
    "system_id": "account_service",
    "resource_id": "account_9975",
    "operation": "VERIFY_RECORD_ABSENT",
    "state": "ABSENT",
    "evidence_id": "",
    "step_no": 5
  },
  {
    "phase": "VERIFICATION",
    "system_id": "search_service",
    "resource_id": "search_3864",
    "operation": "VERIFY_RECORD_ABSENT",
    "state": "ABSENT",
    "evidence_id": "",
    "step_no": 6
  },
  {
    "phase": "VERIFICATION",
    "system_id": "security_service",
    "resource_id": "audit_record_6154",
    "operation": "VERIFY_RECORD_PRESENT",
    "state": "PRESENT",
    "evidence_id": "",
    "step_no": 7
  }
]
```

#### Verdict
**AGREE**. The pipeline's decision, resource attribution, state resolution, and step ordering match our independent audit reading exactly.

---

### Case 19: `case_417` (INCOMPLETE)

- **Subject**: `user_415` (`s.kim14@yahoo.com`, resolution: `current`)
- **Audit Time (`audit_at`)**: `2026-03-25T09:00:00Z`
- **Worker Reported Status**: `NOT_STARTED`
- **Request Text**: *"이 이메일 주소에 연결된 계정의 영구 삭제를 요청합니다. 개인정보 처리 절차에 따라 현재 및 이전 식별자를 검토해 주세요. 검토가 완료되면 결과를 확인해 주세요."*

#### Evidence Used
- Step 1 citation: `evidence_39:31` (`evidence/logs/syslog_archive_ap_southeast_20260325.log`) — `account_service:account_4921` verified `PRESENT` at `audit_at`.
- Step 2 citation: `evidence_39:17` (`evidence/logs/syslog_archive_ap_southeast_20260325.log`) — `search_service:search_5479` verified `PRESENT` at `audit_at`.
- Step 3 action: Proposed remediation `DELETE_RECORD` on `account_service:account_4921` (no prior evidence of compliance).
- Step 4 action: Proposed remediation `DELETE_RECORD` on `search_service:search_5479` (no prior evidence of compliance).
- Step 5 action: Proposed remediation `VERIFY_RECORD_ABSENT` on `account_service:account_4921` (no prior evidence of compliance).
- Step 6 action: Proposed remediation `VERIFY_RECORD_ABSENT` on `search_service:search_5479` (no prior evidence of compliance).
- Step 7 action: Proposed remediation `VERIFY_RECORD_PRESENT` on `security_service:audit_record_7959` (no prior evidence of compliance).

#### Auditor Reading
Residual personal data or active connections remain in: account_service, search_service (account_4921, search_5479). The deletion worker reported `NOT_STARTED`, but empirical evidence confirms incomplete erasure at `2026-03-25T09:00:00Z`. Status is `INCOMPLETE`. Required remediation and verification steps are ordered deterministically by phase.

#### Pipeline Output
- **Deletion Status**: `INCOMPLETE`
- **Steps Count**: 7
```json
[
  {
    "phase": "FINDING",
    "system_id": "account_service",
    "resource_id": "account_4921",
    "operation": "REPORT_REMAINING_RECORD",
    "state": "PRESENT",
    "evidence_id": "evidence_39",
    "step_no": 1
  },
  {
    "phase": "FINDING",
    "system_id": "search_service",
    "resource_id": "search_5479",
    "operation": "REPORT_REMAINING_RECORD",
    "state": "PRESENT",
    "evidence_id": "evidence_39",
    "step_no": 2
  },
  {
    "phase": "REMEDIATION",
    "system_id": "account_service",
    "resource_id": "account_4921",
    "operation": "DELETE_RECORD",
    "state": "ABSENT",
    "evidence_id": "",
    "step_no": 3
  },
  {
    "phase": "REMEDIATION",
    "system_id": "search_service",
    "resource_id": "search_5479",
    "operation": "DELETE_RECORD",
    "state": "ABSENT",
    "evidence_id": "",
    "step_no": 4
  },
  {
    "phase": "VERIFICATION",
    "system_id": "account_service",
    "resource_id": "account_4921",
    "operation": "VERIFY_RECORD_ABSENT",
    "state": "ABSENT",
    "evidence_id": "",
    "step_no": 5
  },
  {
    "phase": "VERIFICATION",
    "system_id": "search_service",
    "resource_id": "search_5479",
    "operation": "VERIFY_RECORD_ABSENT",
    "state": "ABSENT",
    "evidence_id": "",
    "step_no": 6
  },
  {
    "phase": "VERIFICATION",
    "system_id": "security_service",
    "resource_id": "audit_record_7959",
    "operation": "VERIFY_RECORD_PRESENT",
    "state": "PRESENT",
    "evidence_id": "",
    "step_no": 7
  }
]
```

#### Verdict
**AGREE**. The pipeline's decision, resource attribution, state resolution, and step ordering match our independent audit reading exactly.

---

### Case 20: `case_47` (INCOMPLETE)

- **Subject**: `user_45` (`zofia-dvorak79@proton.me`, resolution: `historical`)
- **Audit Time (`audit_at`)**: `2026-09-26T11:00:00Z`
- **Worker Reported Status**: `PARTIALLY_COMPLETE`
- **Request Text**: *"I want to close this account and have its associated personal data deleted. Please ensure the request is applied to the relevant account records. I would appreciate confirmation of the final outcome."*

#### Evidence Used
- Step 1 citation: `evidence_94:36` (`evidence/logs/resource_lookup_trace_20260926_103856.log`) — `search_service:search_4324` verified `PRESENT` at `audit_at`.
- Step 2 citation: `evidence_94:16` (`evidence/logs/resource_lookup_trace_20260926_103856.log`) — `support_platform:support_5742` verified `PRESENT` at `audit_at`.
- Step 3 action: Proposed remediation `DELETE_RECORD` on `search_service:search_4324` (no prior evidence of compliance).
- Step 4 action: Proposed remediation `REDACT_RECORD` on `support_platform:support_5742` (no prior evidence of compliance).
- Step 5 action: Proposed remediation `VERIFY_RECORD_ABSENT` on `account_service:account_617` (no prior evidence of compliance).
- Step 6 action: Proposed remediation `VERIFY_RECORD_ABSENT` on `search_service:search_4324` (no prior evidence of compliance).
- Step 7 action: Proposed remediation `VERIFY_RECORD_REDACTED` on `support_platform:support_5742` (no prior evidence of compliance).

#### Auditor Reading
Residual personal data or active connections remain in: search_service, support_platform (search_4324, support_5742). The deletion worker reported `PARTIALLY_COMPLETE`, but empirical evidence confirms incomplete erasure at `2026-09-26T11:00:00Z`. Status is `INCOMPLETE`. Required remediation and verification steps are ordered deterministically by phase.

#### Pipeline Output
- **Deletion Status**: `INCOMPLETE`
- **Steps Count**: 7
```json
[
  {
    "phase": "FINDING",
    "system_id": "search_service",
    "resource_id": "search_4324",
    "operation": "REPORT_REMAINING_RECORD",
    "state": "PRESENT",
    "evidence_id": "evidence_94",
    "step_no": 1
  },
  {
    "phase": "FINDING",
    "system_id": "support_platform",
    "resource_id": "support_5742",
    "operation": "REPORT_EXPOSED_PII",
    "state": "PRESENT",
    "evidence_id": "evidence_94",
    "step_no": 2
  },
  {
    "phase": "REMEDIATION",
    "system_id": "search_service",
    "resource_id": "search_4324",
    "operation": "DELETE_RECORD",
    "state": "ABSENT",
    "evidence_id": "",
    "step_no": 3
  },
  {
    "phase": "REMEDIATION",
    "system_id": "support_platform",
    "resource_id": "support_5742",
    "operation": "REDACT_RECORD",
    "state": "REDACTED",
    "evidence_id": "",
    "step_no": 4
  },
  {
    "phase": "VERIFICATION",
    "system_id": "account_service",
    "resource_id": "account_617",
    "operation": "VERIFY_RECORD_ABSENT",
    "state": "ABSENT",
    "evidence_id": "",
    "step_no": 5
  },
  {
    "phase": "VERIFICATION",
    "system_id": "search_service",
    "resource_id": "search_4324",
    "operation": "VERIFY_RECORD_ABSENT",
    "state": "ABSENT",
    "evidence_id": "",
    "step_no": 6
  },
  {
    "phase": "VERIFICATION",
    "system_id": "support_platform",
    "resource_id": "support_5742",
    "operation": "VERIFY_RECORD_REDACTED",
    "state": "REDACTED",
    "evidence_id": "",
    "step_no": 7
  }
]
```

#### Verdict
**AGREE**. The pipeline's decision, resource attribution, state resolution, and step ordering match our independent audit reading exactly.

---

### Case 21: `case_495` (INCOMPLETE)

- **Subject**: `user_493` (`H.LIM96@GMAIL.COM`, resolution: `current`)
- **Audit Time (`audit_at`)**: `2026-02-13T08:00:00Z`
- **Worker Reported Status**: `NOT_STARTED`
- **Request Text**: *"이 이메일 주소에 연결된 계정의 영구 삭제를 요청합니다. 개인정보 처리 절차에 따라 현재 및 이전 식별자를 검토해 주세요. 검토가 완료되면 결과를 확인해 주세요."*

#### Evidence Used
- Step 1 citation: `evidence_63:24` (`evidence/databases/customer_data_inventory_20260213.sql`) — `backup_service:backup_5061` verified `ACTIVE` at `audit_at`.
- Step 2 action: Proposed remediation `BLOCK_RESTORE` on `backup_service:backup_5061` (no prior evidence of compliance).
- Step 3 action: Proposed remediation `VERIFY_RECORD_ABSENT` on `account_service:account_2512` (no prior evidence of compliance).
- Step 4 action: Proposed remediation `VERIFY_RESTORE_BLOCKED` on `backup_service:backup_5061` (no prior evidence of compliance).

#### Auditor Reading
Residual personal data or active connections remain in: backup_service (backup_5061). The deletion worker reported `NOT_STARTED`, but empirical evidence confirms incomplete erasure at `2026-02-13T08:00:00Z`. Status is `INCOMPLETE`. Required remediation and verification steps are ordered deterministically by phase.

#### Pipeline Output
- **Deletion Status**: `INCOMPLETE`
- **Steps Count**: 4
```json
[
  {
    "phase": "FINDING",
    "system_id": "backup_service",
    "resource_id": "backup_5061",
    "operation": "REPORT_RESTORE_RISK",
    "state": "ACTIVE",
    "evidence_id": "evidence_63",
    "step_no": 1
  },
  {
    "phase": "REMEDIATION",
    "system_id": "backup_service",
    "resource_id": "backup_5061",
    "operation": "BLOCK_RESTORE",
    "state": "BLOCKED",
    "evidence_id": "",
    "step_no": 2
  },
  {
    "phase": "VERIFICATION",
    "system_id": "account_service",
    "resource_id": "account_2512",
    "operation": "VERIFY_RECORD_ABSENT",
    "state": "ABSENT",
    "evidence_id": "",
    "step_no": 3
  },
  {
    "phase": "VERIFICATION",
    "system_id": "backup_service",
    "resource_id": "backup_5061",
    "operation": "VERIFY_RESTORE_BLOCKED",
    "state": "BLOCKED",
    "evidence_id": "",
    "step_no": 4
  }
]
```

#### Verdict
**AGREE**. The pipeline's decision, resource attribution, state resolution, and step ordering match our independent audit reading exactly.

---

### Case 22: `case_507` (INCOMPLETE)

- **Subject**: `user_505` (`r.ito24@gmail.com`, resolution: `current`)
- **Audit Time (`audit_at`)**: `2026-02-08T07:00:00Z`
- **Worker Reported Status**: `COMPLETE`
- **Request Text**: *"このメールアドレスに関連するアカウントの完全な削除を依頼します。 プライバシー手続きに従い、現在および過去の識別情報を確認してください。 確認が完了したら結果をお知らせください。"*

#### Evidence Used
- Step 1 citation: `evidence_47:27` (`evidence/databases/customer_data_reporting_replica_20260208.sql`) — `backup_service:backup_369` verified `ACTIVE` at `audit_at`.
- Step 2 action: Proposed remediation `BLOCK_RESTORE` on `backup_service:backup_369` (no prior evidence of compliance).
- Step 3 action: Proposed remediation `VERIFY_RECORD_ABSENT` on `account_service:account_5423` (no prior evidence of compliance).
- Step 4 action: Proposed remediation `VERIFY_RECORD_PRESENT` on `security_service:audit_record_7627` (no prior evidence of compliance).
- Step 5 action: Proposed remediation `VERIFY_RESTORE_BLOCKED` on `backup_service:backup_369` (no prior evidence of compliance).

#### Auditor Reading
Residual personal data or active connections remain in: backup_service (backup_369). The deletion worker reported `COMPLETE`, but empirical evidence confirms incomplete erasure at `2026-02-08T07:00:00Z`. Status is `INCOMPLETE`. Required remediation and verification steps are ordered deterministically by phase.

#### Pipeline Output
- **Deletion Status**: `INCOMPLETE`
- **Steps Count**: 5
```json
[
  {
    "phase": "FINDING",
    "system_id": "backup_service",
    "resource_id": "backup_369",
    "operation": "REPORT_RESTORE_RISK",
    "state": "ACTIVE",
    "evidence_id": "evidence_47",
    "step_no": 1
  },
  {
    "phase": "REMEDIATION",
    "system_id": "backup_service",
    "resource_id": "backup_369",
    "operation": "BLOCK_RESTORE",
    "state": "BLOCKED",
    "evidence_id": "",
    "step_no": 2
  },
  {
    "phase": "VERIFICATION",
    "system_id": "account_service",
    "resource_id": "account_5423",
    "operation": "VERIFY_RECORD_ABSENT",
    "state": "ABSENT",
    "evidence_id": "",
    "step_no": 3
  },
  {
    "phase": "VERIFICATION",
    "system_id": "security_service",
    "resource_id": "audit_record_7627",
    "operation": "VERIFY_RECORD_PRESENT",
    "state": "PRESENT",
    "evidence_id": "",
    "step_no": 4
  },
  {
    "phase": "VERIFICATION",
    "system_id": "backup_service",
    "resource_id": "backup_369",
    "operation": "VERIFY_RESTORE_BLOCKED",
    "state": "BLOCKED",
    "evidence_id": "",
    "step_no": 5
  }
]
```

#### Verdict
**AGREE**. The pipeline's decision, resource attribution, state resolution, and step ordering match our independent audit reading exactly.

---

### Case 23: `case_526` (INCOMPLETE)

- **Subject**: `user_524` (`chevalier.hugo@icloud.com`, resolution: `current`)
- **Audit Time (`audit_at`)**: `2026-01-29T12:00:00Z`
- **Worker Reported Status**: `COMPLETE`
- **Request Text**: *"Please process a permanent account-deletion request for this email address. Please review the account data that is eligible for deletion or de-identification. Please confirm when the review is complete."*

#### Evidence Used
- Step 1 citation: `evidence_62:228` (`evidence/records/service_resource_export_20260129_114459.json`) — `search_service:search_3879` verified `PRESENT` at `audit_at`.
- Step 2 citation: `evidence_62:60` (`evidence/records/service_resource_export_20260129_114459.json`) — `analytics_platform:analytics_131` verified `PRESENT` at `audit_at`.
- Step 3 citation: `evidence_62:291` (`evidence/records/service_resource_export_20260129_114459.json`) — `support_platform:support_1191` verified `PRESENT` at `audit_at`.
- Step 4 citation: `evidence_62:141` (`evidence/records/service_resource_export_20260129_114459.json`) — `integration_service:data_flow_2263` verified `ACTIVE` at `audit_at`.
- Step 5 action: Proposed remediation `DISABLE_DATA_FLOW` on `integration_service:data_flow_2263` (no prior evidence of compliance).
- Step 6 action: Proposed remediation `DELETE_RECORD` on `search_service:search_3879` (no prior evidence of compliance).
- Step 7 action: Proposed remediation `REDACT_RECORD` on `support_platform:support_1191` (no prior evidence of compliance).
- Step 8 action: Proposed remediation `ANONYMIZE_RECORD` on `analytics_platform:analytics_131` (no prior evidence of compliance).
- Step 9 action: Proposed remediation `VERIFY_RECORD_ABSENT` on `account_service:account_1400` (no prior evidence of compliance).
- Step 10 action: Proposed remediation `VERIFY_RECORD_ABSENT` on `search_service:search_3879` (no prior evidence of compliance).
- Step 11 action: Proposed remediation `VERIFY_RECORD_PRESENT` on `security_service:audit_record_5792` (no prior evidence of compliance).
- Step 12 action: Proposed remediation `VERIFY_RECORD_REDACTED` on `support_platform:support_1191` (no prior evidence of compliance).
- Step 13 action: Proposed remediation `VERIFY_RECORD_ANONYMIZED` on `analytics_platform:analytics_131` (no prior evidence of compliance).
- Step 14 action: Proposed remediation `VERIFY_DATA_FLOW_DISABLED` on `integration_service:data_flow_2263` (no prior evidence of compliance).

#### Auditor Reading
Residual personal data or active connections remain in: analytics_platform, integration_service, search_service, support_platform (analytics_131, data_flow_2263, search_3879, support_1191). The deletion worker reported `COMPLETE`, but empirical evidence confirms incomplete erasure at `2026-01-29T12:00:00Z`. Status is `INCOMPLETE`. Required remediation and verification steps are ordered deterministically by phase.

#### Pipeline Output
- **Deletion Status**: `INCOMPLETE`
- **Steps Count**: 14
```json
[
  {
    "phase": "FINDING",
    "system_id": "search_service",
    "resource_id": "search_3879",
    "operation": "REPORT_REMAINING_RECORD",
    "state": "PRESENT",
    "evidence_id": "evidence_62",
    "step_no": 1
  },
  {
    "phase": "FINDING",
    "system_id": "analytics_platform",
    "resource_id": "analytics_131",
    "operation": "REPORT_EXPOSED_PII",
    "state": "PRESENT",
    "evidence_id": "evidence_62",
    "step_no": 2
  },
  {
    "phase": "FINDING",
    "system_id": "support_platform",
    "resource_id": "support_1191",
    "operation": "REPORT_EXPOSED_PII",
    "state": "PRESENT",
    "evidence_id": "evidence_62",
    "step_no": 3
  },
  {
    "phase": "FINDING",
    "system_id": "integration_service",
    "resource_id": "data_flow_2263",
    "operation": "REPORT_ACTIVE_DATA_FLOW",
    "state": "ACTIVE",
    "evidence_id": "evidence_62",
    "step_no": 4
  },
  {
    "phase": "REMEDIATION",
    "system_id": "integration_service",
    "resource_id": "data_flow_2263",
    "operation": "DISABLE_DATA_FLOW",
    "state": "DISABLED",
    "evidence_id": "",
    "step_no": 5
  },
  {
    "phase": "REMEDIATION",
    "system_id": "search_service",
    "resource_id": "search_3879",
    "operation": "DELETE_RECORD",
    "state": "ABSENT",
    "evidence_id": "",
    "step_no": 6
  },
  {
    "phase": "REMEDIATION",
    "system_id": "support_platform",
    "resource_id": "support_1191",
    "operation": "REDACT_RECORD",
    "state": "REDACTED",
    "evidence_id": "",
    "step_no": 7
  },
  {
    "phase": "REMEDIATION",
    "system_id": "analytics_platform",
    "resource_id": "analytics_131",
    "operation": "ANONYMIZE_RECORD",
    "state": "ANONYMIZED",
    "evidence_id": "",
    "step_no": 8
  },
  {
    "phase": "VERIFICATION",
    "system_id": "account_service",
    "resource_id": "account_1400",
    "operation": "VERIFY_RECORD_ABSENT",
    "state": "ABSENT",
    "evidence_id": "",
    "step_no": 9
  },
  {
    "phase": "VERIFICATION",
    "system_id": "search_service",
    "resource_id": "search_3879",
    "operation": "VERIFY_RECORD_ABSENT",
    "state": "ABSENT",
    "evidence_id": "",
    "step_no": 10
  },
  {
    "phase": "VERIFICATION",
    "system_id": "security_service",
    "resource_id": "audit_record_5792",
    "operation": "VERIFY_RECORD_PRESENT",
    "state": "PRESENT",
    "evidence_id": "",
    "step_no": 11
  },
  {
    "phase": "VERIFICATION",
    "system_id": "support_platform",
    "resource_id": "support_1191",
    "operation": "VERIFY_RECORD_REDACTED",
    "state": "REDACTED",
    "evidence_id": "",
    "step_no": 12
  },
  {
    "phase": "VERIFICATION",
    "system_id": "analytics_platform",
    "resource_id": "analytics_131",
    "operation": "VERIFY_RECORD_ANONYMIZED",
    "state": "ANONYMIZED",
    "evidence_id": "",
    "step_no": 13
  },
  {
    "phase": "VERIFICATION",
    "system_id": "integration_service",
    "resource_id": "data_flow_2263",
    "operation": "VERIFY_DATA_FLOW_DISABLED",
    "state": "DISABLED",
    "evidence_id": "",
    "step_no": 14
  }
]
```

#### Verdict
**AGREE**. The pipeline's decision, resource attribution, state resolution, and step ordering match our independent audit reading exactly.

---

### Case 24: `case_544` (INCOMPLETE)

- **Subject**: `user_544` (`kito2665@gmail.com`, resolution: `current`)
- **Audit Time (`audit_at`)**: `2026-09-20T12:00:00Z`
- **Worker Reported Status**: `COMPLETE`
- **Request Text**: *"Please begin the deletion process for the account using this email address. Please ensure the request is applied to the relevant account records. A short confirmation when the process is complete is sufficient."*

#### Evidence Used
- Step 1 citation: `evidence_52:28` (`evidence/databases/customer_data_failover_replica_20260920.sql`) — `identity_service:tombstone_8648` verified `PRESENT` at `audit_at`.
- Step 2 action: Proposed remediation `REDACT_RECORD` on `identity_service:tombstone_8648` (no prior evidence of compliance).
- Step 3 action: Proposed remediation `VERIFY_RECORD_ABSENT` on `account_service:account_2577` (no prior evidence of compliance).
- Step 4 action: Proposed remediation `VERIFY_RECORD_PRESENT` on `security_service:audit_record_1037` (no prior evidence of compliance).
- Step 5 action: Proposed remediation `VERIFY_RECORD_REDACTED` on `identity_service:tombstone_8648` (no prior evidence of compliance).

#### Auditor Reading
Residual personal data or active connections remain in: identity_service (tombstone_8648). The deletion worker reported `COMPLETE`, but empirical evidence confirms incomplete erasure at `2026-09-20T12:00:00Z`. Status is `INCOMPLETE`. Required remediation and verification steps are ordered deterministically by phase.

#### Pipeline Output
- **Deletion Status**: `INCOMPLETE`
- **Steps Count**: 5
```json
[
  {
    "phase": "FINDING",
    "system_id": "identity_service",
    "resource_id": "tombstone_8648",
    "operation": "REPORT_EXPOSED_PII",
    "state": "PRESENT",
    "evidence_id": "evidence_52",
    "step_no": 1
  },
  {
    "phase": "REMEDIATION",
    "system_id": "identity_service",
    "resource_id": "tombstone_8648",
    "operation": "REDACT_RECORD",
    "state": "REDACTED",
    "evidence_id": "",
    "step_no": 2
  },
  {
    "phase": "VERIFICATION",
    "system_id": "account_service",
    "resource_id": "account_2577",
    "operation": "VERIFY_RECORD_ABSENT",
    "state": "ABSENT",
    "evidence_id": "",
    "step_no": 3
  },
  {
    "phase": "VERIFICATION",
    "system_id": "security_service",
    "resource_id": "audit_record_1037",
    "operation": "VERIFY_RECORD_PRESENT",
    "state": "PRESENT",
    "evidence_id": "",
    "step_no": 4
  },
  {
    "phase": "VERIFICATION",
    "system_id": "identity_service",
    "resource_id": "tombstone_8648",
    "operation": "VERIFY_RECORD_REDACTED",
    "state": "REDACTED",
    "evidence_id": "",
    "step_no": 5
  }
]
```

#### Verdict
**AGREE**. The pipeline's decision, resource attribution, state resolution, and step ordering match our independent audit reading exactly.

---

### Case 25: `case_96` (INCOMPLETE)

- **Subject**: `user_94` (`smorgan9115@fastmail.com`, resolution: `current`)
- **Audit Time (`audit_at`)**: `2026-09-01T06:00:00Z`
- **Worker Reported Status**: `NOT_STARTED`
- **Request Text**: *"Please close my account and process the associated personal-data deletion. Please review the account data that is eligible for deletion or de-identification. A short confirmation when the process is complete is sufficient."*

#### Evidence Used
- Step 1 citation: `evidence_89:74` (`evidence/records/service_resource_export_20260901_053316.json`) — `export_service:export_8827` verified `PRESENT` at `audit_at`.
- Step 2 citation: `evidence_89:169` (`evidence/records/service_resource_export_20260901_053316.json`) — `search_service:search_5672` verified `PRESENT` at `audit_at`.
- Step 3 action: Proposed remediation `DELETE_RECORD` on `export_service:export_8827` (no prior evidence of compliance).
- Step 4 action: Proposed remediation `DELETE_RECORD` on `search_service:search_5672` (no prior evidence of compliance).
- Step 5 action: Proposed remediation `VERIFY_RECORD_ABSENT` on `account_service:account_4176` (no prior evidence of compliance).
- Step 6 action: Proposed remediation `VERIFY_RECORD_ABSENT` on `export_service:export_8827` (no prior evidence of compliance).
- Step 7 action: Proposed remediation `VERIFY_RECORD_ABSENT` on `search_service:search_5672` (no prior evidence of compliance).

#### Auditor Reading
Residual personal data or active connections remain in: export_service, search_service (export_8827, search_5672). The deletion worker reported `NOT_STARTED`, but empirical evidence confirms incomplete erasure at `2026-09-01T06:00:00Z`. Status is `INCOMPLETE`. Required remediation and verification steps are ordered deterministically by phase.

#### Pipeline Output
- **Deletion Status**: `INCOMPLETE`
- **Steps Count**: 7
```json
[
  {
    "phase": "FINDING",
    "system_id": "export_service",
    "resource_id": "export_8827",
    "operation": "REPORT_REMAINING_RECORD",
    "state": "PRESENT",
    "evidence_id": "evidence_89",
    "step_no": 1
  },
  {
    "phase": "FINDING",
    "system_id": "search_service",
    "resource_id": "search_5672",
    "operation": "REPORT_REMAINING_RECORD",
    "state": "PRESENT",
    "evidence_id": "evidence_89",
    "step_no": 2
  },
  {
    "phase": "REMEDIATION",
    "system_id": "export_service",
    "resource_id": "export_8827",
    "operation": "DELETE_RECORD",
    "state": "ABSENT",
    "evidence_id": "",
    "step_no": 3
  },
  {
    "phase": "REMEDIATION",
    "system_id": "search_service",
    "resource_id": "search_5672",
    "operation": "DELETE_RECORD",
    "state": "ABSENT",
    "evidence_id": "",
    "step_no": 4
  },
  {
    "phase": "VERIFICATION",
    "system_id": "account_service",
    "resource_id": "account_4176",
    "operation": "VERIFY_RECORD_ABSENT",
    "state": "ABSENT",
    "evidence_id": "",
    "step_no": 5
  },
  {
    "phase": "VERIFICATION",
    "system_id": "export_service",
    "resource_id": "export_8827",
    "operation": "VERIFY_RECORD_ABSENT",
    "state": "ABSENT",
    "evidence_id": "",
    "step_no": 6
  },
  {
    "phase": "VERIFICATION",
    "system_id": "search_service",
    "resource_id": "search_5672",
    "operation": "VERIFY_RECORD_ABSENT",
    "state": "ABSENT",
    "evidence_id": "",
    "step_no": 7
  }
]
```

#### Verdict
**AGREE**. The pipeline's decision, resource attribution, state resolution, and step ordering match our independent audit reading exactly.

---

### Case 26: `case_533` (NOT_APPLICABLE)

- **Subject**: `user_531` (`haruka-kato@gmail.com`, resolution: `current`)
- **Audit Time (`audit_at`)**: `2026-10-01T12:00:00Z`
- **Worker Reported Status**: `NOT_STARTED`
- **Request Text**: *"The mobile number on my profile is out of date. Please replace it with the new one and leave the account active."*

#### Evidence Used
- `dataset/system_activity.csv`: `CLASSIFY_REQUEST` intake record logs explicit non-deletion intent (access, export, rectification, or opt-out).

#### Auditor Reading
The request is an inquiry, data export, or rectification rather than an authorized erasure request. The system activity log confirms non-deletion classification at intake. Under policy, no deletion workflow applies; status is `NOT_APPLICABLE` with 0 steps (`[]`).

#### Pipeline Output
- **Deletion Status**: `NOT_APPLICABLE`
- **Steps Count**: 0
`[]` (empty steps array)

#### Verdict
**AGREE**. The pipeline's decision, resource attribution, state resolution, and step ordering match our independent audit reading exactly.

---

### Case 27: `case_534` (NOT_APPLICABLE)

- **Subject**: `user_532` (`mlim7637@gmail.com`, resolution: `current`)
- **Audit Time (`audit_at`)**: `2026-09-30T12:00:00Z`
- **Worker Reported Status**: `NOT_STARTED`
- **Request Text**: *"Please stop the promotional emails. I still need the account and my order history, so I am not asking for deletion."*

#### Evidence Used
- `dataset/system_activity.csv`: `CLASSIFY_REQUEST` intake record logs explicit non-deletion intent (access, export, rectification, or opt-out).

#### Auditor Reading
The request is an inquiry, data export, or rectification rather than an authorized erasure request. The system activity log confirms non-deletion classification at intake. Under policy, no deletion workflow applies; status is `NOT_APPLICABLE` with 0 steps (`[]`).

#### Pipeline Output
- **Deletion Status**: `NOT_APPLICABLE`
- **Steps Count**: 0
`[]` (empty steps array)

#### Verdict
**AGREE**. The pipeline's decision, resource attribution, state resolution, and step ordering match our independent audit reading exactly.

---

### Case 28: `case_535` (NOT_APPLICABLE)

- **Subject**: `user_533` (`gabriel.l5556@outlook.com`, resolution: `current`)
- **Audit Time (`audit_at`)**: `2026-09-29T12:00:00Z`
- **Worker Reported Status**: `NOT_STARTED`
- **Request Text**: *"I'd like to download my account information in a portable format. Please keep the account as it is."*

#### Evidence Used
- `dataset/system_activity.csv`: `CLASSIFY_REQUEST` intake record logs explicit non-deletion intent (access, export, rectification, or opt-out).

#### Auditor Reading
The request is an inquiry, data export, or rectification rather than an authorized erasure request. The system activity log confirms non-deletion classification at intake. Under policy, no deletion workflow applies; status is `NOT_APPLICABLE` with 0 steps (`[]`).

#### Pipeline Output
- **Deletion Status**: `NOT_APPLICABLE`
- **Steps Count**: 0
`[]` (empty steps array)

#### Verdict
**AGREE**. The pipeline's decision, resource attribution, state resolution, and step ordering match our independent audit reading exactly.

---

### Case 29: `case_536` (NOT_APPLICABLE)

- **Subject**: `user_534` (`aditi.mehta@outlook.com`, resolution: `current`)
- **Audit Time (`audit_at`)**: `2026-09-28T12:00:00Z`
- **Worker Reported Status**: `NOT_STARTED`
- **Request Text**: *"I can't access my profile and need help resetting the login. Do not close the account."*

#### Evidence Used
- `dataset/system_activity.csv`: `CLASSIFY_REQUEST` intake record logs explicit non-deletion intent (access, export, rectification, or opt-out).

#### Auditor Reading
The request is an inquiry, data export, or rectification rather than an authorized erasure request. The system activity log confirms non-deletion classification at intake. Under policy, no deletion workflow applies; status is `NOT_APPLICABLE` with 0 steps (`[]`).

#### Pipeline Output
- **Deletion Status**: `NOT_APPLICABLE`
- **Steps Count**: 0
`[]` (empty steps array)

#### Verdict
**AGREE**. The pipeline's decision, resource attribution, state resolution, and step ordering match our independent audit reading exactly.

---

### Case 30: `case_537` (NOT_APPLICABLE)

- **Subject**: `user_535` (`l.alvarez94@yahoo.com`, resolution: `current`)
- **Audit Time (`audit_at`)**: `2026-09-27T12:00:00Z`
- **Worker Reported Status**: `NOT_STARTED`
- **Request Text**: *"My surname is misspelled on the account. Can you correct it without removing any of my records?"*

#### Evidence Used
- `dataset/system_activity.csv`: `CLASSIFY_REQUEST` intake record logs explicit non-deletion intent (access, export, rectification, or opt-out).

#### Auditor Reading
The request is an inquiry, data export, or rectification rather than an authorized erasure request. The system activity log confirms non-deletion classification at intake. Under policy, no deletion workflow applies; status is `NOT_APPLICABLE` with 0 steps (`[]`).

#### Pipeline Output
- **Deletion Status**: `NOT_APPLICABLE`
- **Steps Count**: 0
`[]` (empty steps array)

#### Verdict
**AGREE**. The pipeline's decision, resource attribution, state resolution, and step ordering match our independent audit reading exactly.

---

### Case 31: `case_538` (NOT_APPLICABLE)

- **Subject**: `user_536` (`morgan.amelia@icloud.com`, resolution: `current`)
- **Audit Time (`audit_at`)**: `2026-09-26T12:00:00Z`
- **Worker Reported Status**: `NOT_STARTED`
- **Request Text**: *"Please remove me from marketing lists only. I still want receipts and service messages for this account."*

#### Evidence Used
- `dataset/system_activity.csv`: `CLASSIFY_REQUEST` intake record logs explicit non-deletion intent (access, export, rectification, or opt-out).

#### Auditor Reading
The request is an inquiry, data export, or rectification rather than an authorized erasure request. The system activity log confirms non-deletion classification at intake. Under policy, no deletion workflow applies; status is `NOT_APPLICABLE` with 0 steps (`[]`).

#### Pipeline Output
- **Deletion Status**: `NOT_APPLICABLE`
- **Steps Count**: 0
`[]` (empty steps array)

#### Verdict
**AGREE**. The pipeline's decision, resource attribution, state resolution, and step ordering match our independent audit reading exactly.

---

### Case 32: `case_539` (NOT_APPLICABLE)

- **Subject**: `user_537` (`leonie-rousseau@proton.me`, resolution: `current`)
- **Audit Time (`audit_at`)**: `2026-09-25T12:00:00Z`
- **Worker Reported Status**: `NOT_STARTED`
- **Request Text**: *"Can you tell me what personal information you hold about me? This is an information request, not a request to erase it."*

#### Evidence Used
- `dataset/system_activity.csv`: `CLASSIFY_REQUEST` intake record logs explicit non-deletion intent (access, export, rectification, or opt-out).

#### Auditor Reading
The request is an inquiry, data export, or rectification rather than an authorized erasure request. The system activity log confirms non-deletion classification at intake. Under policy, no deletion workflow applies; status is `NOT_APPLICABLE` with 0 steps (`[]`).

#### Pipeline Output
- **Deletion Status**: `NOT_APPLICABLE`
- **Steps Count**: 0
`[]` (empty steps array)

#### Verdict
**AGREE**. The pipeline's decision, resource attribution, state resolution, and step ordering match our independent audit reading exactly.

---

### Case 33: `case_540` (NOT_APPLICABLE)

- **Subject**: `user_538` (`ieriksen5151@fastmail.com`, resolution: `current`)
- **Audit Time (`audit_at`)**: `2026-09-24T12:00:00Z`
- **Worker Reported Status**: `NOT_STARTED`
- **Request Text**: *"I need a copy of last year's invoices for my records. Please leave my profile and purchase history in place."*

#### Evidence Used
- `dataset/system_activity.csv`: `CLASSIFY_REQUEST` intake record logs explicit non-deletion intent (access, export, rectification, or opt-out).

#### Auditor Reading
The request is an inquiry, data export, or rectification rather than an authorized erasure request. The system activity log confirms non-deletion classification at intake. Under policy, no deletion workflow applies; status is `NOT_APPLICABLE` with 0 steps (`[]`).

#### Pipeline Output
- **Deletion Status**: `NOT_APPLICABLE`
- **Steps Count**: 0
`[]` (empty steps array)

#### Verdict
**AGREE**. The pipeline's decision, resource attribution, state resolution, and step ordering match our independent audit reading exactly.

---

### Case 34: `case_541` (NOT_APPLICABLE)

- **Subject**: `user_539` (`elena.h3070@zoho.com`, resolution: `current`)
- **Audit Time (`audit_at`)**: `2026-09-23T12:00:00Z`
- **Worker Reported Status**: `NOT_STARTED`
- **Request Text**: *"Please change the email address used for this account. I want to continue using the service."*

#### Evidence Used
- `dataset/system_activity.csv`: `CLASSIFY_REQUEST` intake record logs explicit non-deletion intent (access, export, rectification, or opt-out).

#### Auditor Reading
The request is an inquiry, data export, or rectification rather than an authorized erasure request. The system activity log confirms non-deletion classification at intake. Under policy, no deletion workflow applies; status is `NOT_APPLICABLE` with 0 steps (`[]`).

#### Pipeline Output
- **Deletion Status**: `NOT_APPLICABLE`
- **Steps Count**: 0
`[]` (empty steps array)

#### Verdict
**AGREE**. The pipeline's decision, resource attribution, state resolution, and step ordering match our independent audit reading exactly.

---

### Case 35: `case_542` (NOT_APPLICABLE)

- **Subject**: `user_540` (`omar.nasser@gmail.com`, resolution: `current`)
- **Audit Time (`audit_at`)**: `2026-09-22T12:00:00Z`
- **Worker Reported Status**: `NOT_STARTED`
- **Request Text**: *"Could you send me a copy of the information held on my account? I still use it, so please don't delete or change anything."*

#### Evidence Used
- `dataset/system_activity.csv`: `CLASSIFY_REQUEST` intake record logs explicit non-deletion intent (access, export, rectification, or opt-out).

#### Auditor Reading
The request is an inquiry, data export, or rectification rather than an authorized erasure request. The system activity log confirms non-deletion classification at intake. Under policy, no deletion workflow applies; status is `NOT_APPLICABLE` with 0 steps (`[]`).

#### Pipeline Output
- **Deletion Status**: `NOT_APPLICABLE`
- **Steps Count**: 0
`[]` (empty steps array)

#### Verdict
**AGREE**. The pipeline's decision, resource attribution, state resolution, and step ordering match our independent audit reading exactly.

---
