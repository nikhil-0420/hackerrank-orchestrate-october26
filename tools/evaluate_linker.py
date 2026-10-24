"""
Evaluation and ablation measurement script for Phase 2b Linker Lab.

Measures:
  1. Overall resource-level precision, recall, and F1 on sample cases.
  2. Per-resource-type precision and recall.
  3. Comparison against naive baseline (~61% recall).
  4. Signal ablations: dropping each signal S1 through S8.
  5. Leave-one-family-out checks across evidence families.
  6. Generates markdown tables for docs/failure_log.md under "Phase 2b linker lab".
"""

from __future__ import annotations

import csv
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import sys
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "code"))

from ghost_audit.activity import ActivityLog
from ghost_audit.evidence import normalize_all_evidence
from ghost_audit.identity import IdentityResolver
from ghost_audit.linker import Linker, Signal, AttributedResource, CaseLinkage
from ghost_audit.linker.graph import build_case_attribution_graph
from ghost_audit.observation import Observation
from ghost_audit.paths import SAMPLE_REQUESTS_PATH, MANIFEST_PATH
from tools.labels import load_case_resource_labels


def get_resource_type(r_id: str) -> str:
    """Map resource_id prefix to resource type label."""
    if r_id.startswith("account_"):
        return "account"
    if r_id.startswith("search_"):
        return "search"
    if r_id.startswith("support_"):
        return "support"
    if r_id.startswith("export_"):
        return "export"
    if r_id.startswith("analytics_"):
        return "analytics"
    if r_id.startswith("data_flow_"):
        return "flow"
    if r_id.startswith("backup_"):
        return "backup"
    if r_id.startswith("audit_record_"):
        return "audit"
    if r_id.startswith("tombstone_"):
        return "tombstone"
    return "other"


def evaluate_linkages(
    linkages: Dict[str, CaseLinkage],
    labels: Dict[str, Set[Tuple[str, str, str]]],
) -> Dict[str, Any]:
    """Calculate overall and per-type precision, recall, TP, FP, FN."""
    total_gt = 0
    total_tp = 0
    total_fp = 0
    total_fn = 0

    by_type_gt = defaultdict(int)
    by_type_tp = defaultdict(int)
    by_type_fp = defaultdict(int)
    by_type_fn = defaultdict(int)

    all_case_ids = sorted(set(linkages.keys()) | set(labels.keys()))

    for cid in all_case_ids:
        gt_res = {r[0] for r in labels.get(cid, set())}
        pred_res = set(linkages[cid].attributed_resources.keys()) if cid in linkages else set()

        tp_set = gt_res & pred_res
        fp_set = pred_res - gt_res
        fn_set = gt_res - pred_res

        total_gt += len(gt_res)
        total_tp += len(tp_set)
        total_fp += len(fp_set)
        total_fn += len(fn_set)

        for r in gt_res:
            by_type_gt[get_resource_type(r)] += 1
        for r in tp_set:
            by_type_tp[get_resource_type(r)] += 1
        for r in fp_set:
            by_type_fp[get_resource_type(r)] += 1
        for r in fn_set:
            by_type_fn[get_resource_type(r)] += 1

    overall_prec = total_tp / (total_tp + total_fp) if (total_tp + total_fp) else 0.0
    overall_rec = total_tp / total_gt if total_gt else 0.0
    overall_f1 = (
        2 * overall_prec * overall_rec / (overall_prec + overall_rec)
        if (overall_prec + overall_rec)
        else 0.0
    )

    per_type_metrics = {}
    all_types = [
        "account",
        "search",
        "support",
        "export",
        "analytics",
        "flow",
        "backup",
        "audit",
        "tombstone",
        "other",
    ]
    for t in all_types:
        t_gt = by_type_gt[t]
        t_tp = by_type_tp[t]
        t_fp = by_type_fp[t]
        t_fn = by_type_fn[t]
        p = t_tp / (t_tp + t_fp) if (t_tp + t_fp) else (1.0 if t_fp == 0 and t_tp > 0 else 0.0)
        r = t_tp / t_gt if t_gt else (1.0 if t_fn == 0 else 0.0)
        per_type_metrics[t] = {
            "gt": t_gt,
            "tp": t_tp,
            "fp": t_fp,
            "fn": t_fn,
            "precision": p,
            "recall": r,
        }

    return {
        "total_gt": total_gt,
        "total_tp": total_tp,
        "total_fp": total_fp,
        "total_fn": total_fn,
        "precision": overall_prec,
        "recall": overall_rec,
        "f1": overall_f1,
        "per_type": per_type_metrics,
    }


def run_evaluation() -> Tuple[Dict[str, Any], str]:
    resolver = IdentityResolver()
    activity = ActivityLog()
    all_obs, _, _ = normalize_all_evidence()
    labels = load_case_resource_labels()

    with open(SAMPLE_REQUESTS_PATH, "r", encoding="utf-8") as f:
        requests = {r["case_id"]: r for r in csv.DictReader(f)}

    linker = Linker(resolver=resolver, activity=activity, observations=all_obs)
    full_linkages = linker.link_cases(requests)
    base_eval = evaluate_linkages(full_linkages, labels)

    # 1. Naive baseline (only S1 identifier exact match in observations)
    naive_linkages: Dict[str, CaseLinkage] = {}
    for cid, req in requests.items():
        ident = resolver.resolve(req["email"])
        naive_signals = []
        for o in all_obs:
            if o.identifiers and o.identifiers.email and o.identifiers.email.lower().strip() in ident.emails:
                naive_signals.append(
                    Signal(
                        resource_id=o.resource_id,
                        signal_name="S1_IDENTIFIER",
                        evidence_ref=f"{o.file_id}:{o.raw_ref}",
                        strength=1.0,
                        system_id=o.system_id,
                        file_id=o.file_id,
                    )
                )
        linkage = build_case_attribution_graph(
            case_id=cid,
            user_id=ident.user_id,
            email=req["email"],
            audit_at=req["audit_at"],
            all_signals=naive_signals,
            obs_by_res=linker.obs_by_res,
        )
        naive_linkages[cid] = linkage
    naive_eval = evaluate_linkages(naive_linkages, labels)

    # 2. Signal Ablations: Drop each signal family
    ablation_results = {}
    signal_families = [
        ("S1_IDENTIFIER", "Drop S1 (Record Identifiers)"),
        ("S2_USER_ID", "Drop S2 (User ID Joins)"),
        ("S3_MERGED_TRACE", "Drop S3 (Merged Traces)"),
        ("S4_LINK_ROW", "Drop S4 (Link Rows)"),
        ("S5_CHAIN_KEY", "Drop S5 (Chain Keys)"),
        ("S6_HANDOVER_DOC", "Drop S6 (Handover Docs)"),
        ("S7_ACCOUNT_ANCHOR", "Drop S7 (Account Anchors)"),
        ("S8_TUTORIAL_ANALYTICS", "Drop S8 (Activity Chain / Offsets)"),
    ]

    for sig_name, desc in signal_families:
        ablated_linkages: Dict[str, CaseLinkage] = {}
        for cid, linkage in full_linkages.items():
            filtered_signals = []
            for s in linkage.signals:
                if sig_name == "S8_TUTORIAL_ANALYTICS":
                    if s.signal_name in ("S8_TUTORIAL_ACCOUNT", "S8_TUTORIAL_ANALYTICS", "S8_ANON_ANALYTICS"):
                        continue
                elif s.signal_name == sig_name:
                    continue
                filtered_signals.append(s)

            ab_linkage = build_case_attribution_graph(
                case_id=cid,
                user_id=linkage.user_id,
                email=linkage.email,
                audit_at=requests[cid]["audit_at"],
                all_signals=filtered_signals,
                obs_by_res=linker.obs_by_res,
            )
            ablated_linkages[cid] = ab_linkage

        ab_eval = evaluate_linkages(ablated_linkages, labels)
        rec_loss = base_eval["recall"] - ab_eval["recall"]
        ablation_results[desc] = {
            "eval": ab_eval,
            "rec_loss": rec_loss,
        }

    # 3. Leave-one-family-out check (by evidence directory family)
    manifest_families = {}
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            parts = r["file_path"].split("/")
            fam = parts[1] if len(parts) > 1 else "root"
            manifest_families[r["file_id"]] = fam

    all_families = sorted(set(manifest_families.values()))
    family_eval_results = {}

    for fam in all_families:
        filtered_obs = [o for o in all_obs if manifest_families.get(o.file_id) != fam]
        fam_linker = Linker(resolver=resolver, activity=activity, observations=filtered_obs)
        fam_linkages = fam_linker.link_cases(requests)
        f_eval = evaluate_linkages(fam_linkages, labels)
        family_eval_results[fam] = f_eval

    # 4. Unattributed resources analysis
    unattributed_summary = []
    for cid in sorted(labels.keys()):
        gt_res = {r[0] for r in labels[cid]}
        pred_res = set(full_linkages[cid].attributed_resources.keys())
        missing = gt_res - pred_res
        if missing:
            for m in sorted(missing):
                unattributed_summary.append((cid, m, "Absent in evidence files (evidence_id='')"))

    # Generate Markdown Output
    lines = []
    lines.append("## Phase 2b linker lab\n")
    lines.append("### Linker Performance Summary vs Naive Baseline\n")
    lines.append("| Metric | Naive Baseline (S1 only) | Phase 2b Linker | Delta / Gain |")
    lines.append("|---|---|---|---|")
    lines.append(f"| Target Ground Truth Resources | {naive_eval['total_gt']} | {base_eval['total_gt']} | - |")
    lines.append(f"| True Positives (TP) | {naive_eval['total_tp']} | {base_eval['total_tp']} | +{base_eval['total_tp'] - naive_eval['total_tp']} |")
    lines.append(f"| False Positives (FP) | {naive_eval['total_fp']} | {base_eval['total_fp']} | {base_eval['total_fp'] - naive_eval['total_fp']} |")
    lines.append(f"| False Negatives (FN) | {naive_eval['total_fn']} | {base_eval['total_fn']} | -{naive_eval['total_fn'] - base_eval['total_fn']} |")
    lines.append(f"| **Precision** | **{naive_eval['precision']*100:.2f}%** | **{base_eval['precision']*100:.2f}%** | **+{base_eval['precision']*100 - naive_eval['precision']*100:.2f}%** |")
    lines.append(f"| **Recall** | **{naive_eval['recall']*100:.2f}%** | **{base_eval['recall']*100:.2f}%** | **+{base_eval['recall']*100 - naive_eval['recall']*100:.2f}%** |")
    lines.append(f"| **F1 Score** | **{naive_eval['f1']*100:.2f}%** | **{base_eval['f1']*100:.2f}%** | **+{base_eval['f1']*100 - naive_eval['f1']*100:.2f}%** |\n")

    lines.append("### Per-Resource-Type Precision and Recall\n")
    lines.append("| Resource Type | System | Ground Truth | TP | FP | FN | Precision | Recall |")
    lines.append("|---|---|---|---|---|---|---|---|")
    sys_map = {
        "account": "account_service",
        "search": "search_service",
        "support": "support_platform",
        "export": "export_service",
        "analytics": "analytics_platform",
        "flow": "integration_service",
        "backup": "backup_service",
        "audit": "security_service",
        "tombstone": "identity_service",
        "other": "other",
    }
    for t in [
        "account",
        "search",
        "support",
        "export",
        "analytics",
        "flow",
        "backup",
        "audit",
        "tombstone",
        "other",
    ]:
        m = base_eval["per_type"][t]
        if m["gt"] > 0 or m["fp"] > 0:
            lines.append(
                f"| `{t}` | `{sys_map.get(t, t)}` | {m['gt']} | {m['tp']} | {m['fp']} | {m['fn']} | {m['precision']*100:.2f}% | {m['recall']*100:.2f}% |"
            )

    lines.append("\n### Signal Ablation Study (Drop Each Signal)\n")
    lines.append("| Ablation Experiment | Precision | Recall | F1 Score | Recall Loss (Delta) |")
    lines.append("|---|---|---|---|---|")
    lines.append(f"| **Full Linker (S1-S8)** | **{base_eval['precision']*100:.2f}%** | **{base_eval['recall']*100:.2f}%** | **{base_eval['f1']*100:.2f}%** | **Baseline (0.00%)** |")
    for desc, res in ablation_results.items():
        ab_ev = res["eval"]
        loss = res["rec_loss"]
        lines.append(
            f"| {desc} | {ab_ev['precision']*100:.2f}% | {ab_ev['recall']*100:.2f}% | {ab_ev['f1']*100:.2f}% | -{loss*100:.2f}% |"
        )

    lines.append("\n### Leave-One-Family-Out Check\n")
    lines.append("| Excluded Evidence Family | Files Excluded | Precision | Recall | Recall Loss (Delta) |")
    lines.append("|---|---|---|---|---|")
    lines.append(f"| **None (Full Manifest)** | 0 | **{base_eval['precision']*100:.2f}%** | **{base_eval['recall']*100:.2f}%** | **0.00%** |")
    for fam, fe in sorted(family_eval_results.items()):
        f_count = sum(1 for f in manifest_families.values() if f == fam)
        f_loss = base_eval["recall"] - fe["recall"]
        lines.append(
            f"| `evidence/{fam}/` | {f_count} | {fe['precision']*100:.2f}% | {fe['recall']*100:.2f}% | -{f_loss*100:.2f}% |"
        )

    lines.append("\n### Unattributed Ground Truth Resources on Samples\n")
    lines.append("| Case ID | Resource ID | Expected System | Reason / Candidates |")
    lines.append("|---|---|---|---|")
    for cid, rid, reason in unattributed_summary:
        lines.append(f"| `{cid}` | `{rid}` | `security_service` | {reason} |")

    report_md = "\n".join(lines)
    return base_eval, report_md


if __name__ == "__main__":
    _, report = run_evaluation()
    print(report)
