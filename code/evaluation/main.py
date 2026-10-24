"""
Evaluation harness for Ghost Audit.
Computes evaluation metrics between predictions and ground-truth answers.
Renders deterministic Markdown evaluation reports without non-deterministic timestamps.
CLI: python3 code/evaluation/main.py --pred P [--truth T] [--requests R] [--out O]
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

CODE_DIR = Path(__file__).resolve().parent.parent
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

from evaluation.metrics import (
    compute_error_table,
    compute_field_level_accuracy,
    compute_phase_breakdowns,
    compute_row_exact_match,
    compute_sequence_metrics,
    compute_status_breakdowns,
    compute_status_metrics,
    compute_step_multiset_prf,
)


def get_git_commit(repo_root: Path) -> str:
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            check=True,
        )
        return proc.stdout.strip()
    except Exception:
        return "UNKNOWN_COMMIT"


def load_output_cases(path: Path) -> dict[str, dict[str, Any]]:
    cases: dict[str, dict[str, Any]] = {}
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cid = row.get("case_id", "").strip()
            if not cid:
                continue
            status = row.get("deletion_status", "").strip()
            raw_steps = row.get("steps_json", "[]").strip()
            try:
                steps = json.loads(raw_steps)
            except Exception:
                steps = []
            cases[cid] = {
                "case_id": cid,
                "deletion_status": status,
                "steps": steps,
            }
    return cases


def generate_markdown_report(
    pred_path: Path,
    truth_path: Path,
    requests_path: Path | None,
    command_str: str,
    git_commit: str,
    preds: dict[str, dict[str, Any]],
    truths: dict[str, dict[str, Any]],
) -> str:
    # Compute all metric suites
    status_res = compute_status_metrics(preds, truths)
    exact_res = compute_row_exact_match(preds, truths)
    step_prf = compute_step_multiset_prf(preds, truths)
    field_acc = compute_field_level_accuracy(preds, truths)
    seq_metrics = compute_sequence_metrics(preds, truths)
    status_bd = compute_status_breakdowns(preds, truths)
    phase_bd = compute_phase_breakdowns(preds, truths)
    errors = compute_error_table(preds, truths)

    lines: list[str] = []

    # 1. Header with Git commit (deterministic, no timestamp in body)
    lines.append("# Ghost Audit Evaluation Report")
    lines.append("")
    lines.append("| Metadata | Value |")
    lines.append("|---|---|")
    lines.append(f"| **Git Commit** | `{git_commit}` |")
    lines.append(f"| **Command** | `{command_str}` |")
    lines.append(f"| **Predictions** | `{pred_path.as_posix()}` ({len(preds)} cases) |")
    lines.append(f"| **Ground Truth** | `{truth_path.as_posix()}` ({len(truths)} cases) |")
    if requests_path:
        lines.append(f"| **Requests Context** | `{requests_path.as_posix()}` |")
    lines.append("")

    # 2. Executive Summary Metrics Table
    lines.append("## 1. Executive Summary Metrics")
    lines.append("")
    lines.append("| Metric | Score | Detail / Formula |")
    lines.append("|---|---|---|")
    lines.append(f"| **Case Status Accuracy** | {status_res['status_accuracy']:.4f} | {status_res['correct_cases']} / {status_res['total_cases']} cases correct |")
    lines.append(f"| **Row Exact-Match Rate** | {exact_res['exact_match_rate']:.4f} | {exact_res['exact_matches']} / {exact_res['total_cases']} cases identical (status + canonical steps) |")
    lines.append(f"| **Step Multiset Micro F1** | {step_prf['micro_f1']:.4f} | Micro P={step_prf['micro_precision']:.4f}, R={step_prf['micro_recall']:.4f} |")
    lines.append(f"| **Step Multiset Macro F1** | {step_prf['macro_f1']:.4f} | Macro P={step_prf['macro_precision']:.4f}, R={step_prf['macro_recall']:.4f} |")
    lines.append(f"| **Sequence Exact-Order Rate** | {seq_metrics['exact_order_rate']:.4f} | {seq_metrics['exact_order_matches']} / {seq_metrics['total_cases']} exact sequence match |")
    lines.append(f"| **Sequence Mean LCS Ratio** | {seq_metrics['mean_lcs_ratio']:.4f} | Average 2*LCS/(len_p + len_t) across cases |")
    lines.append(f"| **Step Alignment Coverage (Truth)** | {field_acc['coverage_truth']:.4f} | {field_acc['aligned_count']} / {field_acc['total_truth_steps']} truth steps aligned |")
    lines.append(f"| **Step Alignment Coverage (Pred)** | {field_acc['coverage_pred']:.4f} | {field_acc['aligned_count']} / {field_acc['total_pred_steps']} pred steps aligned |")
    lines.append("")

    # 3. Status Confusion Matrix
    lines.append("## 2. Status Confusion Matrix")
    lines.append("")
    lines.append("| Truth \\ Predicted | COMPLETE | INCOMPLETE | NOT_APPLICABLE | Total |")
    lines.append("|---|---|---|---|---|")
    for t_st in ["COMPLETE", "INCOMPLETE", "NOT_APPLICABLE"]:
        row_counts = [status_res["confusion_matrix"][t_st][p_st] for p_st in ["COMPLETE", "INCOMPLETE", "NOT_APPLICABLE"]]
        row_sum = sum(row_counts)
        lines.append(f"| **{t_st}** | {row_counts[0]} | {row_counts[1]} | {row_counts[2]} | {row_sum} |")
    lines.append("")

    # 4. Field-Level Accuracy Table
    lines.append("## 3. Field-Level Accuracy (on Aligned Steps)")
    lines.append("")
    lines.append("| Field Name | Accuracy | Aligned Steps Evaluated |")
    lines.append("|---|---|---|")
    for f_name, acc in field_acc["field_accuracies"].items():
        lines.append(f"| `{f_name}` | {acc:.4f} | {field_acc['aligned_count']} |")
    lines.append("")

    # 5. Breakdowns by Status
    lines.append("## 4. Breakdowns by Truth Status")
    lines.append("")
    lines.append("| Truth Status | Case Count | Status Acc | Row Exact Match | Step Micro F1 | Seq Exact Order |")
    lines.append("|---|---|---|---|---|---|")
    for st_name, metrics in status_bd.items():
        lines.append(
            f"| **{st_name}** | {metrics['count']} | {metrics['status_acc']:.4f} | {metrics['row_exact_match']:.4f} | {metrics['step_micro_f1']:.4f} | {metrics['seq_exact_order']:.4f} |"
        )
    lines.append("")

    # 6. Breakdowns by Step Phase
    lines.append("## 5. Breakdowns by Step Phase")
    lines.append("")
    lines.append("| Step Phase | Truth Steps | Pred Steps | Precision | Recall | F1 Score |")
    lines.append("|---|---|---|---|---|---|")
    for p_name, p_metrics in phase_bd.items():
        lines.append(
            f"| **{p_name}** | {p_metrics['truth_steps']} | {p_metrics['pred_steps']} | {p_metrics['precision']:.4f} | {p_metrics['recall']:.4f} | {p_metrics['f1']:.4f} |"
        )
    lines.append("")

    # 7. Breakdown by Request Email Status
    lines.append("## 6. Breakdown by Request Email (Historical vs Current)")
    lines.append("")
    lines.append("> [!NOTE]")
    lines.append("> Breakdown by historical vs current request email is omitted (requires `ghost_audit.identity` which is not yet implemented in Phase 2).")
    lines.append("")

    # 8. Errors Table
    lines.append("## 7. Non-Exact Match Errors Table")
    lines.append("")
    if not errors:
        lines.append("| Case ID | Truth Status | Pred Status | First Diff Step | Diagnosis Reason |")
        lines.append("|---|---|---|---|---|")
        lines.append("| (None) | - | - | - | All cases match ground truth exactly (100% exact match). |")
    else:
        lines.append("| Case ID | Truth Status | Pred Status | First Diff Step | Diagnosis Reason |")
        lines.append("|---|---|---|---|---|")
        for err in errors[:50]:
            lines.append(f"| `{err['case_id']}` | {err['truth_status']} | {err['pred_status']} | {err['diff_step']} | {err['reason']} |")
        if len(errors) > 50:
            lines.append(f"| ... | ... | ... | ... | {len(errors) - 50} additional error rows omitted. |")
    lines.append("")

    # 9. Placeholder Sections for Future Phases
    lines.append("## 8. Per-Module Error Attribution")
    lines.append("")
    lines.append("NOT YET MEASURED")
    lines.append("")
    lines.append("## 9. Config A/B/C Comparison")
    lines.append("")
    lines.append("NOT YET MEASURED")
    lines.append("")
    lines.append("## 10. Custom Cases")
    lines.append("")
    lines.append("NOT YET MEASURED")
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Ghost Audit Evaluation Report Generator")
    parser.add_argument("--pred", "-p", required=True, help="Path to predictions CSV file")
    parser.add_argument("--truth", "-t", default="dataset/sample_output.csv", help="Path to ground truth CSV file")
    parser.add_argument("--requests", "-r", default="dataset/sample_deletion_requests.csv", help="Path to requests CSV file")
    parser.add_argument("--out", "-o", default="code/evaluation/evaluation_report.md", help="Output path for evaluation report")

    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent.parent
    pred_path = Path(args.pred)
    truth_path = Path(args.truth)
    req_path = Path(args.requests) if args.requests else None
    out_path = Path(args.out)

    if not pred_path.exists():
        print(f"Error: predictions file not found: {pred_path}", file=sys.stderr)
        sys.exit(1)
    if not truth_path.exists():
        print(f"Error: ground truth file not found: {truth_path}", file=sys.stderr)
        sys.exit(1)

    preds = load_output_cases(pred_path)
    truths = load_output_cases(truth_path)

    cmd_str = f"python code/evaluation/main.py --pred {args.pred} --truth {args.truth} --out {args.out}"
    git_commit = get_git_commit(repo_root)

    report_md = generate_markdown_report(
        pred_path=pred_path,
        truth_path=truth_path,
        requests_path=req_path,
        command_str=cmd_str,
        git_commit=git_commit,
        preds=preds,
        truths=truths,
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report_md, encoding="utf-8")
    print(f"Evaluation report generated successfully at: {out_path}")


if __name__ == "__main__":
    main()
