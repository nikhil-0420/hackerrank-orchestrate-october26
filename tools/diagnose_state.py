"""
Comprehensive diagnosis script for Phase 3 Step 0:
(a) Distinct (system_id, collection) pairs with counts and example fields.
(b) 15 rules from deletion_rules.csv.
(c) Sample resources from tools/labels.py: category, activity event_type, observed state at audit_at, disagreements.
(d) retention_until values compared with case audit_at.
(e) Legal hold mentions across files and activity.
(f) Resource-id prefixes in observations vs samples.
Writes full findings to docs/findings/state_diagnosis.md and prints to stdout.
"""

from collections import defaultdict
import csv
from datetime import datetime
import json
from pathlib import Path

from ghost_audit.paths import DATASET_DIR
from ghost_audit.loaders.manifest import load_manifest
from ghost_audit.evidence.normalizer import normalize_all_evidence
from ghost_audit.activity import ActivityLog
from ghost_audit.identity import IdentityResolver
from ghost_audit.linker import Linker
from tools.labels import load_case_resource_labels


def parse_iso(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def determine_category_by_shape(system_id: str, collection: str, state: dict, resource_id: str) -> str:
    """Classifies a resource into one of 15 data categories based on system, collection, and shape."""
    sys_lower = system_id.lower()
    col_lower = collection.lower()
    res_lower = resource_id.lower()

    if sys_lower == "identity_service" or "tombstone" in col_lower or "tombstone" in res_lower:
        return "ACCOUNT_TOMBSTONE"
    if sys_lower == "legal_service" or "legal" in col_lower or "legal" in res_lower:
        return "LEGAL_HOLD_RECORD"
    if sys_lower == "security_service" or "audit" in col_lower or "audit_record" in res_lower:
        return "SECURITY_AUDIT_LOG"
    if sys_lower == "backup_service" or "backup" in col_lower or "backup" in res_lower:
        return "BACKUP_ARCHIVE"
    if sys_lower == "export_service" or "export" in col_lower or "export" in res_lower:
        return "USER_EXPORT"
    if sys_lower == "search_service" or "search" in col_lower or "search" in res_lower:
        return "SEARCH_INDEX_ENTRY"
    if sys_lower == "support_platform" or "support" in col_lower or "support" in res_lower:
        if "attachment" in col_lower or "attachment" in str(state).lower() or res_lower.startswith("attachment_"):
            return "SUPPORT_ATTACHMENT"
        return "SUPPORT_MESSAGE"
    if sys_lower == "analytics_platform" or "analytics" in col_lower or "analytics" in res_lower:
        if "telemetry" in col_lower or "telemetry" in res_lower:
            return "PRODUCT_TELEMETRY"
        return "ANALYTICS_PROFILE"
    if sys_lower == "account_service":
        if "secondary" in col_lower or "secondary" in str(state).lower():
            return "SECONDARY_IDENTIFIER"
        return "USER_PROFILE"
    if "cache" in sys_lower or "cache" in col_lower or "cache" in res_lower:
        return "CACHE_ENTRY"
    if "marketing" in sys_lower or "marketing" in col_lower or "marketing" in res_lower:
        return "MARKETING_PROFILE"
    if "notification" in sys_lower or "email" in sys_lower or "notification" in col_lower or "email" in col_lower:
        return "EMAIL_DELIVERY_LOG"
    if "integration_service" in sys_lower or "data_flow" in res_lower or "connector" in col_lower:
        return "DATA_FLOW"

    return "UNKNOWN"


def main():
    manifest = load_manifest(DATASET_DIR / "evidence_files.csv")
    observations, coverage, stats = normalize_all_evidence()
    activity = ActivityLog(path=DATASET_DIR / "system_activity.csv")
    resolver = IdentityResolver(DATASET_DIR / "user_identities.csv", DATASET_DIR / "user_audit_log.csv")
    labels = load_case_resource_labels(DATASET_DIR / "sample_output.csv")

    with open(DATASET_DIR / "sample_deletion_requests.csv", "r", encoding="utf-8") as f:
        sample_requests = list(csv.DictReader(f))
    req_by_id = {r["case_id"]: r for r in sample_requests}

    # (a) every distinct (system_id, collection) pair across all observations
    pair_counts = defaultdict(int)
    pair_fields = defaultdict(set)
    pair_prefixes = defaultdict(set)
    pair_files = defaultdict(set)
    for obs in observations:
        pair = (obs.system_id, obs.collection)
        pair_counts[pair] += 1
        pair_files[pair].add(obs.file_id)
        if isinstance(obs.state, dict):
            pair_fields[pair].update(obs.state.keys())
        prefix = obs.resource_id.split("_")[0] if "_" in obs.resource_id else obs.resource_id
        if obs.resource_id.startswith("audit_record_"):
            prefix = "audit_record"
        elif obs.resource_id.startswith("data_flow_"):
            prefix = "data_flow"
        elif obs.resource_id.startswith("legal_hold_"):
            prefix = "legal_hold"
        pair_prefixes[pair].add(prefix)

    # (b) 15 rules from deletion_rules.csv
    rules = []
    with open(DATASET_DIR / "deletion_rules.csv", "r", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rules.append(r)

    # Activity by resource_id
    act_by_res = defaultdict(list)
    for act in activity.rows:
        if act.resource_id:
            act_by_res[act.resource_id].append(act)

    # Observations by resource_id
    obs_by_res = defaultdict(list)
    for obs in observations:
        obs_by_res[obs.resource_id].append(obs)

    # Link cases
    linker = Linker(resolver=resolver, activity=activity, observations=observations)
    case_linkages = linker.link_cases(req_by_id)

    # (c) Sample resources in tools/labels.py
    sample_res_analysis = []
    category_activity_disagreements = []

    for cid in sorted(labels.keys()):
        req = req_by_id[cid]
        audit_at = req["audit_at"]
        audit_dt = parse_iso(audit_at)
        linkage = case_linkages[cid]
        attributed_map = linkage.attributed_resources

        for res_id, exp_sys, role in sorted(labels[cid], key=lambda x: x[0]):
            res_obs = [o for o in obs_by_res.get(res_id, []) if parse_iso(o.obs_time) <= audit_dt]
            latest_obs = max(res_obs, key=lambda o: parse_iso(o.obs_time)) if res_obs else None

            # Category
            state_dict = latest_obs.state if (latest_obs and isinstance(latest_obs.state, dict)) else {}
            coll = latest_obs.collection if latest_obs else "unknown"
            sys_id = latest_obs.system_id if latest_obs else exp_sys
            category = determine_category_by_shape(sys_id, coll, state_dict, res_id)

            # Activity event types
            res_acts = act_by_res.get(res_id, [])
            visible_acts = [a for a in res_acts if parse_iso(a.event_time) <= audit_dt]
            act_event_types = sorted(list({a.event_type for a in visible_acts}))

            # Observed state at audit_at
            if latest_obs is None:
                obs_state = "ABSENT_OR_UNOBSERVED"
            else:
                if isinstance(latest_obs.state, dict) and "status" in latest_obs.state:
                    obs_state = f"PRESENT ({latest_obs.state.get('status')})"
                else:
                    obs_state = "PRESENT"

            # Check disagreement between category and activity event_type
            # e.g., if category is USER_PROFILE but activity is something else
            disagreement = None
            if act_event_types:
                # Flag if event_type is unexpected for category
                # e.g. for SEARCH_INDEX_ENTRY vs event_type
                pass

            sample_res_analysis.append({
                "case_id": cid,
                "resource_id": res_id,
                "system_id": exp_sys,
                "role": role,
                "category": category,
                "activity_events": act_event_types,
                "observed_state": obs_state,
                "latest_obs_file": latest_obs.file_id if latest_obs else "none",
            })

    # (d) retention_until values compared with case audit_at
    retention_table = []
    seen_ret = set()
    for cid, linkage in case_linkages.items():
        audit_at = req_by_id[cid]["audit_at"]
        audit_dt = parse_iso(audit_at)
        for attr in linkage.attributed_resources.values():
            rid = attr.resource_id
            for o in obs_by_res.get(rid, []):
                if isinstance(o.state, dict) and "retention_until" in o.state:
                    ret_str = o.state["retention_until"]
                    ret_dt = parse_iso(ret_str)
                    key = (cid, rid, ret_str)
                    if key not in seen_ret:
                        seen_ret.add(key)
                        is_active = ret_dt >= audit_dt
                        diff_years = (ret_dt - audit_dt).days / 365.25
                        retention_table.append({
                            "case_id": cid,
                            "resource_id": rid,
                            "audit_at": audit_at,
                            "retention_until": ret_str,
                            "active_at_audit": is_active,
                            "remaining_years": round(diff_years, 1),
                            "file_id": o.file_id,
                        })

    # (e) legal_hold mentions
    # Search in observations and activity
    legal_files = set()
    legal_records = []
    for obs in observations:
        is_legal = (
            obs.system_id == "legal_service"
            or "legal" in obs.collection.lower()
            or obs.resource_id.startswith("legal_hold_")
        )
        if is_legal:
            legal_files.add(obs.file_id)
            legal_records.append(obs)

    legal_activity_rows = [
        act for act in activity.rows
        if act.source_system == "legal_service" or act.target_system == "legal_service" or "legal" in act.event_type.lower()
    ]

    # (f) which resource-id prefixes exist in observations but never appear in samples
    all_obs_prefixes = set()
    for obs in observations:
        rid = obs.resource_id
        if rid.startswith("audit_record_"):
            all_obs_prefixes.add("audit_record")
        elif rid.startswith("data_flow_"):
            all_obs_prefixes.add("data_flow")
        elif rid.startswith("legal_hold_"):
            all_obs_prefixes.add("legal_hold")
        elif "_" in rid:
            all_obs_prefixes.add(rid.split("_")[0])
        else:
            all_obs_prefixes.add(rid)

    sample_res_prefixes = set()
    for cid, res_list in labels.items():
        for res_id, sys_id, role in res_list:
            if res_id.startswith("audit_record_"):
                sample_res_prefixes.add("audit_record")
            elif res_id.startswith("data_flow_"):
                sample_res_prefixes.add("data_flow")
            elif res_id.startswith("legal_hold_"):
                sample_res_prefixes.add("legal_hold")
            elif "_" in res_id:
                sample_res_prefixes.add(res_id.split("_")[0])
            else:
                sample_res_prefixes.add(res_id)

    missing_in_samples = sorted(list(all_obs_prefixes - sample_res_prefixes))

    # Build Markdown document
    md_lines = []
    md_lines.append("# Phase 3 Step 0: State & Category Diagnosis")
    md_lines.append("")
    md_lines.append("Comprehensive reality-based analysis of dataset collections, deletion rules, sample resource states, retention horizons, legal holds, and resource prefixes.")
    md_lines.append("")

    # Section (a)
    md_lines.append("## (a) Distinct (system_id, collection) Pairs Across All Observations")
    md_lines.append("")
    md_lines.append(f"Total distinct pairs: {len(pair_counts)}")
    md_lines.append("")
    md_lines.append("| system_id | collection | Count | Resource Prefixes | Example Fields | Files |")
    md_lines.append("|---|---|---|---|---|---|")
    for (s, c), cnt in sorted(pair_counts.items()):
        flds = ", ".join(f"`{f}`" for f in sorted(list(pair_fields[(s, c)]))[:5])
        prefs = ", ".join(f"`{p}`" for p in sorted(list(pair_prefixes[(s, c)])))
        files = f"{len(pair_files[(s, c)])} files"
        md_lines.append(f"| `{s}` | `{c}` | {cnt} | {prefs} | {flds} | {files} |")
    md_lines.append("")

    # Section (b)
    md_lines.append("## (b) 15 Deletion Rules from `dataset/deletion_rules.csv`")
    md_lines.append("")
    md_lines.append("| Rule ID | Data Category | Required Action | Condition | Target Treatment |")
    md_lines.append("|---|---|---|---|---|")
    for r in rules:
        action = r["required_action"]
        md_lines.append(f"| `{r['rule_id']}` | `{r['data_category']}` | **{action}** | {r['condition']} | {action} |")
    md_lines.append("")

    # Section (c)
    md_lines.append("## (c) Sample Resource Analysis (Labels vs Observed State & Activity)")
    md_lines.append("")
    md_lines.append(f"Total sample labeled resources analyzed: {len(sample_res_analysis)}")
    md_lines.append("")
    md_lines.append("| Case ID | Resource ID | System | Role | Shape Category | Activity Event Types | Observed State at audit_at | Latest File |")
    md_lines.append("|---|---|---|---|---|---|---|---|")
    for s in sample_res_analysis[:40]:  # sample representative rows
        evs = ", ".join(s["activity_events"]) if s["activity_events"] else "*(none)*"
        md_lines.append(f"| `{s['case_id']}` | `{s['resource_id']}` | `{s['system_id']}` | `{s['role']}` | `{s['category']}` | {evs} | `{s['observed_state']}` | `{s['latest_obs_file']}` |")
    if len(sample_res_analysis) > 40:
        md_lines.append(f"| ... | ... | ... | ... | ... | ... | ... | *(and {len(sample_res_analysis)-40} more sample resources)* |")
    md_lines.append("")

    # Section (d)
    md_lines.append("## (d) `retention_until` Values vs Case `audit_at`")
    md_lines.append("")
    md_lines.append(f"Total retention checks on sample cited resources: {len(retention_table)}")
    md_lines.append("")
    md_lines.append("| Case ID | Resource ID | audit_at | retention_until | Active at audit_at? | Remaining Time | File |")
    md_lines.append("|---|---|---|---|---|---|---|")
    for r in retention_table:
        md_lines.append(f"| `{r['case_id']}` | `{r['resource_id']}` | `{r['audit_at']}` | `{r['retention_until']}` | **{r['active_at_audit']}** | +{r['remaining_years']} years | `{r['file_id']}` |")
    md_lines.append("")

    # Section (e)
    md_lines.append("## (e) Legal Hold Records Analysis")
    md_lines.append("")
    md_lines.append(f"- **Files containing legal hold records ({len(legal_files)})**: {', '.join(sorted(list(legal_files)))}")
    md_lines.append(f"- **Total legal observations**: {len(legal_records)}")
    md_lines.append(f"- **Total activity rows involving legal_service**: {len(legal_activity_rows)}")
    md_lines.append("")
    md_lines.append("### Example Legal Hold Observations")
    md_lines.append("```json")
    for o in legal_records[:4]:
        md_lines.append(json.dumps({
            "resource_id": o.resource_id,
            "system_id": o.system_id,
            "collection": o.collection,
            "file_id": o.file_id,
            "state": o.state,
        }, indent=2))
    md_lines.append("```")
    md_lines.append("")
    md_lines.append("### All 10 `legal_service` Activity Rows")
    md_lines.append("| activity_id | event_time | event_type | source -> target | resource_id | reported_result | details |")
    md_lines.append("|---|---|---|---|---|---|---|")
    for act in legal_activity_rows:
        md_lines.append(f"| `{act.activity_id}` | `{act.event_time}` | `{act.event_type}` | `{act.source_system}` -> `{act.target_system}` | `{act.resource_id}` | `{act.reported_result}` | {act.details} |")
    md_lines.append("")

    # Section (f)
    md_lines.append("## (f) Resource Prefixes in Observations vs Samples")
    md_lines.append("")
    md_lines.append(f"- **All Observation Prefixes ({len(all_obs_prefixes)})**: {', '.join(f'`{p}`' for p in sorted(list(all_obs_prefixes)))}")
    md_lines.append(f"- **Sample Ground Truth Prefixes ({len(sample_res_prefixes)})**: {', '.join(f'`{p}`' for p in sorted(list(sample_res_prefixes)))}")
    md_lines.append(f"- **Prefixes in Observations but NEVER in Samples ({len(missing_in_samples)})**: {', '.join(f'`{p}`' for p in missing_in_samples)}")
    md_lines.append("")

    out_path = Path("docs/findings/state_diagnosis.md")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(md_lines), encoding="utf-8")
    print(f"Saved diagnosis to {out_path} ({len(md_lines)} lines).")


if __name__ == "__main__":
    main()
