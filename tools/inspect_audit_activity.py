import csv, json, os
from pathlib import Path
import sys

repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root / "code"))
sys.path.insert(0, str(repo_root))

from ghost_audit.linker.assign import parse_iso
from tools.labels import iter_sample_labels

activity_rows = list(csv.DictReader(open(repo_root / "dataset" / "system_activity.csv", encoding="utf-8")))
sample_output = list(csv.DictReader(open(repo_root / "dataset" / "sample_output.csv", encoding="utf-8")))
sample_reqs = {r["case_id"]: r for r in csv.DictReader(open(repo_root / "dataset" / "sample_deletion_requests.csv", encoding="utf-8"))}

case_anchors = {}
for cid, rid, sys_id, role in iter_sample_labels():
    if rid.startswith("account_"):
        case_anchors[cid] = rid

audit_gt = {}
for r in sample_output:
    cid = r["case_id"]
    steps = json.loads(r["steps_json"])
    for s in steps:
        if s.get("system_id") == "security_service":
            audit_gt[cid] = (s.get("resource_id"), s.get("evidence_id"))

# Check where each audit record appears in evidence
evidence_dir = repo_root / "dataset" / "evidence"
ev_found = {}
for root, dirs, files in os.walk(evidence_dir):
    for f in files:
        fp = Path(root) / f
        try:
            txt = fp.read_text(encoding="utf-8", errors="ignore")
            for cid, (arid, evid) in audit_gt.items():
                if arid in txt:
                    ev_found.setdefault(arid, []).append(f)
        except Exception:
            pass

from ghost_audit.loaders.manifest import load_manifest
from ghost_audit.evidence import normalize_all_evidence

print("\n=== Checking Observation Identifiers for 24 Audit Records ===")
manifest = load_manifest(repo_root / "dataset" / "evidence_files.csv")
obs_list, _, _ = normalize_all_evidence(repo_root / "dataset" / "evidence_files.csv")




obs_by_res = {}
target_rids = {arid: cid for cid, (arid, evid) in audit_gt.items()}
for o in obs_list:
    if o.resource_id in target_rids:
        obs_by_res.setdefault(o.resource_id, []).append(o)

print(f"Total audit records found in observations: {len(obs_by_res)} / {len(audit_gt)}")
for cid in sorted(audit_gt.keys()):
    arid, evid = audit_gt[cid]
    if arid in obs_by_res:
        o = obs_by_res[arid][0]
        print(f"{cid} -> {arid}: file={o.file_id} sys={o.system_id} col={o.collection} idents={o.identifiers} state={o.state}")
    else:
        print(f"{cid} -> {arid}: NO OBSERVATION in evidence files")







