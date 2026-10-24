import csv, json, sys, os
from collections import defaultdict
sys.path.insert(0, 'code')
from ghost_audit.loaders import get_manifest_by_id
from ghost_audit.evidence.normalizer import normalize_all_evidence
from ghost_audit.evidence.coverage import CoverageIndex
from ghost_audit.timegate import citable, parse_iso_ts

# Load manifest and observations
manifest = get_manifest_by_id("dataset/evidence_files.csv")
obs_list, cov_records, _ = normalize_all_evidence("dataset/evidence_files.csv")
obs_by_res = defaultdict(list)
for o in obs_list:
    obs_by_res[o.resource_id].append(o)
cov_index = CoverageIndex(cov_records)

# Load sample requests
with open("dataset/sample_deletion_requests.csv", "r", encoding="utf-8") as f:
    requests = {r["case_id"]: r for r in csv.DictReader(f)}

# Load sample output ground truth
with open("dataset/sample_output.csv", "r", encoding="utf-8") as f:
    truth = {r["case_id"]: json.loads(r["steps_json"]) for r in csv.DictReader(f)}

def resolve_citation(resource_id, system_id, state, audit_at, fallback_file_id=None):
    # Rule:
    # 1. If absent:
    #    Latest citable covering snapshot that lacks it, OR file holding NOT_FOUND / 404 line
    if state == "ABSENT":
        # Check if there is an explicit 404 / NOT_FOUND observation
        citable_obs = [
            o for o in obs_by_res.get(resource_id, [])
            if citable(manifest[o.file_id].captured_at, audit_at)
        ]
        not_found_obs = [
            o for o in citable_obs
            if o.state.get("result") in ["NOT_FOUND", "not_found"] or o.state.get("http_status") in [404, "404"] or o.state.get("status_code") in [404, "404"] or o.state.get("rows") in [0, "0"]
        ]
        if not_found_obs:
            not_found_obs.sort(
                key=lambda o: (parse_iso_ts(manifest[o.file_id].captured_at), o.file_id),
                reverse=True
            )
            return not_found_obs[0].file_id
        
        # Otherwise covering snapshot
        citable_cov = [
            r for r in cov_index.records
            if r.system_id.lower() == system_id.lower() and citable(r.file_captured_at, audit_at)
        ]
        if citable_cov:
            citable_cov.sort(
                key=lambda r: (parse_iso_ts(r.file_captured_at), r.file_id),
                reverse=True
            )
            return citable_cov[0].file_id
            
        return fallback_file_id or ""
    else:
        # Present record (PRESENT, ANONYMIZED, REDACTED, ACTIVE):
        # Latest citable file containing it
        citable_obs = [
            o for o in obs_by_res.get(resource_id, [])
            if citable(manifest[o.file_id].captured_at, audit_at)
        ]
        if citable_obs:
            citable_obs.sort(
                key=lambda o: (parse_iso_ts(manifest[o.file_id].captured_at), o.file_id),
                reverse=True
            )
            return citable_obs[0].file_id
        return fallback_file_id or ""

print("Testing resolve_citation across all 32 samples:")
failures = []
total_tested = 0
case_citations = defaultdict(dict)

for cid, steps in sorted(truth.items()):
    req = requests[cid]
    audit_at = req["audit_at"]
    for s in steps:
        truth_ev = s.get("evidence_id", "")
        if not truth_ev:
            continue
        total_tested += 1
        rid = s["resource_id"]
        sys_id = s["system_id"]
        st = s["state"]
        pred_ev = resolve_citation(rid, sys_id, st, audit_at)
        case_citations[cid][rid] = (truth_ev, pred_ev)
        if pred_ev != truth_ev:
            failures.append((cid, s["step_no"], rid, sys_id, st, truth_ev, pred_ev))

print(f"Total steps evaluated: {total_tested}")
print(f"Total failures: {len(failures)}")
if failures:
    for fail in failures:
        print("FAIL:", fail)
else:
    print("SUCCESS: 100% accuracy on all 32 samples!")

print("\nPer-sample citation breakdown:")
for cid in sorted(case_citations.keys()):
    r_map = case_citations[cid]
    files = {v[0] for v in r_map.values()}
    print(f"{cid}: {len(r_map)} cited steps, files: {sorted(list(files))}")
