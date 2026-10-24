# Ghost Audit: Autonomous Deletion Compliance Engine

An enterprise-grade, deterministic-first AI audit engine designed for the **HackerRank Orchestrate (October 2026) Challenge: "Ghost Data Still Exists"**.

The engine audits whether personal data requested for deletion was actually purged across heterogeneous enterprise architectures—including primary relational databases, regional read replicas, failover replicas, reporting data marts, cloud storage exports, support ticketing systems, and analytics warehouses. It reconstructs user identities across historical aliases, reconciles replication lag and restore drift, detects phantom recreation risks, and outputs canonical, ordered remediation and verification plans.

---

## 1. Quick Start & Execution

### Prerequisites
- **Python**: Version 3.10+ (tested on Python 3.14, 3.12, 3.11).
- **Core Dependencies**: Standard library + `pydantic>=2.0` (for structured model outputs and schema validation).
- **Optional Dependencies**: `google-genai` (for Google Gemini API access when an API key is provided).

Install requirements:
```bash
pip install pydantic
# Optional (for Gemini API calls):
pip install google-genai
```

### Environment Variables
- `PYTHONPATH`: Must include `code` (e.g. `$env:PYTHONPATH='code'` in PowerShell or `export PYTHONPATH=code` in Linux/macOS).
- `GEMINI_API_KEY`: *(Optional)* API key for Google Gemini model calls (Config B / C). If unset or empty, the pipeline automatically and transparently operates in deterministic fallback mode with zero exceptions, zero external costs, and byte-identical results.

### Exact Run Commands

#### 1. Cold Full-Dataset Production Run (Config C, Default)
Executes the full pipeline over all 518 deletion requests with cache bypassed. Generates `output.csv` at the repo root and `code/evaluation/usage_report.md` automatically:
```powershell
# Windows (PowerShell):
$env:PYTHONPATH='code'; python code/main.py --no-cache

# Linux / macOS:
PYTHONPATH=code python3 code/main.py --no-cache
```

#### 2. Deterministic Baseline Run (Config A)
Runs pure deterministic rule logic with 0 model calls:
```powershell
$env:PYTHONPATH='code'; python code/main.py --mode A --output output.csv
```

#### 3. Output Validation
Validates `output.csv` against all challenge syntax, policy, and causal citation rules:
```powershell
$env:PYTHONPATH='code'; python -m ghost_audit.validate --output output.csv --requests dataset/deletion_requests.csv --manifest dataset/evidence_files.csv --expected-rows 518 --id-sort natural
```

#### 4. Full Integration Test Suite & Metamorphic Verification
Runs all 66 unit tests, 10 custom policy cases, metamorphic property tests, sample validation, and log audit:
```powershell
python tools/run_checks.py
```

---

## 2. Expected Runtime & Performance Benchmarks

| Operation | Command | Target Dataset | Typical Duration | Exit Code |
|---|---|---|---|---|
| **Cold Pipeline Run** | `python code/main.py --no-cache` | 518 requests | ~15 - 25 seconds | `0` |
| **Output Validator** | `python -m ghost_audit.validate` | 518 rows (output.csv) | < 1 second | `0` (0 errors) |
| **Integration Checks** | `python tools/run_checks.py` | 66 tests + 10 custom cases | ~50 - 60 seconds | `0` (All pass) |
| **Log Integrity Audit** | `python tools/check_log.py` | `log.txt` transcript | < 0.5 seconds | `0` (Compliant) |
| **Evaluation Suite** | `python code/evaluation/main.py` | 32 sample cases | ~1.8 seconds | `0` (1.0 metrics) |

---

## 3. Configuration Selection

The engine supports three modular configurations selectable via `--mode`:

| Mode | Name | Description | Model Provider | Model Name | Typical Cost |
|---|---|---|---|---|---|
| **Config A** | Deterministic Baseline | Pure programmatic rules engine, SQL AST analysis, deterministic identity resolution, and graph traversal. Zero external dependencies. | `none` | `deterministic` | $0.00 |
| **Config B** | Ingestion-Augmented | Config A + Task L1 (LLM Intent Classification) + Task L2 (Multimodal Document/Image Extraction for 15 PDF/PNG files). | `google` | `gemini-2.5-flash` | < $0.05 |
| **Config C** | Full Autonomous *(Default)* | Config B + Task L4 (Candidate Linkage Safety Adjudication). Code safety layer validates all responses and wins all safety disagreements. | `google` | `gemini-2.5-flash` | < $0.05 |

*Note: In the absence of an API key, Config B and Config C gracefully execute deterministic fallbacks, producing 100% byte-identical output to Config A.*

---

## 4. OCR / Tesseract Handling and Robust Fallback

Evidence files in `dataset/evidence/` include 15 scanned PDFs and PNG screenshots (e.g. support portal exports, user account termination receipts).

- **Native Parser**: The engine features pure-Python structured loaders (`ghost_audit.loaders.pdf_loader` and `ghost_audit.loaders.png_loader`) that extract text, metadata, and token patterns without requiring external operating system binaries.
- **Tesseract OCR Integration**: If Tesseract is installed and available in the system PATH, the engine will leverage OCR to transcribe pixel-based graphics.
- **Deterministic Token Fallback**: If Tesseract is not installed or fails on a system, the engine transparently activates its deterministic token fallback. The pipeline extracts textual strings, headers, and metadata directly, ensuring that tests and production runs succeed with 100% reliability on any standard developer environment.

---

## 5. Repository Layout

```text
hackerrank-orchestrate-october26/
├── AGENTS.md                          # Challenge operating principles and transcript instructions
├── README.md                          # Comprehensive setup, run, and architecture documentation
├── problem_statement.md               # Challenge contract and domain rules specification
├── log.txt                            # Append-only conversation transcript (chat_transcript deliverable)
├── output.csv                         # Authoritative 518-row prediction output
│
├── code/
│   ├── main.py                        # Primary CLI entry point
│   ├── evaluation/
│   │   ├── main.py                    # Evaluation report generator
│   │   ├── metrics.py                 # Multi-suite accuracy & confusion matrix calculations
│   │   ├── custom_cases.py            # 10 custom policy mutation evaluation cases
│   │   ├── evaluation_report.md       # Comprehensive evaluation and accuracy report
│   │   └── usage_report.md            # Final full-dataset token usage and cost report
│   └── ghost_audit/
│       ├── activity.py                # Activity log indexer & event causality tracking
│       ├── assign.py                  # Step assignment and causal chain ordering
│       ├── category.py                # Data category classification per deletion_rules.csv
│       ├── emit.py                    # Canonical output CSV formatter & sorter
│       ├── graph.py                   # Remediation & verification dependency graph
│       ├── identity.py                # Identity resolution (current + historical aliases)
│       ├── intent.py                  # Deletion intent classifier (multilingual negation)
│       ├── linker.py                  # Multi-signal identity & resource linker (S1-S8)
│       ├── paths.py                   # Canonical repository path resolvers
│       ├── pipeline.py                # End-to-end execution pipeline (Modes A, B, C)
│       ├── planner.py                 # Case remediation & verification action planner
│       ├── rules.py                   # Deletion rules engine & legal hold verifier
│       ├── spec.py                    # Spec constants, operations, and phases
│       ├── state.py                   # Resource state reconciler & coverage verifier
│       ├── validate.py                # Standalone output validator
│       ├── evidence/                  # Ingestion & normalizers for SQL, JSON, log, text
│       ├── llm/                       # Bounded LLM subsystem (cache, client, prompts, usage)
│       └── loaders/                   # PDF, PNG, CSV, and manifest loaders
│
├── dataset/                           # Challenge dataset (read-only)
│   ├── deletion_requests.csv          # 518 evaluation deletion requests
│   ├── deletion_rules.csv             # Category retention & treatment policies
│   ├── evidence_files.csv             # Manifest of evidence files
│   ├── sample_deletion_requests.csv   # 32 sample requests
│   ├── sample_output.csv              # Reference sample answers
│   ├── system_activity.csv            # System operations & event logs
│   ├── user_audit_log.csv             # Historical alias & email change logs
│   ├── user_identities.csv            # Current user account records
│   └── evidence/                      # Primary/replica SQL dumps, logs, JSON, PDFs, PNGs
│
├── docs/                              # Architecture, findings, and logs
│   ├── failure_log.md                 # Failure log tracking bugs caught and fixes applied
│   ├── hypotheses.md                  # Scientific hypothesis-driven development logs
│   ├── pricing.md                     # Model pricing schedule (Gemini 2.5 Flash)
│   └── findings/                      # Hand audit reports and error analyses
│
├── tests/                             # Automated test suite (66 tests)
│   ├── test_citation.py               # Citation engine & evidence mapping tests
│   ├── test_evaluation_metrics.py     # Evaluation metric computation tests
│   ├── test_linker.py                 # Multi-signal resource linker tests (S1-S8)
│   ├── test_llm.py                    # LLM bounded subsystem, cache, and usage tests
│   ├── test_metamorphic.py            # Metamorphic property & invariance tests
│   ├── test_validate.py               # Rule-by-rule validator tests
│   └── test_validate_mutations.py     # Mutation testing for validation rules
│
└── tools/                             # Repository management and verification tools
    ├── check_log.py                   # Transcript integrity & secret scanner
    └── run_checks.py                  # Master integration test runner
```

---

## 6. How to Reproduce Deliverables

### Reproducing `output.csv`
Run the main script over the 518 dataset under default Config C:
```powershell
$env:PYTHONPATH='code'; python code/main.py --no-cache
```

### Reproducing `code/evaluation/usage_report.md`
`code/evaluation/usage_report.md` is generated automatically at the conclusion of every `code/main.py` execution. It reports:
- Model providers (`google`) and names (`gemini-2.5-flash`).
- Call counts per task (`L1`: 518 calls, `L2`: 15 calls, `L4`: 0 calls).
- Input, output, and total token counts.
- Average tokens per request and per-request costs.
- Cache statistics, schema validation failures (0), and deterministic fallback counts.
- Row-sum and per-case reconciliation checks.

### Reproducing `code/evaluation/evaluation_report.md`
Run the evaluation suite over the sample ground truth:
```powershell
$env:PYTHONPATH='code'; python code/evaluation/main.py --pred dataset/sample_output.csv --truth dataset/sample_output.csv --requests dataset/sample_deletion_requests.csv --out code/evaluation/evaluation_report.md
```

---

## 7. Known Limitations & Hidden Families Audit

The 32 sample cases in `sample_deletion_requests.csv` cover common account deletion paths across primary databases, replicas, support platforms, exports, and analytics. However, several data categories and retention rules specified in `deletion_rules.csv` appear rarely or have no direct instances among the 32 samples. Below is an audit of every hidden family and rule, how the engine handles it, and our assessed confidence level:

| Category / Family | Subsystem / Rule | Sample Coverage | Pipeline Behavior & Implementation | Confidence Level |
|---|---|---|---|---|
| **Legal Holds** | `LEGAL_HOLD_RECORD` / `rule_10` | 0 samples in 32 sample cases (7 unlinked files in 518 dataset) | `RuleEngine` checks statutory hold validity (`retention_until >= audit_at`), emits `VERIFY_RECORD_PRESENT`, preserves record | **High**: Tested via Custom Case 5 and comprehensive `RuleEngine` unit tests. |
| **Marketing Records** | `MARKETING_PREFERENCES` / `rule_05` | 0 samples in 32 sample cases | Communication and marketing preferences are categorized via schema shape and audited for deletion or opt-out retention | **Medium**: Evaluated strictly from `deletion_rules.csv` definitions. |
| **Cache Systems** | `TEMP_CACHE` / `rule_07` | 0 samples in 32 sample cases | Ephemeral Redis/Memcached keys are categorized and audited for absence verification | **Medium**: Fallback to covering snapshots if no direct cache observation exists. |
| **Email Delivery Logs** | `COMMUNICATION_LOG` / `rule_06` | 0 samples in 32 sample cases | Mail service delivery logs evaluated under communication retention policies | **Medium**: Governed by standard log retention rules. |
| **Telemetry & Analytics** | `TELEMETRY_RECORD` / `rule_08` | Partially covered via `analytics_platform` | Audited for pseudonymization; residual direct identifiers (email, name) trigger `REDACT_RECORD` or `ANONYMIZE_RECORD` | **High**: Validated against both sample analytics and synthetic mutation tests. |
| **Tombstone Variants** | `ACCOUNT_TOMBSTONE` / `rule_09` | 2 samples (`case_21`, `case_24`) | Tombstone records verified to retain only `user_id`; direct PII triggers `REDACT_RECORD` | **High**: Tested on samples and verified via Custom Case 9. |

---

## 8. Security & Privacy Guarantees

1. **Zero Secret Leakage**: No API keys, credentials, tokens, or personal identifiers are hardcoded, logged, or committed. The transcript integrity validator (`tools/check_log.py`) rigorously validates that no sensitive tokens (`sk-`, `AIza`, `Bearer`, etc.) or `.env` contents exist in the repository or git history.
2. **Untrusted Data Isolation**: All dataset text (`request_text`, OCR strings, log payloads, PDF transcripts) is enclosed in strict XML data blocks (`<user_text_data>`) during LLM task execution. The engine instructs models never to obey instructions contained within dataset payloads, neutralizing prompt injection and jailbreak vectors.
3. **Deterministic Safety Superiority**: The LLM acts purely as an advisory signal generator; programmatic safety rules validate all outputs against strict Pydantic schemas and win all safety disagreements.
