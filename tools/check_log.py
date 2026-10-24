#!/usr/bin/env python3
"""
Log integrity validator for HackerRank Orchestrate (October 2026).
Enforces AGENTS.md §3, §5, and README transcript logging requirements:
- Valid header `## [ISO-8601] title`
- Complete §5.1 fields on SESSION START
- Exactly one non-empty, non-generic, non-placeholder, non-unknown tool= and model=
- Model name not used as tool name
- Required sections in per-turn entries
- No secrets (sk-, AIza, Bearer, api_key=, .env values)
- Append-only compared to `git show HEAD:log.txt`
"""

import os
import re
import subprocess
import sys
from pathlib import Path

# Header format: ## [ISO-8601] title
HEADER_RE = re.compile(
    r"^##\s+(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2}))\s+(.+)$"
)

# Secret patterns
SECRET_PATTERNS = [
    (re.compile(r"\bsk-[a-zA-Z0-9_\-]{4,}\b"), "Secret pattern: sk-..."),
    (re.compile(r"\bAIza[0-9A-Za-z\-_]{10,}\b"), "Google API key pattern: AIza..."),
    (re.compile(r"\bBearer\s+[a-zA-Z0-9_\-\.]{10,}\b"), "Authorization Bearer token"),
    (re.compile(r"api_key\s*=\s*['\"]?[a-zA-Z0-9_\-]{4,}", re.IGNORECASE), "API key assignment: api_key=..."),
]

# Required §5.1 fields for SESSION START
REQUIRED_SESSION_START_FIELDS = [
    "tool=",
    "model=",
    "Repo Root:",
    "Branch:",
    "Worktree:",
    "Parent Agent:",
    "Language:",
    "Time Remaining:",
]

# Required sections for per-turn entries
REQUIRED_PER_TURN_SECTIONS = [
    ("User Prompt (verbatim", "User Prompt (verbatim…)"),
    ("Agent Response Summary:", "Agent Response Summary:"),
    ("Actions:", "Actions:"),
    ("Context:", "Context:"),
]

GENERIC_NAMES = {"ai", "llm", "agent", "assistant", "coding agent", "bot", "model", "generic"}
MODEL_NAMES_AS_TOOLS = {
    "gemini", "gemini-3.8-flash", "gemini-1.5-pro", "gemini-2.0-flash",
    "gpt", "gpt-4", "gpt-4o", "gpt-3.5", "claude-3-5-sonnet", "sonnet", "opus", "haiku"
}


def load_dotenv_secrets(repo_root: Path) -> list[str]:
    secrets = []
    dotenv = repo_root / ".env"
    if dotenv.exists():
        try:
            for line in dotenv.read_text(encoding="utf-8", errors="replace").splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    _, val = line.split("=", 1)
                    val = val.strip().strip("'\"")
                    if len(val) >= 4 and val.lower() not in {
                        "true", "false", "development", "production", "none", "null", "test"
                    }:
                        secrets.append(val)
        except Exception as e:
            print(f"Warning: could not read .env: {e}", file=sys.stderr)
    return secrets


def check_append_only(log_path: Path) -> list[str]:
    violations = []
    try:
        proc = subprocess.run(
            ["git", "show", "HEAD:log.txt"],
            capture_output=True,
            check=False
        )
        if proc.returncode != 0:
            # log.txt is not yet committed in HEAD (initial state)
            return []

        head_bytes = proc.stdout
        current_bytes = log_path.read_bytes()

        if not current_bytes.startswith(head_bytes):
            head_norm = head_bytes.decode("utf-8", errors="replace").replace("\r\n", "\n")
            curr_norm = current_bytes.decode("utf-8", errors="replace").replace("\r\n", "\n")
            if not (curr_norm.startswith(head_norm) or curr_norm.startswith(head_norm.rstrip())):
                violations.append(
                    "Append-only failure: log.txt content does not match git show HEAD:log.txt at earlier bytes."
                )

    except FileNotFoundError:
        violations.append("git command not found; cannot verify append-only state.")
    except Exception as e:
        violations.append(f"Error checking git show HEAD:log.txt: {e}")
    return violations


def validate_log(log_path: Path) -> list[str]:
    violations = []

    if not log_path.exists():
        return [f"Log file not found: {log_path}"]

    content = log_path.read_text(encoding="utf-8", errors="replace")
    if not content.strip():
        return [f"Log file is empty: {log_path}"]

    # 1. Append-only check
    violations.extend(check_append_only(log_path))

    # 2. Secret check against .env values
    repo_root = log_path.parent
    dotenv_secrets = load_dotenv_secrets(repo_root)
    for s in dotenv_secrets:
        if s in content:
            violations.append(f"Secret value from .env found in log file: [REDACTED_{s[:3]}...]")

    # 3. Secret check against regexes
    for pattern, desc in SECRET_PATTERNS:
        match = pattern.search(content)
        if match:
            violations.append(f"Potential secret detected ({desc}): '{match.group(0)[:15]}...'")

    # 4. Entry-by-entry validation
    lines = content.splitlines()
    entry_indices = [i for i, line in enumerate(lines) if line.startswith("## ")]

    if not entry_indices:
        return [f"No entries found starting with '## ' in {log_path}"]

    if entry_indices[0] != 0:
        preamble = "\n".join(lines[:entry_indices[0]]).strip()
        if preamble:
            violations.append(f"Unexpected content before first entry header: '{preamble[:60]}...'")

    entries = []
    for idx, start_line in enumerate(entry_indices):
        end_line = entry_indices[idx + 1] if idx + 1 < len(entry_indices) else len(lines)
        entry_lines = lines[start_line:end_line]
        entries.append((start_line + 1, entry_lines))

    for line_num, entry_lines in entries:
        header = entry_lines[0].strip()
        header_match = HEADER_RE.match(header)
        if not header_match:
            violations.append(
                f"Line {line_num}: Header '{header}' does not match format '## [ISO-8601] title'"
            )
            continue

        timestamp, title = header_match.groups()
        title = title.strip()
        entry_text = "\n".join(entry_lines)

        # Check tool= and model= counts and values
        tool_matches = []
        model_matches = []
        for l in entry_lines:
            tm = re.match(r"^\s*tool\s*=\s*(.*?)\s*$", l)
            if tm:
                tool_matches.append(tm.group(1).strip())
            mm = re.match(r"^\s*model\s*=\s*(.*?)\s*$", l)
            if mm:
                model_matches.append(mm.group(1).strip())

        # Validate tool=
        if len(tool_matches) == 0:
            violations.append(f"Entry '{title}' ({timestamp}, line {line_num}): missing 'tool=' line")
        elif len(tool_matches) > 1:
            violations.append(
                f"Entry '{title}' ({timestamp}, line {line_num}): expected exactly one 'tool=' line, found {len(tool_matches)}"
            )
        else:
            t_val = tool_matches[0]
            if not t_val:
                violations.append(f"Entry '{title}' ({timestamp}, line {line_num}): 'tool=' is empty")
            elif t_val.lower() == "unknown":
                violations.append(f"Entry '{title}' ({timestamp}, line {line_num}): 'tool=' is 'unknown'")
            elif ("<" in t_val and ">" in t_val) or t_val.lower() in {"todo", "fixme", "placeholder"}:
                violations.append(f"Entry '{title}' ({timestamp}, line {line_num}): 'tool=' has placeholder '{t_val}'")
            elif t_val.lower() in GENERIC_NAMES:
                violations.append(f"Entry '{title}' ({timestamp}, line {line_num}): 'tool=' has generic name '{t_val}'")
            elif t_val.lower() in MODEL_NAMES_AS_TOOLS or (len(model_matches) == 1 and t_val.lower() == model_matches[0].lower()):
                violations.append(
                    f"Entry '{title}' ({timestamp}, line {line_num}): tool name '{t_val}' appears to be a model name"
                )

        # Validate model=
        if len(model_matches) == 0:
            violations.append(f"Entry '{title}' ({timestamp}, line {line_num}): missing 'model=' line")
        elif len(model_matches) > 1:
            violations.append(
                f"Entry '{title}' ({timestamp}, line {line_num}): expected exactly one 'model=' line, found {len(model_matches)}"
            )
        else:
            m_val = model_matches[0]
            if not m_val:
                violations.append(f"Entry '{title}' ({timestamp}, line {line_num}): 'model=' is empty")
            elif m_val.lower() == "unknown":
                violations.append(f"Entry '{title}' ({timestamp}, line {line_num}): 'model=' is 'unknown'")
            elif ("<" in m_val and ">" in m_val) or m_val.lower() in {"todo", "fixme", "placeholder"}:
                violations.append(f"Entry '{title}' ({timestamp}, line {line_num}): 'model=' has placeholder '{m_val}'")
            elif m_val.lower() in GENERIC_NAMES:
                violations.append(f"Entry '{title}' ({timestamp}, line {line_num}): 'model=' has generic name '{m_val}'")

        # Type-specific validation
        if title == "SESSION START":
            # Must contain all §5.1 fields
            for req_field in REQUIRED_SESSION_START_FIELDS:
                field_found = False
                for l in entry_lines:
                    clean_l = l.strip()
                    if clean_l.lower().startswith(req_field.lower()):
                        val = clean_l[len(req_field):].strip()
                        if val:
                            field_found = True
                            break
                if not field_found:
                    violations.append(
                        f"SESSION START entry ({timestamp}, line {line_num}): missing or empty required field '{req_field}'"
                    )
        else:
            # Per-turn entry: must contain User Prompt, Agent Response Summary, Actions, Context
            for req_needle, section_label in REQUIRED_PER_TURN_SECTIONS:
                if req_needle not in entry_text:
                    violations.append(
                        f"Per-turn entry '{title}' ({timestamp}, line {line_num}): missing section '{section_label}'"
                    )

    return violations


def main():
    repo_root = Path(__file__).resolve().parent.parent
    log_path = repo_root / "log.txt"

    if len(sys.argv) > 1:
        log_path = Path(sys.argv[1]).resolve()

    violations = validate_log(log_path)
    if violations:
        print(f"Log validation FAILED with {len(violations)} violation(s):", file=sys.stderr)
        for v in violations:
            print(f"  - {v}", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"Log validation PASSED: {log_path} is healthy, append-only, and fully compliant.")
        sys.exit(0)


if __name__ == "__main__":
    main()
