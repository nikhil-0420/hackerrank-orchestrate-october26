"""
CLI deliverable for Phase 1 Evidence Ingestion:
python3 -m ghost_audit.evidence.dump

Outputs:
1. Per-file observation counts and unparsed-line counts for all evidence files
2. Summary verification: total files, total observations, total unparsed lines (must be 0)
3. 10 sampled observations traced back to their raw source text
"""

import json
import random
import sys
from pathlib import Path

# Add 'code' directory to sys.path so ghost_audit can be executed as a module
code_dir = Path(__file__).resolve().parent.parent.parent
if str(code_dir) not in sys.path:
    sys.path.insert(0, str(code_dir))

from ghost_audit.evidence.normalizer import normalize_all_evidence
from ghost_audit.loaders.manifest import load_manifest
from ghost_audit.paths import DATASET_DIR, MANIFEST_PATH


def get_raw_source_snippet(obs, manifest_by_id) -> str:
    """Retrieve the original source snippet for an observation based on raw_ref."""
    meta = manifest_by_id.get(obs.file_id)
    if not meta or not meta.abs_path.exists():
        return f"[File not found: {obs.file_id}]"

    kind = obs.source_kind
    if kind == "log":
        # e.g. "trace:tr-XXXX lines:12-14 id:resource_123" or "line:12 id:resource_123"
        lines = meta.abs_path.read_text(encoding="utf-8", errors="replace").splitlines()
        if "lines:" in obs.raw_ref:
            try:
                line_part = obs.raw_ref.split("lines:")[1].split()[0]
                start_l, end_l = map(int, line_part.split("-"))
                snippet = "\n".join(lines[start_l - 1 : end_l])
                return snippet[:300]
            except Exception:
                pass
        elif "line:" in obs.raw_ref:
            try:
                lno = int(obs.raw_ref.split("line:")[1].split()[0])
                return lines[lno - 1][:300]
            except Exception:
                pass
        return f"[Raw ref: {obs.raw_ref}]"

    elif kind == "txt":
        lines = meta.abs_path.read_text(encoding="utf-8", errors="replace").splitlines()
        try:
            lno = int(obs.raw_ref.split("line:")[1].split()[0])
            return lines[lno - 1][:300]
        except Exception:
            return f"[Raw ref: {obs.raw_ref}]"

    elif kind == "json":
        return json.dumps(obs.state, indent=2)[:300]

    elif kind == "sql":
        return f"SQL Record from {obs.raw_ref}: {obs.state}"

    return str(obs.state)[:300]


def main():
    manifest = load_manifest()
    manifest_by_id = {m.file_id: m for m in manifest}

    print("=" * 80)
    print("PHASE 1 EVIDENCE INGESTION REPORT")
    print("=" * 80)

    observations, coverage, file_stats = normalize_all_evidence()

    total_unparsed = 0
    total_obs = len(observations)

    print("\n--- Per-File Ingestion Stats ---")
    print(f"{'File ID':<13} {'Kind':<6} {'Obs':<6} {'Unparsed':<9} {'File Path'}")
    print("-" * 80)

    for file_id in sorted(file_stats.keys(), key=lambda x: int(x.split('_')[1]) if '_' in x and x.split('_')[1].isdigit() else x):
        stat = file_stats[file_id]
        obs_c = stat["obs_count"]
        unp_c = stat["unparsed_lines"]
        total_unparsed += unp_c
        kind = stat["source_kind"]
        path = stat["file_path"]
        print(f"{file_id:<13} {kind:<6} {obs_c:<6} {unp_c:<9} {path}")

    print("-" * 80)
    print(f"Total Evidence Files : {len(file_stats)}")
    print(f"Total Observations   : {total_obs}")
    print(f"Total Coverage Scopes: {len(coverage)}")
    print(f"Total Unparsed Lines : {total_unparsed}")
    print("=" * 80)

    if total_unparsed != 0:
        print(f"\nFAILED ACCEPTANCE: Found {total_unparsed} unparsed lines (expected 0).", file=sys.stderr)
        sys.exit(1)

    # Sample 10 random observations deterministically
    random.seed(42)
    sample_size = min(10, len(observations))
    sampled_obs = random.sample(observations, sample_size)

    print(f"\n--- 10 Sampled Observations Traced to Source Text (Seed=42) ---\n")
    for idx, obs in enumerate(sampled_obs, 1):
        print(f"[{idx}/10] Observation: {obs.resource_id} (File: {obs.file_id})")
        print(f"  System / Collection : {obs.system_id} / {obs.collection}")
        print(f"  Obs Time / File Time: {obs.obs_time} / {obs.file_captured_at}")
        print(f"  Source Kind / Ref   : {obs.source_kind} ({obs.raw_ref})")
        print(f"  Identifiers         : email={obs.identifiers.email!r}, phone={obs.identifiers.phone!r}, "
              f"user_ref={obs.identifiers.user_ref!r}, name={obs.identifiers.name!r}, masked={obs.identifiers.masked}")
        print(f"  State Sample        : {str(obs.state)[:160]}...")
        snippet = get_raw_source_snippet(obs, manifest_by_id)
        print(f"  Raw Source Snippet  :\n    {snippet.replace(chr(10), chr(10) + '    ')}")
        print("-" * 80)

    print("\nACCEPTANCE CHECK: All files parsed successfully with unparsed lines == 0.")


if __name__ == "__main__":
    main()
