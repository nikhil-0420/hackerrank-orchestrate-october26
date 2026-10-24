"""
End-to-end execution pipeline for Ghost Audit.
Connects ingestion, linkage, state determination, rule evaluation, and output emission.
Supports execution Modes A (deterministic), B (A + L1/L2), and C (B + L4).
"""

from __future__ import annotations

from collections import defaultdict
import csv
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from ghost_audit.activity import ActivityLog
from ghost_audit.category import classify_category, normalize_system_id
from ghost_audit.emit import emit_output_file
from ghost_audit.evidence.coverage import CoverageIndex
from ghost_audit.evidence.normalizer import normalize_all_evidence
from ghost_audit.identity import IdentityResolver
from ghost_audit.intent import is_deletion_request
from ghost_audit.linker import Linker
from ghost_audit.llm.client import LLMClient
from ghost_audit.llm.tasks import (
    run_l1_intent_classification,
    run_l2_document_extraction,
    run_l4_linkage_adjudication,
)
from ghost_audit.loaders.manifest import EvidenceFileMeta, get_manifest_by_id, load_manifest
from ghost_audit.loaders.pdf_loader import extract_pdf_text
from ghost_audit.loaders.png_loader import extract_png_text
from ghost_audit.paths import DATASET_DIR
from ghost_audit.planner import CaseDecision, plan_case
from ghost_audit.rules import RuleEngine
from ghost_audit.spec import STATUS_NOT_APPLICABLE
from ghost_audit.state import determine_resource_state


def run_pipeline(
    dataset_dir: Union[str, Path] = DATASET_DIR,
    requests_path: Optional[Union[str, Path]] = None,
    out_path: Optional[Union[str, Path]] = None,
    config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Executes the Ghost Audit pipeline over requests.
    Configuration options:
      - mode: "A" (deterministic baseline), "B" (A + L1/L2), "C" (B + L4)
      - provider: "google" (default) or "mock"
      - model: model identifier, e.g. "gemini-2.5-flash"
      - id_sort: "natural" or "lexical"
    Writes canonical output CSV to out_path.
    Returns pipeline execution metrics and summary statistics.
    """
    cfg = config or {}
    mode = cfg.get("mode", "A").upper()
    if mode not in ("A", "B", "C"):
        mode = "A"

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

    # Initialize LLM client if in Mode B or C
    llm_client: Optional[LLMClient] = None
    if mode in ("B", "C"):
        provider = cfg.get("provider", "google")
        model = cfg.get("model", "gemini-2.5-flash")
        llm_client = LLMClient(provider=provider, model=model)

    # 1. Evidence Ingestion & Normalization
    observations, coverage_records, norm_stats = normalize_all_evidence(
        manifest_path=manifest_path,
    )
    coverage_index = CoverageIndex(coverage_records)
    total_unparsed_lines = sum(s.get("unparsed_lines", 0) for s in norm_stats.values())

    # Task L2: Document / Image structured extraction on 15 media files
    empty_extraction_files: List[str] = []
    l2_extractions: Dict[str, List[str]] = {}
    l2_rejected_hallucinations = 0
    media_file_count = 0

    if mode in ("B", "C") and llm_client:
        for f_meta in load_manifest(manifest_path):
            ext = f_meta.abs_path.suffix.lower()
            if ext in (".pdf", ".png"):
                media_file_count += 1
                doc_text = ""
                if ext == ".pdf":
                    doc_text = extract_pdf_text(f_meta.abs_path)
                elif ext == ".png":
                    doc_text = extract_png_text(f_meta.abs_path)

                l2_res, _, rejected, extracted_rids = run_l2_document_extraction(
                    client=llm_client,
                    file_id=f_meta.file_id,
                    text_content=doc_text,
                )
                l2_rejected_hallucinations += rejected
                l2_extractions[f_meta.file_id] = extracted_rids
                if len(l2_res.records) == 0:
                    empty_extraction_files.append(f_meta.file_id)

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

    # Index CLASSIFY_REQUEST rows by resource_id (account_XXXX)
    intake_by_account: Dict[str, str] = {}
    for act_row in activity_log.rows:
        if act_row.event_type == "CLASSIFY_REQUEST":
            intake_by_account[act_row.resource_id] = act_row.details

    # 3. Request Linkage
    linker = Linker(resolver, activity_log, observations)
    with open(requests_path, "r", encoding="utf-8") as f:
        requests_dict = {row["case_id"]: row for row in csv.DictReader(f)}

    linkages = linker.link_cases(requests_dict)

    # Map intake records by case_id based on attributed account resources
    intake_by_case: Dict[str, str] = {}
    for cid, linkage in linkages.items():
        for rid in linkage.attributed_resources:
            if rid in intake_by_account:
                intake_by_case[cid] = intake_by_account[rid]

    # Task L4: Linkage Adjudication on ambiguous candidates if in Mode C
    l4_safety_overrides = 0
    l4_adjudications = 0
    if mode == "C" and llm_client:
        for cid, linkage in linkages.items():
            req_info = requests_dict.get(cid, {})
            subject_info = {
                "user_id": linkage.user_id,
                "email": linkage.email,
            }
            for unattributed in linkage.unattributed_resources:
                l4_adjudications += 1
                _, _, was_override = run_l4_linkage_adjudication(
                    client=llm_client,
                    case_id=cid,
                    candidate_resource_id=unattributed.resource_id,
                    candidate_signals=unattributed.candidate_signals,
                    subject_info=subject_info,
                )
                if was_override:
                    l4_safety_overrides += 1

    # 4. Rules & Planning
    rule_engine = RuleEngine(rules_path=rules_path)

    decisions: List[CaseDecision] = []
    status_counts: Dict[str, int] = defaultdict(int)
    unattributed_by_case: Dict[str, int] = {}
    zero_resource_cases: List[str] = []
    manual_review_cases: List[Dict[str, Any]] = []
    field_disagreements: List[Dict[str, Any]] = []
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

        # Intent evaluation (L1 or deterministic)
        is_deletion = True
        if mode in ("B", "C") and llm_client:
            l1_out, is_model, manual_review = run_l1_intent_classification(
                client=llm_client,
                case_id=cid,
                request_text=req_text,
                intake_records=intake_by_case,
            )
            is_deletion = l1_out.authorizes_deletion
            if manual_review:
                manual_review_cases.append(manual_review)
            # Check agreement with deterministic classifier
            det_is_del = is_deletion_request(req_text)
            if is_deletion != det_is_del:
                field_disagreements.append({
                    "case_id": cid,
                    "field": "authorizes_deletion",
                    "model_value": is_deletion,
                    "deterministic_value": det_is_del,
                    "reason": "L1 intent disagreement",
                })
        else:
            is_deletion = is_deletion_request(req_text)

        if not is_deletion:
            dec = CaseDecision(
                case_id=cid,
                deletion_status=STATUS_NOT_APPLICABLE,
                treatments={},
                steps=[],
            )
            decisions.append(dec)
            status_counts[dec.deletion_status] += 1
            continue

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
    id_sort = cfg.get("id_sort", "natural")
    emit_output_file(decisions, out_path, id_sort=id_sort)

    total_cases = len(decisions)
    stats: Dict[str, Any] = {
        "mode": mode,
        "total_cases": total_cases,
        "status_counts": dict(status_counts),
        "not_applicable_count": status_counts.get("NOT_APPLICABLE", 0),
        "resources_per_case_avg": (total_resources / total_cases) if total_cases > 0 else 0.0,
        "total_unattributed": sum(unattributed_by_case.values()),
        "unattributed_by_case": unattributed_by_case,
        "zero_resource_cases": zero_resource_cases,
        "total_undecided": total_undecided,
        "unparsed_log_lines": total_unparsed_lines,
        "media_file_count": media_file_count,
        "empty_extractions_count": len(empty_extraction_files),
        "empty_extraction_files": empty_extraction_files,
        "l2_rejected_hallucinations": l2_rejected_hallucinations,
        "l4_adjudications_count": l4_adjudications,
        "l4_safety_overrides_count": l4_safety_overrides,
        "manual_review_cases": manual_review_cases,
        "field_disagreements": field_disagreements,
        "schema_failure_rate": llm_client.schema_failure_rate() if llm_client else 0.0,
        "usage_summary": llm_client.ledger.summary() if llm_client else None,
        "silent_failures": [f.to_dict() for f in llm_client.silent_failures] if llm_client else [],
    }
    return stats
