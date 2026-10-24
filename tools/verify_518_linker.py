import csv
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Set, Tuple

repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root / "code"))
sys.path.insert(0, str(repo_root))

from ghost_audit.activity import ActivityLog
from ghost_audit.identity import IdentityResolver
from ghost_audit.linker import Linker, CaseLinkage
from ghost_audit.linker.assign import (
    assign_account_anchors,
    parse_iso,
    TUTORIAL_WINDOW_MIN,
    STANDARD_WINDOW_MIN,
)

from ghost_audit.linker.signals import collect_hard_signals_for_case


def main():
    print("Loading 518 cases from dataset/deletion_requests.csv...")
    with open(repo_root / "dataset" / "deletion_requests.csv", encoding="utf-8") as f:
        requests = {r["case_id"]: r for r in csv.DictReader(f)}
    
    total_cases = len(requests)
    print(f"Total requests: {total_cases}")
    
    linker = Linker()
    print(f"Loaded {len(linker.observations)} observations across {len(linker.obs_by_res)} resources.")
    
    # Let's inspect step-by-step:
    # 1. Hard signals S1-S6
    case_hard_signals = {}
    case_hard_resources = {}
    for cid, req in requests.items():
        ident = linker.resolver.resolve(req["email"])
        h_signals = collect_hard_signals_for_case(
            case_id=cid,
            requested_at=req["requested_at"],
            audit_at=req["audit_at"],
            identity=ident,
            all_observations=linker.observations,
            activity=linker.activity,
            obs_by_res=linker.obs_by_res,
        )
        case_hard_signals[cid] = h_signals
        case_hard_resources[cid] = {s.resource_id for s in h_signals}

    # Find accounts attributed by hard signals (S1-S6)
    hard_account_by_case: Dict[str, str] = {}
    for cid, sigs in case_hard_signals.items():
        accs = {s.resource_id for s in sigs if s.resource_id.startswith("account_")}
        if accs:
            # take the primary account
            hard_account_by_case[cid] = sorted(accs)[0]

    # 2. Anchor assignment inspection
    # Let's see how many candidates were available per case after S1-S6
    dw_account_rows = [
        r for r in linker.activity.rows
        if r.source_system == "deletion_worker"
        and r.target_system == "account_service"
        and r.event_type == "DELETE_RECORD"
    ]
    
    # Track candidate counts per case
    cases_with_2plus_candidates = 0
    cases_with_1_candidate = 0
    cases_with_0_candidates = 0
    
    for cid, req in requests.items():
        rep_dt = parse_iso(req["reported_at"])
        is_tut = not req["reported_at"].endswith(":00:00Z")
        w_min, w_max = TUTORIAL_WINDOW_MIN if is_tut else STANDARD_WINDOW_MIN
        
        # count candidate activity rows in time window
        candidates = []
        for r in dw_account_rows:
            ev_dt = parse_iso(r.event_time)
            delta_m = (ev_dt - rep_dt).total_seconds() / 60.0
            if w_min <= delta_m <= w_max:
                candidates.append(r)
        
        if len(candidates) >= 2:
            cases_with_2plus_candidates += 1
        elif len(candidates) == 1:
            cases_with_1_candidate += 1
        else:
            cases_with_0_candidates += 1

    # Run Linker.link_cases
    linkages = linker.link_cases(requests)
    
    # 1. Cases with an attributed account
    cases_with_account = 0
    cases_with_unique_anchor = 0
    account_attr_types = Counter()
    
    anchor_assigned_counts = Counter()
    for cid, lk in linkages.items():
        accs = [ar for ar in lk.attributed_resources.values() if ar.resource_id.startswith("account_")]
        if accs:
            cases_with_account += 1
            for ar in accs:
                for s in ar.signals:
                    account_attr_types[s.signal_name] += 1
        
        # Check anchors
        anchors = [ar for ar in lk.attributed_resources.values() if any(s.signal_name in ("S7_ACCOUNT_ANCHOR", "S8_TUTORIAL_ACCOUNT") for s in ar.signals)]
        if len(anchors) == 1:
            cases_with_unique_anchor += 1
        for a in anchors:
            anchor_assigned_counts[a.resource_id] += 1


    pct_with_account = (cases_with_account / total_cases) * 100.0
    
    # Unattributed resources per case
    unattr_counts = [len(lk.unattributed_resources) for lk in linkages.values()]
    unattr_counter = Counter(unattr_counts)
    
    # Gap distribution for anchors attributed by HARD SIGNALS ONLY
    # gap = event_time - reported_at
    gaps_tutorial = []
    gaps_standard = []
    all_hard_gaps = []
    
    for cid, acc_id in hard_account_by_case.items():
        req = requests[cid]
        rep_dt = parse_iso(req["reported_at"])
        # Find the activity row for this account
        rows = [r for r in dw_account_rows if r.resource_id == acc_id]
        if rows:
            ev_dt = parse_iso(rows[0].event_time)
            gap_m = (ev_dt - rep_dt).total_seconds() / 60.0
            all_hard_gaps.append(gap_m)
            if not req["reported_at"].endswith(":00:00Z"):
                gaps_tutorial.append(gap_m)
            else:
                gaps_standard.append(gap_m)

    print("\n" + "=" * 60)
    print("PHASE 2C VERIFICATION: 518 HIDDEN CASES REPORT")
    print("=" * 60)
    print(f"Total Cases: {total_cases}")
    print(f"Cases with an Attributed Account: {cases_with_account} / {total_cases} ({pct_with_account:.2f}%) [GATE >= 95%]")
    print(f"Cases with Anchors Uniquely Assigned: {cases_with_unique_anchor} / {total_cases} ({(cases_with_unique_anchor/total_cases)*100.0:.2f}%)")
    print(f"Cases with 2+ Candidate Anchors in window after S1-S6: {cases_with_2plus_candidates}")
    print(f"Cases with 1 Candidate Anchor in window: {cases_with_1_candidate}")
    print(f"Cases with 0 Candidate Anchors in window: {cases_with_0_candidates}")
    
    print("\nUnattributed Resource Counts per Case:")
    print(f"  Min: {min(unattr_counts)}, Max: {max(unattr_counts)}, Avg: {sum(unattr_counts)/len(unattr_counts):.2f}")
    print(f"  Distribution: {sorted(unattr_counter.items())}")
    
    print(f"\nGap Distribution (event_time minus reported_at) for Anchors Attributed by HARD SIGNALS ONLY (N={len(all_hard_gaps)}):")
    if all_hard_gaps:
        all_sorted = sorted(all_hard_gaps)
        p10 = all_sorted[int(len(all_sorted) * 0.10)]
        p25 = all_sorted[int(len(all_sorted) * 0.25)]
        p50 = all_sorted[int(len(all_sorted) * 0.50)]
        p75 = all_sorted[int(len(all_sorted) * 0.75)]
        p90 = all_sorted[int(len(all_sorted) * 0.90)]
        print(f"  Overall: min={min(all_hard_gaps):.2f}m, max={max(all_hard_gaps):.2f}m, mean={sum(all_hard_gaps)/len(all_hard_gaps):.2f}m")
        print(f"  Percentiles: p10={p10:.2f}m, p25={p25:.2f}m, p50={p50:.2f}m, p75={p75:.2f}m, p90={p90:.2f}m")
    
    print(f"\n  Tutorial Regime (N={len(gaps_tutorial)}):")
    if gaps_tutorial:
        print(f"    min={min(gaps_tutorial):.2f}m, max={max(gaps_tutorial):.2f}m, mean={sum(gaps_tutorial)/len(gaps_tutorial):.2f}m")
    else:
        print("    None")
        
    print(f"\n  Standard Regime (N={len(gaps_standard)}):")
    if gaps_standard:
        print(f"    min={min(gaps_standard):.2f}m, max={max(gaps_standard):.2f}m, mean={sum(gaps_standard)/len(gaps_standard):.2f}m")
    else:
        print("    None")

    two_regimes = bool(gaps_tutorial and gaps_standard and max(gaps_tutorial) < min(gaps_standard) or (gaps_tutorial and gaps_standard and all(g < -30 for g in gaps_standard) and all(abs(g) < 15 for g in gaps_tutorial)))
    print(f"\nDoes hard-signal anchor gap distribution still show two distinct regimes? {'YES' if two_regimes else 'NO'}")


if __name__ == "__main__":
    main()
