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
import re
import subprocess
import sys
import time
from typing import Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent


def parse_test_counts(output: str) -> Optional[Tuple[int, int, int]]:
    """
    Parse (passed, skipped, failed) counts from unittest output.
    Returns None if output does not contain unittest results.
    """
    m_ran = re.search(r"Ran (\d+) tests? in", output)
    if not m_ran:
        return None
    total = int(m_ran.group(1))

    m_skip = re.search(r"skipped=(\d+)", output)
    skipped = int(m_skip.group(1)) if m_skip else 0

    m_fail = re.search(r"failures=(\d+)", output)
    failures = int(m_fail.group(1)) if m_fail else 0

    m_err = re.search(r"errors=(\d+)", output)
    errors = int(m_err.group(1)) if m_err else 0

    failed = failures + errors
    passed = max(0, total - skipped - failed)
    return passed, skipped, failed


def run_step(name: str, cmd: list[str], env: dict[str, str]) -> tuple[bool, float, str, Optional[Tuple[int, int, int]]]:
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
        counts = parse_test_counts(output)
        return success, duration, output, counts
    except Exception as e:
        duration = time.time() - start
        return False, duration, f"Exception during execution: {e}", None


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
            "Unit Tests: Linker & Signals (S1-S8)",
            [sys.executable, "-m", "unittest", "tests/test_linker.py"],
        ),
        (
            "Unit Tests: Citation Engine",
            [sys.executable, "-m", "unittest", "tests/test_citation.py"],
        ),
        (
            "Unit Tests: LLM Bounded Subsystem",
            [sys.executable, "-m", "unittest", "tests/test_llm.py"],
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
                "scratch/eval_self_check.md",
            ],
        ),
        (
            "Custom Policy Cases: custom_cases.py",
            [sys.executable, "code/evaluation/custom_cases.py"],
        ),
        (
            "Log Integrity: check_log.py",
            [sys.executable, "tools/check_log.py"],
        ),
    ]

    print("==========================================================================================")
    print("RUNNING GHOST AUDIT INTEGRATION CHECKS")
    print("==========================================================================================\n")

    results = []
    overall_success = True

    for name, cmd in steps:
        print(f"[*] Running: {name} ...")
        success, duration, output, counts = run_step(name, cmd, env)
        status_str = "PASS" if success else "FAIL"
        results.append((name, status_str, duration, counts, output))
        if not success:
            overall_success = False
            count_info = f" [passed={counts[0]}, skipped={counts[1]}, failed={counts[2]}]" if counts else ""
            print(f"    -> FAILED in {duration:.2f}s{count_info}:\n{output}\n")
        else:
            count_info = f" [passed={counts[0]}, skipped={counts[1]}]" if counts else ""
            print(f"    -> PASSED ({duration:.2f}s){count_info}")

    print("\n==========================================================================================")
    print("INTEGRATION CHECK SUMMARY TABLE")
    print("==========================================================================================")
    print(f"{'Step Name':<42} | {'Status':<8} | {'Passed':<6} | {'Skipped':<7} | {'Duration':<10}")
    print("-" * 82)
    total_passed = 0
    total_skipped = 0
    total_failed = 0
    for name, status, duration, counts, _ in results:
        if counts:
            p, s, f = counts
            total_passed += p
            total_skipped += s
            total_failed += f
            p_str, s_str = str(p), str(s)
        else:
            p_str, s_str = "-", "-"
        print(f"{name:<42} | {status:<8} | {p_str:>6} | {s_str:>7} | {duration:>7.2f}s")
    print("=" * 82)
    print(f"Total Test Counts: {total_passed} passed, {total_skipped} skipped, {total_failed} failed.")

    if overall_success:
        print("\nALL INTEGRATION CHECKS PASSED (exit 0).\n")
        sys.exit(0)
    else:
        print("\nONE OR MORE CHECKS FAILED (exit 1).\n", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

