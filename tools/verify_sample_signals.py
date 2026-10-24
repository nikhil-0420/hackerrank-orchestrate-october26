import csv
from collections import defaultdict
from pathlib import Path
import sys

# Ensure code is on path
repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root / "code"))
sys.path.insert(0, str(repo_root))

from ghost_audit.activity import ActivityLog
from ghost_audit.evidence.normalizer import normalize_all_evidence
from ghost_audit.identity import IdentityResolver
from ghost_audit.linker import Linker
from tools.labels import iter_sample_labels

manifest_path = repo_root / "dataset" / "evidence_files.csv"
obs, cov, _ = normalize_all_evidence(manifest_path)
activity = ActivityLog(repo_root / "dataset" / "system_activity.csv")
resolver = IdentityResolver(
    repo_root / "dataset" / "user_identities.csv",
    repo_root / "dataset" / "user_audit_log.csv",
)
linker = Linker(resolver, activity, obs)

with open(repo_root / "dataset" / "sample_deletion_requests.csv", encoding="utf-8") as f:
    requests_dict = {r["case_id"]: r for r in csv.DictReader(f)}

linkages = linker.link_cases(requests_dict)

# Collect truth resources per case
truth_by_case = defaultdict(set)
for cid, rid, sys_id, role in iter_sample_labels():
    truth_by_case[cid].add(rid)

hard_signal_names = {"S1_IDENTIFIER", "S2_USER_ID", "S3_MERGED_TRACE", "S4_LINK_ROW", "S5_CHAIN_KEY", "S6_HANDOVER_DOC"}
exception_signal_names = {"S7_ACCOUNT_ANCHOR", "S8_TUTORIAL_ACCOUNT", "S8_TUTORIAL_ANALYTICS", "S8_ANON_ANALYTICS"}

tp_count = 0
rely_only_s7_s8_by_type = defaultdict(int)
violations = []

print("=== SAMPLE TP SIGNAL BREAKDOWN ===")
for cid in sorted(requests_dict.keys()):
    link = linkages[cid]
    truth_res = truth_by_case[cid]
    for rid, attr in sorted(link.attributed_resources.items()):
        if rid in truth_res:
            tp_count += 1
            sig_names = [s.signal_name for s in attr.signals]
            has_hard = any(s in hard_signal_names for s in sig_names)
            only_s7_s8 = not has_hard and any(s in exception_signal_names for s in sig_names)
            
            rtype = rid.split("_")[0]
            if only_s7_s8:
                rely_only_s7_s8_by_type[rtype] += 1
                if rtype not in ("account", "analytics"):
                    violations.append((cid, rid, rtype, sig_names))

            print(f"{cid} | {rid:<20} | Type: {rtype:<10} | Signals: {', '.join(sig_names)} | Only S7/S8: {only_s7_s8}")

print(f"\nTotal Sample TPs evaluated: {tp_count}")
print("\nCount of attributions that rely ONLY on S7/S8 by resource type:")
for rtype, count in sorted(rely_only_s7_s8_by_type.items()):
    print(f"  {rtype}: {count}")

print(f"\nHard rule violations (relying only on S7/S8 for types other than account or analytics): {len(violations)}")
for v in violations:
    print(f"  VIOLATION: case={v[0]}, resource={v[1]}, type={v[2]}, signals={v[3]}")
