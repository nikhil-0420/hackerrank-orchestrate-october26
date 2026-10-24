# Ghost Audit Evaluation Report

| Metadata | Value |
|---|---|
| **Git Commit** | `86c5ab8f90cad7004dd34d8da88cf1e343e15b50` |
| **Command** | `python code/evaluation/main.py --pred dataset/sample_output.csv --truth dataset/sample_output.csv --out code/evaluation/evaluation_report.md` |
| **Predictions** | `dataset/sample_output.csv` (32 cases) |
| **Ground Truth** | `dataset/sample_output.csv` (32 cases) |
| **Requests Context** | `dataset/sample_deletion_requests.csv` |

## 1. Executive Summary Metrics

| Metric | Score | Detail / Formula |
|---|---|---|
| **Case Status Accuracy** | 1.0000 | 32 / 32 cases correct |
| **Row Exact-Match Rate** | 1.0000 | 32 / 32 cases identical (status + canonical steps) |
| **Step Multiset Micro F1** | 1.0000 | Micro P=1.0000, R=1.0000 |
| **Step Multiset Macro F1** | 1.0000 | Macro P=1.0000, R=1.0000 |
| **Sequence Exact-Order Rate** | 1.0000 | 32 / 32 exact sequence match |
| **Sequence Mean LCS Ratio** | 1.0000 | Average 2*LCS/(len_p + len_t) across cases |
| **Step Alignment Coverage (Truth)** | 1.0000 | 193 / 193 truth steps aligned |
| **Step Alignment Coverage (Pred)** | 1.0000 | 193 / 193 pred steps aligned |

## 2. Status Confusion Matrix

| Truth \ Predicted | COMPLETE | INCOMPLETE | NOT_APPLICABLE | Total |
|---|---|---|---|---|
| **COMPLETE** | 10 | 0 | 0 | 10 |
| **INCOMPLETE** | 0 | 22 | 0 | 22 |
| **NOT_APPLICABLE** | 0 | 0 | 0 | 0 |

## 3. Field-Level Accuracy (on Aligned Steps)

| Field Name | Accuracy | Aligned Steps Evaluated |
|---|---|---|
| `phase` | 1.0000 | 193 |
| `operation` | 1.0000 | 193 |
| `system_id` | 1.0000 | 193 |
| `resource_id` | 1.0000 | 193 |
| `state` | 1.0000 | 193 |
| `evidence_id` | 1.0000 | 193 |
| `step_no` | 1.0000 | 193 |

## 4. Breakdowns by Truth Status

| Truth Status | Case Count | Status Acc | Row Exact Match | Step Micro F1 | Seq Exact Order |
|---|---|---|---|---|---|
| **COMPLETE** | 10 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| **INCOMPLETE** | 22 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| **NOT_APPLICABLE** | 0 | 0.0000 | 0.0000 | 1.0000 | 0.0000 |

## 5. Breakdowns by Step Phase

| Step Phase | Truth Steps | Pred Steps | Precision | Recall | F1 Score |
|---|---|---|---|---|---|
| **FINDING** | 41 | 41 | 1.0000 | 1.0000 | 1.0000 |
| **REMEDIATION** | 41 | 41 | 1.0000 | 1.0000 | 1.0000 |
| **VERIFICATION** | 111 | 111 | 1.0000 | 1.0000 | 1.0000 |

## 6. Breakdown by Request Email (Historical vs Current)

> [!NOTE]
> Breakdown by historical vs current request email is omitted (requires `ghost_audit.identity` which is not yet implemented in Phase 2).

## 7. Non-Exact Match Errors Table

| Case ID | Truth Status | Pred Status | First Diff Step | Diagnosis Reason |
|---|---|---|---|---|
| (None) | - | - | - | All cases match ground truth exactly (100% exact match). |

## 8. Per-Module Error Attribution

NOT YET MEASURED

## 9. Config A/B/C Comparison

NOT YET MEASURED

## 10. Custom Cases

NOT YET MEASURED
