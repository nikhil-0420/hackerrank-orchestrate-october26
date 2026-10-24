"""
Pure metric calculation functions for Ghost Audit evaluation.
Computes case-level, step-level, field-level, and sequence-level metrics.
Deterministic, stdlib-only.
"""

from __future__ import annotations

from collections import Counter
from typing import Any


def canonical_step(step: dict[str, Any]) -> tuple:
    """Produces a canonical hashable representation of a step dict."""
    return (
        int(step.get("step_no", 0)),
        str(step.get("phase", "")),
        str(step.get("system_id", "")),
        str(step.get("resource_id", "")),
        str(step.get("operation", "")),
        str(step.get("state", "")),
        str(step.get("evidence_id", "")),
    )


def step_tuple_semantic(step: dict[str, Any]) -> tuple[str, str, str, str, str]:
    """Semantic 5-tuple: (phase, system_id, resource_id, operation, state)."""
    return (
        str(step.get("phase", "")),
        str(step.get("system_id", "")),
        str(step.get("resource_id", "")),
        str(step.get("operation", "")),
        str(step.get("state", "")),
    )


def compute_status_metrics(
    preds: dict[str, dict[str, Any]],
    truths: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """
    Computes status accuracy and a 3x3 confusion matrix.
    Statuses: COMPLETE, INCOMPLETE, NOT_APPLICABLE.
    """
    statuses = ["COMPLETE", "INCOMPLETE", "NOT_APPLICABLE"]
    matrix = {t: {p: 0 for p in statuses} for t in statuses}
    correct = 0
    total = len(truths)

    for case_id, truth_obj in truths.items():
        t_status = truth_obj.get("deletion_status", "")
        p_obj = preds.get(case_id, {})
        p_status = p_obj.get("deletion_status", "")

        if t_status in matrix and p_status in matrix[t_status]:
            matrix[t_status][p_status] += 1
        if t_status == p_status:
            correct += 1

    accuracy = correct / total if total > 0 else 0.0
    return {
        "status_accuracy": accuracy,
        "confusion_matrix": matrix,
        "total_cases": total,
        "correct_cases": correct,
    }


def compute_row_exact_match(
    preds: dict[str, dict[str, Any]],
    truths: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """
    Exact match: status matches AND canonical steps array matches exactly.
    """
    exact_matches = 0
    total = len(truths)

    for case_id, truth_obj in truths.items():
        p_obj = preds.get(case_id, {})
        if truth_obj.get("deletion_status") != p_obj.get("deletion_status"):
            continue

        t_canon = [canonical_step(s) for s in truth_obj.get("steps", [])]
        p_canon = [canonical_step(s) for s in p_obj.get("steps", [])]

        if t_canon == p_canon:
            exact_matches += 1

    rate = exact_matches / total if total > 0 else 0.0
    return {
        "exact_match_rate": rate,
        "exact_matches": exact_matches,
        "total_cases": total,
    }


def compute_step_multiset_prf(
    preds: dict[str, dict[str, Any]],
    truths: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """
    Step-level precision/recall/F1 on the tuple (phase, system_id, resource_id, operation, state),
    measured as multisets per case.
    Reports micro-aggregated totals and macro mean over cases.
    """
    case_precisions = []
    case_recalls = []
    case_f1s = []

    total_intersection = 0
    total_pred_steps = 0
    total_truth_steps = 0

    for case_id, truth_obj in truths.items():
        p_obj = preds.get(case_id, {})
        t_steps = truth_obj.get("steps", [])
        p_steps = p_obj.get("steps", [])

        t_counter = Counter(step_tuple_semantic(s) for s in t_steps)
        p_counter = Counter(step_tuple_semantic(s) for s in p_steps)

        intersection = sum((t_counter & p_counter).values())
        p_count = sum(p_counter.values())
        t_count = sum(t_counter.values())

        total_intersection += intersection
        total_pred_steps += p_count
        total_truth_steps += t_count

        if p_count == 0 and t_count == 0:
            c_prec = 1.0
            c_rec = 1.0
            c_f1 = 1.0
        elif p_count == 0:
            c_prec = 0.0
            c_rec = 0.0
            c_f1 = 0.0
        elif t_count == 0:
            c_prec = 0.0
            c_rec = 0.0
            c_f1 = 0.0
        else:
            c_prec = intersection / p_count
            c_rec = intersection / t_count
            c_f1 = (2 * c_prec * c_rec / (c_prec + c_rec)) if (c_prec + c_rec) > 0 else 0.0

        case_precisions.append(c_prec)
        case_recalls.append(c_rec)
        case_f1s.append(c_f1)

    # Micro PRF
    if total_pred_steps == 0 and total_truth_steps == 0:
        micro_p, micro_r, micro_f1 = 1.0, 1.0, 1.0
    elif total_pred_steps == 0 or total_truth_steps == 0:
        micro_p, micro_r, micro_f1 = 0.0, 0.0, 0.0
    else:
        micro_p = total_intersection / total_pred_steps
        micro_r = total_intersection / total_truth_steps
        micro_f1 = (2 * micro_p * micro_r / (micro_p + micro_r)) if (micro_p + micro_r) > 0 else 0.0

    n_cases = len(truths)
    macro_p = sum(case_precisions) / n_cases if n_cases > 0 else 0.0
    macro_r = sum(case_recalls) / n_cases if n_cases > 0 else 0.0
    macro_f1 = sum(case_f1s) / n_cases if n_cases > 0 else 0.0

    return {
        "micro_precision": micro_p,
        "micro_recall": micro_r,
        "micro_f1": micro_f1,
        "macro_precision": macro_p,
        "macro_recall": macro_r,
        "macro_f1": macro_f1,
        "total_intersection": total_intersection,
        "total_pred_steps": total_pred_steps,
        "total_truth_steps": total_truth_steps,
    }


def compute_field_level_accuracy(
    preds: dict[str, dict[str, Any]],
    truths: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """
    Field-level accuracy per field (phase, operation, system_id, resource_id, state,
    evidence_id, step_no), measured over steps that align by (phase, system_id, resource_id, operation).
    """
    fields = ["phase", "operation", "system_id", "resource_id", "state", "evidence_id", "step_no"]
    field_matches = {f: 0 for f in fields}
    aligned_count = 0
    total_truth_steps = 0
    total_pred_steps = 0

    for case_id, truth_obj in truths.items():
        p_obj = preds.get(case_id, {})
        t_steps = truth_obj.get("steps", [])
        p_steps = p_obj.get("steps", [])

        total_truth_steps += len(t_steps)
        total_pred_steps += len(p_steps)

        # Index pred steps by alignment key (phase, system_id, resource_id, operation)
        pred_map: dict[tuple[str, str, str, str], list[dict[str, Any]]] = {}
        for ps in p_steps:
            k = (
                str(ps.get("phase", "")),
                str(ps.get("system_id", "")),
                str(ps.get("resource_id", "")),
                str(ps.get("operation", "")),
            )
            pred_map.setdefault(k, []).append(ps)

        for ts in t_steps:
            k = (
                str(ts.get("phase", "")),
                str(ts.get("system_id", "")),
                str(ts.get("resource_id", "")),
                str(ts.get("operation", "")),
            )
            if k in pred_map and pred_map[k]:
                ps = pred_map[k].pop(0)
                aligned_count += 1
                for f in fields:
                    if str(ts.get(f, "")) == str(ps.get(f, "")):
                        field_matches[f] += 1

    field_accuracies = {}
    for f in fields:
        field_accuracies[f] = (field_matches[f] / aligned_count) if aligned_count > 0 else 1.0

    coverage_truth = (aligned_count / total_truth_steps) if total_truth_steps > 0 else 1.0
    coverage_pred = (aligned_count / total_pred_steps) if total_pred_steps > 0 else 1.0

    return {
        "aligned_count": aligned_count,
        "total_truth_steps": total_truth_steps,
        "total_pred_steps": total_pred_steps,
        "coverage_truth": coverage_truth,
        "coverage_pred": coverage_pred,
        "field_accuracies": field_accuracies,
    }


def compute_lcs(seq1: list, seq2: list) -> list:
    """Computes longest common subsequence between two lists."""
    m, n = len(seq1), len(seq2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m):
        for j in range(n):
            if seq1[i] == seq2[j]:
                dp[i + 1][j + 1] = dp[i][j] + 1
            else:
                dp[i + 1][j + 1] = max(dp[i + 1][j], dp[i][j + 1])

    lcs = []
    i, j = m, n
    while i > 0 and j > 0:
        if seq1[i - 1] == seq2[j - 1]:
            lcs.append(seq1[i - 1])
            i -= 1
            j -= 1
        elif dp[i - 1][j] >= dp[i][j - 1]:
            i -= 1
        else:
            j -= 1
    return list(reversed(lcs))


def compute_sequence_metrics(
    preds: dict[str, dict[str, Any]],
    truths: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """
    Sequence accuracy: exact sequence order match rate and mean LCS ratio.
    """
    exact_order_matches = 0
    lcs_ratios = []
    total = len(truths)

    for case_id, truth_obj in truths.items():
        p_obj = preds.get(case_id, {})
        t_seq = [step_tuple_semantic(s) for s in truth_obj.get("steps", [])]
        p_seq = [step_tuple_semantic(s) for s in p_obj.get("steps", [])]

        if t_seq == p_seq:
            exact_order_matches += 1

        if not t_seq and not p_seq:
            lcs_ratios.append(1.0)
        elif not t_seq or not p_seq:
            lcs_ratios.append(0.0)
        else:
            lcs = compute_lcs(t_seq, p_seq)
            ratio = (2.0 * len(lcs)) / (len(t_seq) + len(p_seq))
            lcs_ratios.append(ratio)

    exact_order_rate = exact_order_matches / total if total > 0 else 0.0
    mean_lcs_ratio = sum(lcs_ratios) / len(lcs_ratios) if lcs_ratios else 1.0

    return {
        "exact_order_rate": exact_order_rate,
        "mean_lcs_ratio": mean_lcs_ratio,
        "exact_order_matches": exact_order_matches,
        "total_cases": total,
    }


def compute_status_breakdowns(
    preds: dict[str, dict[str, Any]],
    truths: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """Breakdown metrics by truth deletion status."""
    by_status: dict[str, dict[str, Any]] = {}
    for st in ["COMPLETE", "INCOMPLETE", "NOT_APPLICABLE"]:
        sub_truth = {cid: obj for cid, obj in truths.items() if obj.get("deletion_status") == st}
        sub_pred = {cid: preds.get(cid, {}) for cid in sub_truth}

        by_status[st] = {
            "count": len(sub_truth),
            "status_acc": compute_status_metrics(sub_pred, sub_truth)["status_accuracy"],
            "row_exact_match": compute_row_exact_match(sub_pred, sub_truth)["exact_match_rate"],
            "step_micro_f1": compute_step_multiset_prf(sub_pred, sub_truth)["micro_f1"],
            "seq_exact_order": compute_sequence_metrics(sub_pred, sub_truth)["exact_order_rate"],
        }
    return by_status


def compute_phase_breakdowns(
    preds: dict[str, dict[str, Any]],
    truths: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """Breakdown step precision/recall/F1 by step phase."""
    by_phase: dict[str, dict[str, Any]] = {}
    for phase in ["FINDING", "REMEDIATION", "VERIFICATION"]:
        total_inter = 0
        total_p = 0
        total_t = 0

        for case_id, t_obj in truths.items():
            p_obj = preds.get(case_id, {})
            t_steps = [s for s in t_obj.get("steps", []) if s.get("phase") == phase]
            p_steps = [s for s in p_obj.get("steps", []) if s.get("phase") == phase]

            t_c = Counter(step_tuple_semantic(s) for s in t_steps)
            p_c = Counter(step_tuple_semantic(s) for s in p_steps)

            total_inter += sum((t_c & p_c).values())
            total_p += sum(p_c.values())
            total_t += sum(t_c.values())

        if total_p == 0 and total_t == 0:
            p, r, f1 = 1.0, 1.0, 1.0
        elif total_p == 0 or total_t == 0:
            p, r, f1 = 0.0, 0.0, 0.0
        else:
            p = total_inter / total_p
            r = total_inter / total_t
            f1 = (2 * p * r / (p + r)) if (p + r) > 0 else 0.0

        by_phase[phase] = {
            "truth_steps": total_t,
            "pred_steps": total_p,
            "precision": p,
            "recall": r,
            "f1": f1,
        }
    return by_phase


def compute_error_table(
    preds: dict[str, dict[str, Any]],
    truths: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Produces error table: every case not an exact match, with first differing step and reason.
    """
    errors: list[dict[str, Any]] = []

    for case_id in sorted(truths.keys()):
        t_obj = truths[case_id]
        p_obj = preds.get(case_id, {})

        t_status = t_obj.get("deletion_status", "")
        p_status = p_obj.get("deletion_status", "")
        t_steps = t_obj.get("steps", [])
        p_steps = p_obj.get("steps", [])

        if t_status != p_status:
            errors.append({
                "case_id": case_id,
                "truth_status": t_status,
                "pred_status": p_status,
                "diff_step": "-",
                "reason": f"Status mismatch: expected {t_status}, got {p_status}",
            })
            continue

        # Check steps
        diff_found = False
        common_len = min(len(t_steps), len(p_steps))
        for idx in range(common_len):
            ts = t_steps[idx]
            ps = p_steps[idx]
            step_no = ts.get("step_no", idx + 1)

            if ts.get("operation") != ps.get("operation"):
                errors.append({
                    "case_id": case_id,
                    "truth_status": t_status,
                    "pred_status": p_status,
                    "diff_step": str(step_no),
                    "reason": f"Wrong operation: expected {ts.get('operation')}, got {ps.get('operation')}",
                })
                diff_found = True
                break
            elif ts.get("state") != ps.get("state"):
                errors.append({
                    "case_id": case_id,
                    "truth_status": t_status,
                    "pred_status": p_status,
                    "diff_step": str(step_no),
                    "reason": f"Wrong state: expected {ts.get('state')}, got {ps.get('state')}",
                })
                diff_found = True
                break
            elif (ts.get("system_id"), ts.get("resource_id")) != (ps.get("system_id"), ps.get("resource_id")):
                errors.append({
                    "case_id": case_id,
                    "truth_status": t_status,
                    "pred_status": p_status,
                    "diff_step": str(step_no),
                    "reason": f"Wrong resource: expected ({ts.get('system_id')}, {ts.get('resource_id')}), got ({ps.get('system_id')}, {ps.get('resource_id')})",
                })
                diff_found = True
                break
            elif ts.get("evidence_id") != ps.get("evidence_id"):
                errors.append({
                    "case_id": case_id,
                    "truth_status": t_status,
                    "pred_status": p_status,
                    "diff_step": str(step_no),
                    "reason": f"Wrong evidence_id: expected '{ts.get('evidence_id')}', got '{ps.get('evidence_id')}'",
                })
                diff_found = True
                break
            elif ts.get("phase") != ps.get("phase"):
                errors.append({
                    "case_id": case_id,
                    "truth_status": t_status,
                    "pred_status": p_status,
                    "diff_step": str(step_no),
                    "reason": f"Wrong phase: expected {ts.get('phase')}, got {ps.get('phase')}",
                })
                diff_found = True
                break

        if not diff_found and len(t_steps) != len(p_steps):
            if len(p_steps) < len(t_steps):
                missing_step = t_steps[len(p_steps)]
                errors.append({
                    "case_id": case_id,
                    "truth_status": t_status,
                    "pred_status": p_status,
                    "diff_step": str(missing_step.get("step_no", len(p_steps) + 1)),
                    "reason": f"Missing step: expected {missing_step.get('operation')} on ({missing_step.get('system_id')}, {missing_step.get('resource_id')})",
                })
            else:
                extra_step = p_steps[len(t_steps)]
                errors.append({
                    "case_id": case_id,
                    "truth_status": t_status,
                    "pred_status": p_status,
                    "diff_step": str(extra_step.get("step_no", len(t_steps) + 1)),
                    "reason": f"Extra step: unexpected {extra_step.get('operation')} on ({extra_step.get('system_id')}, {extra_step.get('resource_id')})",
                })

    return errors
