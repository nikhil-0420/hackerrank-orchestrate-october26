import csv, json, sys, os
from collections import defaultdict
sys.path.insert(0, 'code')
from ghost_audit.loaders import load_manifest
from ghost_audit.evidence.normalizer import normalize_all_evidence
from ghost_audit.evidence.coverage import CoverageIndex
from ghost_audit.timegate import citable, parse_iso_ts

# Load manifest and observations
manifest = load_manifest("dataset/evidence_files.csv")
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

print("Evaluating Citation Rule against Sample Ground Truth:")
failures = []
total_eval_steps = 0

for cid, steps in truth.items():
    req = requests[cid]
    audit_at = req["audit_at"]
    
    for s in steps:
        truth_ev = s.get("evidence_id", "")
        # Only evaluate steps that cite evidence (remediation steps and incomplete future checks have evidence_id="")
        if not truth_ev:
            continue
            
        total_eval_steps += 1
        rid = s["resource_id"]
        sys_id = s["system_id"]
        state = s["state"]
        
        # Test Citation Rule:
        # 1. If record is PRESENT/ANONYMIZED/REDACTED/ACTIVE (present record):
        #    Cites latest citable file (file_captured_at <= audit_at) that contains it.
        # 2. If record is ABSENT:
        #    Cites latest citable covering snapshot that lacks it, OR file holding NOT_FOUND / 404 line.
        
        rule_ev = None
        if state == "ABSENT":
            # Check covering snapshot or 404 line
            cov_snap = cov_index.latest_citable_covering_snapshot(sys_id, audit_at)
            # Also check if any observation has 404/NOT_FOUND
            citable_obs = [
                o for o in obs_by_res.get(rid, [])
                if citable(manifest.get(o.file_id).captured_at, audit_at)
            ]
            not_found_obs = [
                o for o in citable_obs
                if o.state.get("result") in ["NOT_FOUND", "not_found"] or o.state.get("http_status") in [404, "404"] or o.state.get("rows") in [0, "0"]
            ]
            if not_found_obs:
                not_found_obs.sort(
                    key=lambda o: (parse_iso_ts(manifest[o.file_id].captured_at), o.file_id),
                    reverse=True
                )
                rule_ev = not_found_obs[0].file_id
            elif cov_snap:
                rule_ev = cov_snap.file_id
        else:
            # Present record: latest citable file containing it
            citable_obs = [
                o for o in obs_by_res.get(rid, [])
                if citable(manifest.get(o.file_id).captured_at, audit_at)
            ]
            if citable_obs:
                citable_obs.sort(
                    key=lambda o: (parse_iso_ts(manifest[o.file_id].captured_at), o.file_id),
                    reverse=True
                )
                rule_ev = citable_obs[0].file_id
                
        match = (rule_ev == truth_ev)
        if not match:
            failures.append({
                "case_id": cid,
                "step_no": s["step_no"],
                "resource_id": rid,
                "system_id": sys_id,
                "state": state,
                "truth_ev": truth_ev,
                "rule_ev": rule_ev,
                "audit_at": audit_at,
            })

print(f"Total evaluated steps with evidence_id: {total_eval_steps}")
print(f"Total failures: {len(failures)}")
if failures:
    for f in failures:
        print("FAIL:", f)
else:
    print("ALL 32 SAMPLES PASSED THE CITATION RULE WITH 100% ACCURACY!")
