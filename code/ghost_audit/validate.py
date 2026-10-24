"""
Output validation harness for Ghost Audit.
Validates structure, integrity, and domain rules against problem_statement.md.
Does NOT import anything from evaluation and does NOT read sample_output.csv.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path
import re
import sys
from typing import Any, Callable

from ghost_audit.spec import (
    ALLOWED_PHASES,
    ALLOWED_STATUSES,
    FINDING_TO_REMEDIATION,
    LEGAL_OPERATION_STATE_PAIRS,
    OPERATION_ORDER_WITHIN_PHASE,
    OPERATION_TO_PHASE,
    OUTPUT_HEADER,
    PHASE_FINDING,
    PHASE_ORDER,
    PHASE_REMEDIATION,
    PHASE_VERIFICATION,
    REMEDIATION_TO_VERIFICATION,
    STATUS_COMPLETE,
    STATUS_INCOMPLETE,
    STATUS_NOT_APPLICABLE,
    STEP_FIELDS,
)


@dataclass(frozen=True)
class Violation:
    rule_id: str
    severity: str  # "ERROR" | "WARN"
    case_id: str
    step_no: int | None
    message: str

    def __getitem__(self, item: str) -> Any:
        return getattr(self, item)

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "severity": self.severity,
            "case_id": self.case_id,
            "step_no": self.step_no,
            "message": self.message,
        }


def natural_sort_key(s: str) -> list[int | str]:
    """Helper to produce a natural sorting key for alphanumeric strings."""
    return [int(c) if c.isdigit() else c.lower() for c in re.split(r"(\d+)", str(s))]


def parse_iso_timestamp(ts: str) -> datetime | None:
    """Parse an ISO-8601 timestamp string safely."""
    if not ts:
        return None
    try:
        clean = ts.replace("Z", "+00:00")
        return datetime.fromisoformat(clean)
    except Exception:
        return None


def check_header(header: list[str]) -> list[Violation]:
    """V01: Check exact header matching."""
    if header != OUTPUT_HEADER:
        return [
            Violation(
                rule_id="V01",
                severity="ERROR",
                case_id="<HEADER>",
                step_no=None,
                message=f"Header mismatch: expected {OUTPUT_HEADER}, got {header}",
            )
        ]
    return []


def check_requests_alignment(
    output_case_ids: list[str],
    request_case_ids: list[str],
    expected_rows: int | None = None,
) -> list[Violation]:
    """V02: One row per request, no missing/extra case_id, matching row count."""
    violations: list[Violation] = []
    
    if expected_rows is not None and len(output_case_ids) != expected_rows:
        violations.append(
            Violation(
                rule_id="V02",
                severity="ERROR",
                case_id="<DATASET>",
                step_no=None,
                message=f"Expected {expected_rows} rows, found {len(output_case_ids)}",
            )
        )

    # Check duplicates in output
    seen = set()
    duplicates = set()
    for cid in output_case_ids:
        if cid in seen:
            duplicates.add(cid)
        seen.add(cid)
    for dup in sorted(duplicates):
        violations.append(
            Violation(
                rule_id="V02",
                severity="ERROR",
                case_id=dup,
                step_no=None,
                message=f"Duplicate case_id in output: '{dup}'",
            )
        )

    out_set = set(output_case_ids)
    req_set = set(request_case_ids)

    missing = req_set - out_set
    for m in sorted(missing):
        violations.append(
            Violation(
                rule_id="V02",
                severity="ERROR",
                case_id=m,
                step_no=None,
                message=f"Missing case_id from requests: '{m}'",
            )
        )

    extra = out_set - req_set
    for e in sorted(extra):
        violations.append(
            Violation(
                rule_id="V02",
                severity="ERROR",
                case_id=e,
                step_no=None,
                message=f"Extra case_id not in requests: '{e}'",
            )
        )

    return violations


def check_case_sorting(
    output_case_ids: list[str],
    id_sort: str = "lexical",
) -> list[Violation]:
    """V03: Sorted unique case_id."""
    sort_fn: Callable[[str], Any] = natural_sort_key if id_sort == "natural" else (lambda x: x)
    expected_order = sorted(output_case_ids, key=sort_fn)
    
    if output_case_ids != expected_order:
        # Locate the first out-of-order element
        for actual, expected in zip(output_case_ids, expected_order):
            if actual != expected:
                return [
                    Violation(
                        rule_id="V03",
                        severity="ERROR",
                        case_id=actual,
                        step_no=None,
                        message=f"Output case_ids not sorted under {id_sort} ordering (found '{actual}', expected '{expected}')",
                    )
                ]
        return [
            Violation(
                rule_id="V03",
                severity="ERROR",
                case_id=output_case_ids[0] if output_case_ids else "<EMPTY>",
                step_no=None,
                message=f"Output case_ids not sorted under {id_sort} ordering",
            )
        ]
    return []


def check_status_validity(case_id: str, status: str) -> list[Violation]:
    """V11: deletion_status in allowed set."""
    if status not in ALLOWED_STATUSES:
        return [
            Violation(
                rule_id="V11",
                severity="ERROR",
                case_id=case_id,
                step_no=None,
                message=f"Invalid deletion_status '{status}'; allowed: {sorted(ALLOWED_STATUSES)}",
            )
        ]
    return []


def check_not_applicable_rule(case_id: str, status: str, steps: list[dict[str, Any]]) -> list[Violation]:
    """V12: NOT_APPLICABLE <=> steps == []."""
    if status == STATUS_NOT_APPLICABLE and len(steps) > 0:
        return [
            Violation(
                rule_id="V12",
                severity="ERROR",
                case_id=case_id,
                step_no=None,
                message=f"Status is NOT_APPLICABLE but steps_json contains {len(steps)} steps",
            )
        ]
    if status != STATUS_NOT_APPLICABLE and len(steps) == 0:
        return [
            Violation(
                rule_id="V12",
                severity="ERROR",
                case_id=case_id,
                step_no=None,
                message=f"Status is {status} but steps_json is empty []",
            )
        ]
    return []


def check_complete_rule(case_id: str, status: str, steps: list[dict[str, Any]]) -> list[Violation]:
    """V13: COMPLETE => VERIFICATION steps only and every evidence_id non-empty."""
    violations: list[Violation] = []
    if status == STATUS_COMPLETE:
        for s in steps:
            step_no = s.get("step_no")
            phase = s.get("phase")
            evidence_id = s.get("evidence_id")
            if phase != PHASE_VERIFICATION:
                violations.append(
                    Violation(
                        rule_id="V13",
                        severity="ERROR",
                        case_id=case_id,
                        step_no=step_no,
                        message=f"COMPLETE case contains step with phase '{phase}', expected '{PHASE_VERIFICATION}'",
                    )
                )
            if not evidence_id:
                violations.append(
                    Violation(
                        rule_id="V13",
                        severity="ERROR",
                        case_id=case_id,
                        step_no=step_no,
                        message="COMPLETE case step has empty evidence_id",
                    )
                )
    return violations


def check_incomplete_finding_rule(case_id: str, status: str, steps: list[dict[str, Any]]) -> list[Violation]:
    """V14: INCOMPLETE => >=1 FINDING step."""
    if status == STATUS_INCOMPLETE:
        finding_count = sum(1 for s in steps if s.get("phase") == PHASE_FINDING)
        if finding_count == 0:
            return [
                Violation(
                    rule_id="V14",
                    severity="ERROR",
                    case_id=case_id,
                    step_no=None,
                    message="INCOMPLETE case must contain at least 1 FINDING step",
                )
            ]
    return []


def check_steps_structure_and_order(
    case_id: str,
    steps: list[dict[str, Any]],
    manifest: dict[str, str],
    case_audit_at: str | None,
    id_sort: str = "lexical",
) -> list[Violation]:
    """V05, V06, V07, V08, V09, V10: Per-step field and integrity validation."""
    violations: list[Violation] = []
    expected_step_fields = set(STEP_FIELDS)
    parsed_audit_at = parse_iso_timestamp(case_audit_at) if case_audit_at else None

    prev_phase_order = 0
    prev_phase_name = ""

    for idx, step in enumerate(steps, start=1):
        # V05: step_no == 1..n
        step_no = step.get("step_no")
        if step_no != idx:
            violations.append(
                Violation(
                    rule_id="V05",
                    severity="ERROR",
                    case_id=case_id,
                    step_no=step_no,
                    message=f"Step index mismatch: expected step_no {idx}, got {step_no}",
                )
            )

        # V06: exact field set per step
        actual_fields = set(step.keys())
        if actual_fields != expected_step_fields:
            missing = sorted(expected_step_fields - actual_fields)
            extra = sorted(actual_fields - expected_step_fields)
            violations.append(
                Violation(
                    rule_id="V06",
                    severity="ERROR",
                    case_id=case_id,
                    step_no=step_no,
                    message=f"Step field mismatch: missing={missing}, extra={extra}",
                )
            )

        phase = step.get("phase")
        operation = step.get("operation")
        state = step.get("state")
        evidence_id = step.get("evidence_id")

        # V07: phase in allowed set and monotonic order
        if phase not in ALLOWED_PHASES:
            violations.append(
                Violation(
                    rule_id="V07",
                    severity="ERROR",
                    case_id=case_id,
                    step_no=step_no,
                    message=f"Invalid phase '{phase}'; allowed: {ALLOWED_PHASES}",
                )
            )
        else:
            curr_order = PHASE_ORDER[phase]
            if curr_order < prev_phase_order:
                violations.append(
                    Violation(
                        rule_id="V07",
                        severity="ERROR",
                        case_id=case_id,
                        step_no=step_no,
                        message=f"Non-monotonic phase sequence: '{prev_phase_name}' followed by '{phase}'",
                    )
                )
            prev_phase_order = curr_order
            prev_phase_name = phase

        # V08: (operation, state) legal pair and phase match
        if (operation, state) not in LEGAL_OPERATION_STATE_PAIRS:
            violations.append(
                Violation(
                    rule_id="V08",
                    severity="ERROR",
                    case_id=case_id,
                    step_no=step_no,
                    message=f"Illegal (operation, state) pair: ('{operation}', '{state}')",
                )
            )
        elif phase in ALLOWED_PHASES and OPERATION_TO_PHASE.get(operation) != phase:
            violations.append(
                Violation(
                    rule_id="V08",
                    severity="ERROR",
                    case_id=case_id,
                    step_no=step_no,
                    message=f"Operation '{operation}' belongs to phase '{OPERATION_TO_PHASE.get(operation)}', not '{phase}'",
                )
            )

        # V09: evidence_id is "" or exists in manifest
        if evidence_id != "" and evidence_id not in manifest:
            violations.append(
                Violation(
                    rule_id="V09",
                    severity="ERROR",
                    case_id=case_id,
                    step_no=step_no,
                    message=f"evidence_id '{evidence_id}' not found in evidence manifest",
                )
            )

        # V10: manifest captured_at <= case audit_at
        if evidence_id and evidence_id in manifest:
            cap_str = manifest[evidence_id]
            parsed_cap = parse_iso_timestamp(cap_str)
            if parsed_cap and parsed_audit_at:
                if parsed_cap > parsed_audit_at:
                    violations.append(
                        Violation(
                            rule_id="V10",
                            severity="ERROR",
                            case_id=case_id,
                            step_no=step_no,
                            message=f"evidence_id '{evidence_id}' captured_at ({cap_str}) > case audit_at ({case_audit_at})",
                        )
                    )
            elif cap_str and case_audit_at and cap_str > case_audit_at:
                violations.append(
                    Violation(
                        rule_id="V10",
                        severity="ERROR",
                        case_id=case_id,
                        step_no=step_no,
                        message=f"evidence_id '{evidence_id}' captured_at ({cap_str}) > case audit_at ({case_audit_at})",
                    )
                )

    return violations


def check_warn_conventions(
    case_id: str,
    status: str,
    steps: list[dict[str, Any]],
    id_sort: str = "lexical",
) -> list[Violation]:
    """W01-W06: Convention checks (inferred from 32 samples)."""
    violations: list[Violation] = []
    sort_fn: Callable[[str], Any] = natural_sort_key if id_sort == "natural" else (lambda x: x)

    # W01: INCOMPLETE: REMEDIATION and VERIFICATION evidence_id == ""
    if status == STATUS_INCOMPLETE:
        for s in steps:
            phase = s.get("phase")
            ev_id = s.get("evidence_id")
            if phase in (PHASE_REMEDIATION, PHASE_VERIFICATION) and ev_id != "":
                violations.append(
                    Violation(
                        rule_id="W01",
                        severity="WARN",
                        case_id=case_id,
                        step_no=s.get("step_no"),
                        message=f"INCOMPLETE case {phase} step has non-empty evidence_id '{ev_id}'",
                    )
                )

    # W02: every FINDING has matching REMEDIATION and every REMEDIATION matching VERIFICATION
    if status == STATUS_INCOMPLETE:
        by_resource: dict[tuple[str, str], dict[str, list[dict[str, Any]]]] = {}
        for s in steps:
            key = (s.get("system_id", ""), s.get("resource_id", ""))
            by_resource.setdefault(key, {}).setdefault(s.get("phase", ""), []).append(s)

        for (sys_id, res_id), phase_map in by_resource.items():
            findings = phase_map.get(PHASE_FINDING, [])
            remediations = phase_map.get(PHASE_REMEDIATION, [])
            verifications = phase_map.get(PHASE_VERIFICATION, [])

            for f in findings:
                f_op = f.get("operation", "")
                if not remediations:
                    violations.append(
                        Violation(
                            rule_id="W02",
                            severity="WARN",
                            case_id=case_id,
                            step_no=f.get("step_no"),
                            message=f"FINDING '{f_op}' on ({sys_id}, {res_id}) has no matching REMEDIATION",
                        )
                    )
                else:
                    allowed_rems = FINDING_TO_REMEDIATION.get(f_op)
                    if allowed_rems is None:
                        violations.append(
                            Violation(
                                rule_id="W02",
                                severity="WARN",
                                case_id=case_id,
                                step_no=f.get("step_no"),
                                message=f"Operation '{f_op}' has no defined remediation pair",
                            )
                        )
                    else:
                        rem_ops = {r.get("operation") for r in remediations}
                        if not rem_ops.intersection(allowed_rems):
                            violations.append(
                                Violation(
                                    rule_id="W02",
                                    severity="WARN",
                                    case_id=case_id,
                                    step_no=remediations[0].get("step_no"),
                                    message=f"Remediation operations {rem_ops} do not match FINDING '{f_op}' (allowed: {allowed_rems}) on ({sys_id}, {res_id})",
                                )
                            )

            for r in remediations:
                r_op = r.get("operation", "")
                if not verifications:
                    violations.append(
                        Violation(
                            rule_id="W02",
                            severity="WARN",
                            case_id=case_id,
                            step_no=r.get("step_no"),
                            message=f"REMEDIATION '{r_op}' on ({sys_id}, {res_id}) has no matching VERIFICATION",
                        )
                    )
                else:
                    expected_ver = REMEDIATION_TO_VERIFICATION.get(r_op)
                    if not expected_ver:
                        violations.append(
                            Violation(
                                rule_id="W02",
                                severity="WARN",
                                case_id=case_id,
                                step_no=r.get("step_no"),
                                message=f"Remediation operation '{r_op}' has no defined verification pair",
                            )
                        )
                    else:
                        ver_ops = {v.get("operation") for v in verifications}
                        if expected_ver not in ver_ops:
                            violations.append(
                                Violation(
                                    rule_id="W02",
                                    severity="WARN",
                                    case_id=case_id,
                                    step_no=verifications[0].get("step_no"),
                                    message=f"Expected verification '{expected_ver}' for remediation '{r_op}', found {ver_ops} on ({sys_id}, {res_id})",
                                )
                            )

    # W03: within a phase: operation order = table order, then system_id, then resource_id under id_sort
    by_phase: dict[str, list[dict[str, Any]]] = {}
    for s in steps:
        by_phase.setdefault(s.get("phase", ""), []).append(s)

    for phase, p_steps in by_phase.items():
        expected_sorted = sorted(
            p_steps,
            key=lambda s: (
                OPERATION_ORDER_WITHIN_PHASE.get(s.get("operation", ""), 99),
                sort_fn(s.get("system_id", "")),
                sort_fn(s.get("resource_id", "")),
            ),
        )
        if p_steps != expected_sorted:
            for actual, exp in zip(p_steps, expected_sorted):
                if actual != exp:
                    violations.append(
                        Violation(
                            rule_id="W03",
                            severity="WARN",
                            case_id=case_id,
                            step_no=actual.get("step_no"),
                            message=f"Step in phase '{phase}' out of order (found {actual.get('operation')}/{actual.get('system_id')}/{actual.get('resource_id')}, expected {exp.get('operation')}/{exp.get('system_id')}/{exp.get('resource_id')} under {id_sort} sort)",
                        )
                    )
                    break

    # W04: no duplicate steps (same phase, operation, system_id, resource_id, state)
    seen_steps = set()
    for s in steps:
        tup = (
            s.get("phase"),
            s.get("operation"),
            s.get("system_id"),
            s.get("resource_id"),
            s.get("state"),
        )
        if tup in seen_steps:
            violations.append(
                Violation(
                    rule_id="W04",
                    severity="WARN",
                    case_id=case_id,
                    step_no=s.get("step_no"),
                    message=f"Duplicate step tuple in case: {tup}",
                )
            )
        seen_steps.add(tup)

    # W05: no REMEDIATION on a resource whose rule category is RETAIN
    # (use deletion_rules conventions: security_service / audit_record / legal_hold)
    for s in steps:
        if s.get("phase") == PHASE_REMEDIATION:
            sys_id = s.get("system_id", "")
            res_id = s.get("resource_id", "")
            # Recognizable RETAIN patterns from deletion_rules
            is_retain = (
                sys_id == "security_service"
                or res_id.startswith("audit_record_")
                or res_id.startswith("legal_hold_")
            )
            if is_retain:
                violations.append(
                    Violation(
                        rule_id="W05",
                        severity="WARN",
                        case_id=case_id,
                        step_no=s.get("step_no"),
                        message=f"Remediation proposed on retained resource: ({sys_id}, {res_id})",
                    )
                )

    # W06: INCOMPLETE verification contains the user's account VERIFY_RECORD_ABSENT step
    if status == STATUS_INCOMPLETE:
        has_account_absent = any(
            s.get("phase") == PHASE_VERIFICATION
            and s.get("system_id") == "account_service"
            and s.get("operation") == "VERIFY_RECORD_ABSENT"
            for s in steps
        )
        if not has_account_absent:
            violations.append(
                Violation(
                    rule_id="W06",
                    severity="WARN",
                    case_id=case_id,
                    step_no=None,
                    message="INCOMPLETE case verification does not contain account_service VERIFY_RECORD_ABSENT",
                )
            )

    return violations


def validate_output(
    path: str | Path,
    requests_path: str | Path,
    evidence_manifest_path: str | Path,
    expected_rows: int | None = None,
    id_sort: str = "lexical",
) -> list[Violation]:
    """
    Main validator entry point.
    Returns list of Violations.
    """
    violations: list[Violation] = []
    output_path = Path(path)
    req_path = Path(requests_path)
    man_path = Path(evidence_manifest_path)

    if not output_path.exists():
        return [
            Violation(
                rule_id="V01",
                severity="ERROR",
                case_id="<FILE>",
                step_no=None,
                message=f"Output file does not exist: {output_path}",
            )
        ]

    # Load requests metadata: case_ids and audit_at
    request_case_ids: list[str] = []
    case_audit_at: dict[str, str] = {}
    if req_path.exists():
        with open(req_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                cid = row.get("case_id", "")
                if cid:
                    request_case_ids.append(cid)
                    case_audit_at[cid] = row.get("audit_at", "")

    # Load manifest: file_id -> captured_at
    manifest: dict[str, str] = {}
    if man_path.exists():
        with open(man_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                fid = row.get("file_id", "")
                if fid:
                    manifest[fid] = row.get("captured_at", "")

    # Read output file
    rows: list[list[str]] = []
    header: list[str] = []
    with open(output_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
        except StopIteration:
            return [
                Violation(
                    rule_id="V01",
                    severity="ERROR",
                    case_id="<HEADER>",
                    step_no=None,
                    message="Output file is empty",
                )
            ]
        for r in reader:
            if r:
                rows.append(r)

    # V01: Check header
    violations.extend(check_header(header))

    output_case_ids = [r[0] for r in rows if len(r) > 0]

    # V02: Requests alignment and row count
    violations.extend(check_requests_alignment(output_case_ids, request_case_ids, expected_rows))

    # V03: Sorting
    violations.extend(check_case_sorting(output_case_ids, id_sort=id_sort))

    # Row-by-row checks
    for row in rows:
        if len(row) < 3:
            violations.append(
                Violation(
                    rule_id="V01",
                    severity="ERROR",
                    case_id=row[0] if row else "<ROW>",
                    step_no=None,
                    message=f"Row has {len(row)} columns, expected 3",
                )
            )
            continue

        case_id = row[0]
        deletion_status = row[1]
        steps_raw = row[2]

        # V11: Status validity
        violations.extend(check_status_validity(case_id, deletion_status))

        # V04: steps_json parse
        try:
            steps = json.loads(steps_raw)
            if not isinstance(steps, list):
                violations.append(
                    Violation(
                        rule_id="V04",
                        severity="ERROR",
                        case_id=case_id,
                        step_no=None,
                        message=f"steps_json is not a JSON array (got {type(steps).__name__})",
                    )
                )
                continue
        except Exception as e:
            violations.append(
                Violation(
                    rule_id="V04",
                    severity="ERROR",
                    case_id=case_id,
                    step_no=None,
                    message=f"Invalid JSON in steps_json: {e}",
                )
            )
            continue

        # V12: NOT_APPLICABLE <=> steps == []
        violations.extend(check_not_applicable_rule(case_id, deletion_status, steps))

        # V13: COMPLETE checks
        violations.extend(check_complete_rule(case_id, deletion_status, steps))

        # V14: INCOMPLETE checks
        violations.extend(check_incomplete_finding_rule(case_id, deletion_status, steps))

        # V05, V06, V07, V08, V09, V10: Per-step field and integrity checks
        violations.extend(
            check_steps_structure_and_order(
                case_id=case_id,
                steps=steps,
                manifest=manifest,
                case_audit_at=case_audit_at.get(case_id),
                id_sort=id_sort,
            )
        )

        # W01-W06: Convention checks
        violations.extend(
            check_warn_conventions(
                case_id=case_id,
                status=deletion_status,
                steps=steps,
                id_sort=id_sort,
            )
        )

    return violations


def main() -> None:
    parser = argparse.ArgumentParser(description="Ghost Audit Output Validator")
    parser.add_argument("--output", "-o", required=True, help="Path to output CSV file")
    parser.add_argument("--requests", "-r", required=True, help="Path to requests CSV file")
    parser.add_argument("--manifest", "-m", required=True, help="Path to evidence manifest CSV file")
    parser.add_argument("--expected-rows", "-n", type=int, default=None, help="Expected number of data rows")
    parser.add_argument("--id-sort", choices=["lexical", "natural"], default="lexical", help="Case and ID sort order")

    args = parser.parse_args()

    violations = validate_output(
        path=args.output,
        requests_path=args.requests,
        evidence_manifest_path=args.manifest,
        expected_rows=args.expected_rows,
        id_sort=args.id_sort,
    )

    errors = [v for v in violations if v.severity == "ERROR"]
    warns = [v for v in violations if v.severity == "WARN"]

    # Group violations by rule_id
    by_rule: dict[str, list[Violation]] = {}
    for v in violations:
        by_rule.setdefault(v.rule_id, []).append(v)

    print("================================================================================")
    print("GHOST AUDIT VALIDATION SUMMARY")
    print("================================================================================")
    print(f"Target Output: {args.output}")
    print(f"ID Sort Mode:  {args.id_sort}")
    print(f"Total Errors:  {len(errors)}")
    print(f"Total Warns:   {len(warns)}")
    print("--------------------------------------------------------------------------------")
    print("Violations by Rule:")
    for rule_id in sorted(by_rule.keys()):
        rule_viols = by_rule[rule_id]
        sev = rule_viols[0].severity
        print(f"  [{sev}] {rule_id:<4}: {len(rule_viols):>4} occurrences")
    print("--------------------------------------------------------------------------------")

    if warns:
        print("\nWarnings Detail (sample):")
        for w in warns[:15]:
            step_str = f" step={w.step_no}" if w.step_no is not None else ""
            print(f"  [{w.rule_id}] case={w.case_id}{step_str}: {w.message}")
        if len(warns) > 15:
            print(f"  ... and {len(warns) - 15} more warnings.")

    if errors:
        print("\nERRORS Detail:")
        for e in errors[:20]:
            step_str = f" step={e.step_no}" if e.step_no is not None else ""
            print(f"  [{e.rule_id}] case={e.case_id}{step_str}: {e.message}")
        if len(errors) > 20:
            print(f"  ... and {len(errors) - 20} more errors.")
        sys.exit(1)

    print("\nValidation PASSED (0 errors).")
    sys.exit(0)


if __name__ == "__main__":
    main()
