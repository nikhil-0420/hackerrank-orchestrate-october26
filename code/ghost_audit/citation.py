"""
Deterministic Citation Engine for Ghost Audit.
Resolves citable evidence files for findings and verification checks.
Adheres strictly to time-gating rules: never cites a file captured after audit_at.
"""

from __future__ import annotations

from typing import Dict, List, Optional
from ghost_audit.evidence.coverage import CoverageIndex
from ghost_audit.loaders.manifest import EvidenceFileMeta
from ghost_audit.observation import Observation
from ghost_audit.timegate import citable, parse_iso_ts


def resolve_step_citation(
    resource_id: str,
    system_id: str,
    state: str,
    audit_at: str,
    obs_by_res: Dict[str, List[Observation]],
    coverage_index: Optional[CoverageIndex],
    manifest: Dict[str, EvidenceFileMeta],
    fallback_file_id: Optional[str] = None,
) -> str:
    """
    Resolves the exact citable evidence_id for a given step.
    
    Rules:
    1. An absent record ('ABSENT') cites:
       - The latest citable evidence file containing an explicit NOT_FOUND / 404 line
         (e.g., http_status=404, status_code=404, result='NOT_FOUND', rows=0).
       - Or if no 404 line exists, the latest citable covering snapshot that lacks the record.
    2. A present record ('PRESENT', 'ANONYMIZED', 'REDACTED', 'ACTIVE', etc.) cites:
       - The latest citable evidence file containing the resource observation.
    3. Fallback:
       - Uses fallback_file_id (if citable) or empty string.
    """
    if state == "ABSENT":
        # 1a. Explicit 404 / NOT_FOUND observation
        citable_obs = [
            o for o in obs_by_res.get(resource_id, [])
            if o.file_id in manifest and citable(manifest[o.file_id].captured_at, audit_at)
        ]
        not_found_obs = [
            o for o in citable_obs
            if (
                o.state.get("result") in ["NOT_FOUND", "not_found"]
                or o.state.get("http_status") in [404, "404"]
                or o.state.get("status_code") in [404, "404"]
                or o.state.get("rows") in [0, "0"]
            )
        ]
        if not_found_obs:
            not_found_obs.sort(
                key=lambda o: (parse_iso_ts(manifest[o.file_id].captured_at), o.file_id),
                reverse=True,
            )
            return not_found_obs[0].file_id

        # 1b. Covering snapshot lacking the record
        if coverage_index is not None:
            citable_cov = [
                r for r in coverage_index.records
                if r.system_id.lower() == system_id.lower()
                and citable(r.file_captured_at, audit_at)
            ]
            if citable_cov:
                citable_cov.sort(
                    key=lambda r: (parse_iso_ts(r.file_captured_at), r.file_id),
                    reverse=True,
                )
                return citable_cov[0].file_id

        return fallback_file_id or ""

    else:
        # 2. Present record: latest citable file containing the resource
        citable_obs = [
            o for o in obs_by_res.get(resource_id, [])
            if o.file_id in manifest and citable(manifest[o.file_id].captured_at, audit_at)
        ]
        if citable_obs:
            citable_obs.sort(
                key=lambda o: (parse_iso_ts(manifest[o.file_id].captured_at), o.file_id),
                reverse=True,
            )
            return citable_obs[0].file_id

        return fallback_file_id or ""
