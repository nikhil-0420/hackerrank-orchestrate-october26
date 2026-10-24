"""
End-to-end execution pipeline for Ghost Audit.
Connects ingestion, linkage, state determination, rule evaluation, and output emission.
"""

from __future__ import annotations

from collections import defaultdict
import csv
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ghost_audit.activity import ActivityLog
from ghost_audit.category import classify_category, normalize_system_id
from ghost_audit.emit import emit_output_file
from ghost_audit.evidence.coverage import CoverageIndex
from ghost_audit.evidence.normalizer import normalize_all_evidence
from ghost_audit.identity import IdentityResolver
from ghost_audit.linker import Linker
from ghost_audit.loaders.manifest import get_manifest_by_id
from ghost_audit.paths import DATASET_DIR
from ghost_audit.planner import CaseDecision, plan_case
from ghost_audit.rules import RuleEngine
from ghost_audit.state import determine_resource_state


def run_pipeline(
    dataset_dir: Union[str, Path] = DATASET_DIR,
    requests_path: Optional[Union[str, Path]] = None,
    out_path: Optional[Union[str, Path]] = None,
    config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Executes the Ghost Audit deterministic pipeline over requests.
    Writes canonical output CSV to out_path.
    Returns pipeline execution metrics and summary statistics.
    """
    dataset_dir = Path(dataset_dir)
    if requests_path is None:
        requests_path = dataset_dir / "deletion_requests.csv"
    else:
        requests_path = Path(requests_path)

    if out_path is None:
        out_path = Path("output.csv")
    else:
        out_path = Path(out_path)

    manifest_path = dataset_dir / "evidence_files.csv"
    manifest = get_manifest_by_id(manifest_path)
    activity_path = dataset_dir / "system_activity.csv"
    identities_path = dataset_dir / "user_identities.csv"
    audit_log_path = dataset_dir / "user_audit_log.csv"
    rules_path = dataset_dir / "deletion_rules.csv"
    evidence_dir = dataset_dir / "evidence"

    # 1. Evidence Ingestion & Normalization
    observations, coverage_records, norm_stats = normalize_all_evidence(
        manifest_path=manifest_path,
    )
    coverage_index = CoverageIndex(coverage_records)

    obs_by_res = defaultdict(list)
    for obs in observations:
        if obs.resource_id:
            obs_by_res[obs.resource_id].append(obs)

    # 2. Activity & Identity Resolution
    activity_log = ActivityLog(path=activity_path)
    resolver = IdentityResolver(
        identities_path=identities_path,
        audit_log_path=audit_log_path if audit_log_path.exists() else None,
    )

    # 3. Request Linkage
    linker = Linker(resolver, activity_log, observations)
    with open(requests_path, "r", encoding="utf-8") as f:
        requests_dict = {row["case_id"]: row for row in csv.DictReader(f)}

    linkages = linker.link_cases(requests_dict)

    # 4. Rules & Planning
    rule_engine = RuleEngine(rules_path=rules_path)

    decisions: List[CaseDecision] = []
    status_counts: Dict[str, int] = defaultdict(int)
    unattributed_by_case: Dict[str, int] = {}
    zero_resource_cases: List[str] = []
    total_resources = 0
    total_undecided = 0

    for cid, req in requests_dict.items():
        linkage = linkages.get(cid)
        if not linkage:
            continue

        audit_at = req.get("audit_at", "")
        req_text = req.get("request_text", "")

        unattributed_count = len(linkage.unattributed_resources)
        unattributed_by_case[cid] = unattributed_count

        resource_states = {}
        categories = {}
        attributed_count = len(linkage.attributed_resources)
        total_resources += attributed_count
        if attributed_count == 0:
            zero_resource_cases.append(cid)

        for rid, attr in linkage.attributed_resources.items():
            res_obs = obs_by_res.get(rid, [])
            sys_id = normalize_system_id(attr.system_id)
            st = determine_resource_state(
                resource_id=rid,
                system_id=sys_id,
                observations=res_obs,
                audit_at=audit_at,
                coverage_index=coverage_index,
            )
            cat = classify_category(
                system_id=sys_id,
                collection=st.supporting_observation.collection if st.supporting_observation else "",
                state=st.supporting_observation.state if st.supporting_observation else {},
                resource_id=rid,
            )
            resource_states[rid] = st
            categories[rid] = cat

        dec = plan_case(
            case_id=cid,
            request_text=req_text,
            audit_at=audit_at,
            case_linkage=linkage,
            resource_states=resource_states,
            categories=categories,
            rule_engine=rule_engine,
            obs_by_res=obs_by_res,
            coverage_index=coverage_index,
            manifest=manifest,
        )
        decisions.append(dec)
        status_counts[dec.deletion_status] += 1

    # 5. Emit output CSV
    id_sort = config.get("id_sort", "natural") if config else "natural"
    emit_output_file(decisions, out_path, id_sort=id_sort)

    total_cases = len(decisions)
    stats = {
        "total_cases": total_cases,
        "status_counts": dict(status_counts),
        "not_applicable_count": status_counts.get("NOT_APPLICABLE", 0),
        "resources_per_case_avg": (total_resources / total_cases) if total_cases > 0 else 0.0,
        "total_unattributed": sum(unattributed_by_case.values()),
        "unattributed_by_case": unattributed_by_case,
        "zero_resource_cases": zero_resource_cases,
        "total_undecided": total_undecided,
    }
    return stats
