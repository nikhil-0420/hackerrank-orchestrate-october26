import csv
import json
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent

def run_diagnose():
    print("================================================================================")
    print("STEP 0 DIAGNOSIS: OUTPUT SPECIFICATION & BASELINE INSPECTION")
    print("================================================================================\n")

    # (a) exact output header and field set
    output_header = ["case_id", "deletion_status", "steps_json"]
    step_fields = ["step_no", "phase", "system_id", "resource_id", "operation", "state", "evidence_id"]
    print("--- (a) Output Header and Field Set ---")
    print(f"Output CSV Header: {output_header}")
    print(f"Step Object Fields (exact 7 fields): {step_fields}\n")

    # (b) legal (operation, state) pairs, phase list, operation order table
    phases = ["FINDING", "REMEDIATION", "VERIFICATION"]
    legal_pairs = [
        # FINDING
        ("REPORT_REMAINING_RECORD", "PRESENT"),
        ("REPORT_EXPOSED_PII", "PRESENT"),
        ("REPORT_ACTIVE_DATA_FLOW", "ACTIVE"),
        ("REPORT_RESTORE_RISK", "ACTIVE"),
        # REMEDIATION
        ("DISABLE_DATA_FLOW", "DISABLED"),
        ("BLOCK_RESTORE", "BLOCKED"),
        ("DELETE_RECORD", "ABSENT"),
        ("REDACT_RECORD", "REDACTED"),
        ("ANONYMIZE_RECORD", "ANONYMIZED"),
        # VERIFICATION
        ("VERIFY_RECORD_ABSENT", "ABSENT"),
        ("VERIFY_RECORD_PRESENT", "PRESENT"),
        ("VERIFY_RECORD_REDACTED", "REDACTED"),
        ("VERIFY_RECORD_ANONYMIZED", "ANONYMIZED"),
        ("VERIFY_DATA_FLOW_DISABLED", "DISABLED"),
        ("VERIFY_RESTORE_BLOCKED", "BLOCKED"),
    ]

    op_order_table = [
        ("FINDING", "REPORT_REMAINING_RECORD", "PRESENT", "A record that should have been deleted still exists."),
        ("FINDING", "REPORT_EXPOSED_PII", "PRESENT", "A record may remain, but it still contains identifiers that should have been redacted or anonymized."),
        ("FINDING", "REPORT_ACTIVE_DATA_FLOW", "ACTIVE", "An active process can copy or recreate the user's data."),
        ("FINDING", "REPORT_RESTORE_RISK", "ACTIVE", "A backup or restore path can bring deleted data back."),
        ("REMEDIATION", "DISABLE_DATA_FLOW", "DISABLED", "Stop the process that can copy or recreate the data."),
        ("REMEDIATION", "BLOCK_RESTORE", "BLOCKED", "Prevent the affected backup from restoring the user's data."),
        ("REMEDIATION", "DELETE_RECORD", "ABSENT", "Remove the entire record."),
        ("REMEDIATION", "REDACT_RECORD", "REDACTED", "Keep the record but remove the identifying fields required by policy."),
        ("REMEDIATION", "ANONYMIZE_RECORD", "ANONYMIZED", "Keep the record after irreversibly unlinking it from the user."),
        ("VERIFICATION", "VERIFY_RECORD_ABSENT", "ABSENT", "Confirm that a record no longer exists."),
        ("VERIFICATION", "VERIFY_RECORD_PRESENT", "PRESENT", "Confirm that a policy-required retained record still exists."),
        ("VERIFICATION", "VERIFY_RECORD_REDACTED", "REDACTED", "Confirm that required identifying fields have been removed."),
        ("VERIFICATION", "VERIFY_RECORD_ANONYMIZED", "ANONYMIZED", "Confirm that the record can no longer be linked to the user."),
        ("VERIFICATION", "VERIFY_DATA_FLOW_DISABLED", "DISABLED", "Confirm that the relevant data flow is inactive."),
        ("VERIFICATION", "VERIFY_RESTORE_BLOCKED", "BLOCKED", "Confirm that the affected data cannot be restored."),
    ]

    print("--- (b) Phase List ---")
    print(f"Phases (monotonic order): {phases}\n")

    print("--- (b) Legal (Operation, State) Pairs & Operation Order Table ---")
    for phase, op, state, meaning in op_order_table:
        print(f"  {phase:<14} | {op:<28} | {state:<12} | {meaning}")
    print()

    # (c) header and first 3 rows of requests, manifest, and sample_output
    print("--- (c) Header and First 3 Rows ---")
    files_to_print = [
        ("dataset/deletion_requests.csv", "Requests (Evaluation)"),
        ("dataset/sample_deletion_requests.csv", "Requests (Sample)"),
        ("dataset/evidence_files.csv", "Evidence Manifest"),
        ("dataset/sample_output.csv", "Sample Output (Ground Truth for Samples)"),
    ]

    for rel_path, label in files_to_print:
        p = repo_root / rel_path
        print(f"\n[{label}] Path: {rel_path}")
        with open(p, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)
            print(f"  Header: {header}")
            for i in range(3):
                try:
                    row = next(reader)
                    # Truncate very long fields for readable console display
                    display_row = [c if len(c) < 80 else c[:77] + "..." for c in row]
                    print(f"  Row {i+1}: {display_row}")
                except StopIteration:
                    break

if __name__ == "__main__":
    run_diagnose()
