"""
Identity resolution module for Ghost Audit.
Reconstructs current and historical identifiers for users.
Enforces exact matching (never fuzzy) and strict word-boundary matching on user IDs.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
import logging
from pathlib import Path
import re
from typing import Any

from ghost_audit.paths import USER_AUDIT_LOG_PATH, USER_IDENTITIES_PATH

logger = logging.getLogger(__name__)


class UnresolvedIdentityError(KeyError):
    """Raised when an email cannot be matched to any user."""
    pass


class AmbiguousIdentityError(ValueError):
    """Raised when an email matches multiple users."""
    pass


@dataclass
class ResolvedIdentity:
    user_id: str
    resolution_kind: str  # "current" | "historical"
    emails: list[str] = field(default_factory=list)
    phones: list[str] = field(default_factory=list)
    hashes: list[str] = field(default_factory=list)
    name: str = ""

    def __getitem__(self, item: str) -> Any:
        return getattr(self, item)

    def to_dict(self) -> dict[str, Any]:
        return {
            "user_id": self.user_id,
            "resolution_kind": self.resolution_kind,
            "emails": self.emails,
            "phones": self.phones,
            "hashes": self.hashes,
            "name": self.name,
        }


def match_user_id(text: str, user_id: str) -> bool:
    """
    Word-boundary matcher for user ids.
    Ensures 'user_3' does NOT match 'user_32' or 'sub_user_3'.
    """
    if not text or not user_id:
        return False
    # In regex, \w matches [a-zA-Z0-9_].
    # Using \b correctly treats '_' as a word character.
    pattern = r"\b" + re.escape(user_id) + r"\b"
    return bool(re.search(pattern, text))


class IdentityResolver:
    """
    Loads user_identities.csv and user_audit_log.csv to map emails to full user identities.
    """

    def __init__(
        self,
        identities_path: Path | str | None = None,
        audit_log_path: Path | str | None = None,
    ):
        self.identities_path = Path(identities_path) if identities_path else USER_IDENTITIES_PATH
        self.audit_log_path = Path(audit_log_path) if audit_log_path else USER_AUDIT_LOG_PATH

        # user_id -> dict of identity fields
        self.users: dict[str, dict[str, Any]] = {}
        # email -> user_id
        self.current_email_to_user: dict[str, str] = {}
        # historical email -> set of user_ids
        self.historical_email_to_users: dict[str, set[str]] = {}

        self._load_data()

    def _load_data(self) -> None:
        if self.identities_path.exists():
            with open(self.identities_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    uid = row["user_id"].strip()
                    name = row.get("name", "").strip()
                    email = row.get("email", "").strip().lower()
                    phone = row.get("phone", "").strip()
                    email_hash = row.get("email_hash", "").strip()

                    self.users[uid] = {
                        "user_id": uid,
                        "name": name,
                        "emails": {email} if email else set(),
                        "phones": {phone} if phone else set(),
                        "hashes": {email_hash} if email_hash else set(),
                        "current_email": email,
                    }
                    if email:
                        self.current_email_to_user[email] = uid

        if self.audit_log_path.exists():
            with open(self.audit_log_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    uid = row.get("user_id", "").strip()
                    if uid not in self.users:
                        self.users[uid] = {
                            "user_id": uid,
                            "name": "",
                            "emails": set(),
                            "phones": set(),
                            "hashes": set(),
                            "current_email": "",
                        }
                    user_data = self.users[uid]
                    field_name = row.get("field_name", "").strip()
                    old_v = row.get("old_value", "").strip()
                    new_v = row.get("new_value", "").strip()

                    if field_name == "email":
                        if old_v:
                            old_lower = old_v.lower()
                            user_data["emails"].add(old_lower)
                            self.historical_email_to_users.setdefault(old_lower, set()).add(uid)
                        if new_v:
                            new_lower = new_v.lower()
                            user_data["emails"].add(new_lower)
                            self.historical_email_to_users.setdefault(new_lower, set()).add(uid)
                    elif field_name == "phone":
                        if old_v:
                            user_data["phones"].add(old_v)
                        if new_v:
                            user_data["phones"].add(new_v)
                    elif field_name == "email_hash":
                        if old_v:
                            user_data["hashes"].add(old_v)
                        if new_v:
                            user_data["hashes"].add(new_v)
                    elif field_name == "name":
                        if not user_data["name"] and new_v:
                            user_data["name"] = new_v

    def resolve(self, email: str) -> ResolvedIdentity:
        """
        Resolves an email address to a ResolvedIdentity.
        Exact match only (case-insensitive).
        Raises UnresolvedIdentityError if not found.
        Raises AmbiguousIdentityError if more than one user matches.
        """
        if not email or not isinstance(email, str):
            raise UnresolvedIdentityError(f"Invalid email: {email}")

        clean_email = email.strip().lower()

        # Check current identities first
        if clean_email in self.current_email_to_user:
            uid = self.current_email_to_user[clean_email]
            u_info = self.users[uid]
            return ResolvedIdentity(
                user_id=uid,
                resolution_kind="current",
                emails=sorted(u_info["emails"]),
                phones=sorted(u_info["phones"]),
                hashes=sorted(u_info["hashes"]),
                name=u_info["name"],
            )

        # Check historical identities
        if clean_email in self.historical_email_to_users:
            uids = self.historical_email_to_users[clean_email]
            if len(uids) > 1:
                raise AmbiguousIdentityError(
                    f"Multiple users matched for historical email '{clean_email}': {sorted(uids)}"
                )
            uid = next(iter(uids))
            u_info = self.users[uid]
            return ResolvedIdentity(
                user_id=uid,
                resolution_kind="historical",
                emails=sorted(u_info["emails"]),
                phones=sorted(u_info["phones"]),
                hashes=sorted(u_info["hashes"]),
                name=u_info["name"],
            )

        # Log potential similar decoys without attributing
        similar_decoys = [
            e for e in self.current_email_to_user
            if e != clean_email and (clean_email in e or e in clean_email)
        ]
        if similar_decoys:
            logger.info("Similar-email decoy detected for '%s' (not attributed): %s", clean_email, similar_decoys)

        raise UnresolvedIdentityError(f"No user found for email '{clean_email}'")


_DEFAULT_RESOLVER: IdentityResolver | None = None


def resolve(
    email: str,
    identities_path: Path | str | None = None,
    audit_log_path: Path | str | None = None,
) -> ResolvedIdentity:
    """Convenience function to resolve an email to a ResolvedIdentity."""
    global _DEFAULT_RESOLVER
    if identities_path or audit_log_path:
        resolver = IdentityResolver(identities_path, audit_log_path)
        return resolver.resolve(email)
    if _DEFAULT_RESOLVER is None:
        _DEFAULT_RESOLVER = IdentityResolver()
    return _DEFAULT_RESOLVER.resolve(email)
