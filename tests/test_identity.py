"""
Unit tests for code/ghost_audit/identity.py.
Uses ONLY hand-made synthetic data (no dataset files).
"""

from pathlib import Path
import tempfile
import unittest

from ghost_audit.identity import (
    AmbiguousIdentityError,
    IdentityResolver,
    UnresolvedIdentityError,
    match_user_id,
    resolve,
)


class TestIdentityResolution(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.temp_dir = Path(self.td.name)

        self.identities_csv = self.temp_dir / "user_identities.csv"
        self.audit_log_csv = self.temp_dir / "user_audit_log.csv"

        # Synthetic user identities
        self.identities_csv.write_text(
            "user_id,name,email,phone,email_hash,updated_at\n"
            "user_1,Alice Smith,alice@example.com,+1-555-0101,hash_alice_curr,2026-05-01T00:00:00Z\n"
            "user_2,Bob Jones,bob@example.com,+1-555-0102,hash_bob_curr,2026-05-01T00:00:00Z\n"
            "user_3,Charlie Brown,charlie@example.com,+1-555-0103,hash_charlie_curr,2026-05-01T00:00:00Z\n",
            encoding="utf-8",
        )

        # Synthetic audit log (historical changes)
        self.audit_log_csv.write_text(
            "audit_id,user_id,event_time,field_name,old_value,new_value\n"
            "a1,user_1,2025-01-01T00:00:00Z,email,alice.old@example.com,alice@example.com\n"
            "a2,user_1,2025-01-01T00:00:00Z,phone,+1-555-0001,+1-555-0101\n"
            "a3,user_1,2025-01-01T00:00:00Z,email_hash,hash_alice_old,hash_alice_curr\n"
            "a4,user_2,2025-02-01T00:00:00Z,email,shared.old@example.com,bob@example.com\n"
            "a5,user_3,2025-03-01T00:00:00Z,email,shared.old@example.com,charlie@example.com\n",
            encoding="utf-8",
        )

        self.resolver = IdentityResolver(self.identities_csv, self.audit_log_csv)

    def tearDown(self):
        self.td.cleanup()

    def test_current_email_resolution(self):
        res = self.resolver.resolve("ALICE@EXAMPLE.COM")
        self.assertEqual(res.user_id, "user_1")
        self.assertEqual(res.resolution_kind, "current")
        self.assertEqual(res.name, "Alice Smith")
        self.assertIn("alice@example.com", res.emails)
        self.assertIn("alice.old@example.com", res.emails)
        self.assertIn("+1-555-0101", res.phones)
        self.assertIn("+1-555-0001", res.phones)
        self.assertIn("hash_alice_curr", res.hashes)
        self.assertIn("hash_alice_old", res.hashes)

    def test_historical_email_resolution(self):
        res = self.resolver.resolve("alice.old@example.com")
        self.assertEqual(res.user_id, "user_1")
        self.assertEqual(res.resolution_kind, "historical")
        self.assertEqual(res.name, "Alice Smith")
        self.assertIn("alice@example.com", res.emails)

    def test_unresolved_email_error(self):
        with self.assertRaises(UnresolvedIdentityError):
            self.resolver.resolve("nonexistent@example.com")

    def test_ambiguous_historical_email_error(self):
        # shared.old@example.com was linked to both user_2 and user_3 in audit log
        with self.assertRaises(AmbiguousIdentityError):
            self.resolver.resolve("shared.old@example.com")

    def test_no_fuzzy_matching(self):
        # Similar typo email should NOT match
        with self.assertRaises(UnresolvedIdentityError):
            self.resolver.resolve("alicee@example.com")

    def test_word_boundary_user_id_matching(self):
        # Exact word match
        self.assertTrue(match_user_id("user_3", "user_3"))
        self.assertTrue(match_user_id("customer user_3 deleted", "user_3"))
        self.assertTrue(match_user_id("user_ref: 'user_3'", "user_3"))

        # Must NOT match prefixes, suffixes, or larger numbers
        self.assertFalse(match_user_id("user_32", "user_3"))
        self.assertFalse(match_user_id("user_300", "user_3"))
        self.assertFalse(match_user_id("sub_user_3", "user_3"))
        self.assertFalse(match_user_id("myuser_3", "user_3"))


if __name__ == "__main__":
    unittest.main()
