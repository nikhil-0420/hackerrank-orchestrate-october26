"""
Root entry point for Ghost Audit pipeline.
Usage: python code/main.py [--dataset-dir DATASET_DIR] [--requests REQUESTS_PATH] [--output OUTPUT_PATH]
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

# Ensure code directory is on sys.path
CODE_DIR = Path(__file__).resolve().parent
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

from ghost_audit.paths import DATASET_DIR
from ghost_audit.pipeline import run_pipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="Ghost Audit Deletion Compliance Pipeline")
    parser.add_argument(
        "--dataset-dir",
        type=Path,
        default=DATASET_DIR,
        help="Path to dataset directory (default: dataset/)",
    )
    parser.add_argument(
        "--requests",
        type=Path,
        default=None,
        help="Path to deletion requests CSV (default: <dataset-dir>/deletion_requests.csv)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("output.csv"),
        help="Path to write output CSV (default: output.csv)",
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        default=False,
        help="Bypass/disable persistent LLM disk cache",
    )
    parser.add_argument(
        "--mode",
        choices=["A", "B", "C"],
        default="C",
        help="Execution mode: A (deterministic baseline), B (A + L1/L2), C (B + L4, default)",
    )
    parser.add_argument(
        "--provider",
        type=str,
        default="google",
        help="Model provider (default: google)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gemini-2.5-flash",
        help="Model name (default: gemini-2.5-flash)",
    )
    parser.add_argument(
        "--id-sort",
        type=str,
        choices=["natural", "lexical"],
        default="natural",
        help="ID sorting order for output (default: natural)",
    )
    parser.add_argument(
        "--usage-report",
        type=Path,
        default=Path("code/evaluation/usage_report.md"),
        help="Path to write token and cost usage report (default: code/evaluation/usage_report.md)",
    )
    args = parser.parse_args()

    requests_path = args.requests or (args.dataset_dir / "deletion_requests.csv")

    config = {
        "mode": args.mode,
        "provider": args.provider,
        "model": args.model,
        "id_sort": args.id_sort,
        "no_cache": args.no_cache,
        "usage_report_path": args.usage_report,
    }

    print("Starting Ghost Audit Pipeline:")
    print(f"  Dataset:      {args.dataset_dir}")
    print(f"  Requests:     {requests_path}")
    print(f"  Output:       {args.output}")
    print(f"  Mode:         Config {args.mode}")
    print(f"  Provider:     {args.provider}")
    print(f"  Model:        {args.model}")
    print(f"  No-Cache:     {args.no_cache}")
    print(f"  Usage Report: {args.usage_report}")

    stats = run_pipeline(
        dataset_dir=args.dataset_dir,
        requests_path=requests_path,
        out_path=args.output,
        config=config,
    )

    print("\n--- Pipeline Execution Summary ---")
    print(f"Total Cases:            {stats['total_cases']}")
    print(f"Status Distribution:    {stats['status_counts']}")
    print(f"NOT_APPLICABLE Count:   {stats['not_applicable_count']}")
    print(f"Avg Resources / Case:   {stats['resources_per_case_avg']:.2f}")
    print(f"Total Unattributed:     {stats['total_unattributed']}")
    print(f"Zero-Resource Cases:    {len(stats['zero_resource_cases'])}")
    if stats['total_unattributed'] > 0:
        print("\nCases with unattributed candidate resources:")
        for cid, count in stats['unattributed_by_case'].items():
            if count > 0:
                print(f"  {cid}: {count} unattributed")

    print(f"\nSuccessfully generated {args.output}")


if __name__ == "__main__":
    main()
