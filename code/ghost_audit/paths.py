from pathlib import Path

# Repository root resolved relative to this module
PACKAGE_DIR = Path(__file__).resolve().parent
CODE_DIR = PACKAGE_DIR.parent
REPO_ROOT = CODE_DIR.parent

DATASET_DIR = REPO_ROOT / "dataset"
EVIDENCE_DIR = DATASET_DIR / "evidence"
MANIFEST_PATH = DATASET_DIR / "evidence_files.csv"
DELETION_REQUESTS_PATH = DATASET_DIR / "deletion_requests.csv"
SAMPLE_REQUESTS_PATH = DATASET_DIR / "sample_deletion_requests.csv"
SAMPLE_OUTPUT_PATH = DATASET_DIR / "sample_output.csv"
USER_IDENTITIES_PATH = DATASET_DIR / "user_identities.csv"
USER_AUDIT_LOG_PATH = DATASET_DIR / "user_audit_log.csv"
SYSTEM_ACTIVITY_PATH = DATASET_DIR / "system_activity.csv"
DELETION_RULES_PATH = DATASET_DIR / "deletion_rules.csv"

CACHE_DIR = CODE_DIR / ".cache"
OUTPUT_PATH = REPO_ROOT / "output.csv"
