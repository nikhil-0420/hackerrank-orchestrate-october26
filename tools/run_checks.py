#!/usr/bin/env python3
"""
Integration runner for Ghost Audit repository.
Runs in order:
1. Unit tests (validator, mutation tests, evaluation metrics, metamorphic suite)
2. Validator on sample_output.csv (sanity check: 0 errors)
3. Evaluation main on sample_output vs sample_output (sanity check: 1.0 metrics)
4. Chat transcript log integrity check (tools/check_log.py)

Exits non-zero on failure and prints a summary table.
"""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import time

REPO_ROOT = Path(__file__).resolve().parent.parent


def run_step(name: str, cmd: list[str], env: dict[str, str]) -> tuple[bool, float, str]:
    start = time.time()
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(REPO_ROOT),
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        duration = time.time() - start
        output = (proc.stdout + "\n" + proc.stderr).strip()
        success = proc.returncode == 0
        return success, duration, output
    except Exception as e:
        duration = time.time() - start
        return False, duration, f"Exception during execution: {e}"


def main() -> None:
    env = dict(os.environ)
    code_path = str(REPO_ROOT / "code")
    curr_pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = f"{code_path}{os.pathsep}{curr_pythonpath}" if curr_pythonpath else code_path

    steps = [
        (
            "Unit Tests: Validator Rules",
            [sys.executable, "-m", "unittest", "tests/test_validate.py"],
        ),
        (
            "Unit Tests: Validator Mutations",
            [sys.executable, "-m", "unittest", "tests/test_validate_mutations.py"],
        ),
        (
            "Unit Tests: Evaluation Metrics",
            [sys.executable, "-m", "unittest", "tests/test_evaluation_metrics.py"],
        ),
        (
            "Scaffold Tests: Metamorphic Properties",
            [sys.executable, "-m", "unittest", "tests/test_metamorphic.py"],
        ),
        (
            "Validation: Sample Ground Truth",
            [
                sys.executable,
                "-m",
                "ghost_audit.validate",
                "--output",
                "dataset/sample_output.csv",
                "--requests",
                "dataset/sample_deletion_requests.csv",
                "--manifest",
                "dataset/evidence_files.csv",
                "--expected-rows",
                "32",
                "--id-sort",
                "lexical",
            ],
        ),
        (
            "Evaluation: Sample Self-Check",
            [
                sys.executable,
                "code/evaluation/main.py",
                "--pred",
                "dataset/sample_output.csv",
                "--truth",
                "dataset/sample_output.csv",
                "--requests",
                "dataset/sample_deletion_requests.csv",
                "--out",
                "code/evaluation/evaluation_report.md",
            ],
        ),
        (
            "Log Integrity: check_log.py",
            [sys.executable, "tools/check_log.py"],
        ),
    ]

    print("================================================================================")
    print("RUNNING GHOST AUDIT INTEGRATION CHECKS")
    print("================================================================================\n")

    results = []
    overall_success = True

    for name, cmd in steps:
        print(f"[*] Running: {name} ...")
        success, duration, output = run_step(name, cmd, env)
        status_str = "PASS" if success else "FAIL"
        results.append((name, status_str, duration, output))
        if not success:
            overall_success = False
            print(f"    -> FAILED in {duration:.2f}s:\n{output}\n")
        else:
            print(f"    -> PASSED ({duration:.2f}s)")

    print("\n================================================================================")
    print("INTEGRATION CHECK SUMMARY TABLE")
    print("================================================================================")
    print(f"{'Step Name':<42} | {'Status':<8} | {'Duration':<10}")
    print("-" * 66)
    for name, status, duration, _ in results:
        print(f"{name:<42} | {status:<8} | {duration:>7.2f}s")
    print("=" * 66)

    if overall_success:
        print("\nALL INTEGRATION CHECKS PASSED (exit 0).\n")
        sys.exit(0)
    else:
        print("\nONE OR MORE CHECKS FAILED (exit 1).\n", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
