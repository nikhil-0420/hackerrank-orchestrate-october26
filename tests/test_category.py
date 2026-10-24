"""
Unit tests for ghost_audit/category.py.
Validates classification of all distinct (system_id, collection) pairs from reality.
"""

import unittest

from ghost_audit.category import VALID_DATA_CATEGORIES, classify_category


class TestCategoryClassification(unittest.TestCase):
    def test_account_service_profiles(self):
        cat = classify_category("account_service", "customer_profiles")
        self.assertEqual(cat, "USER_PROFILE")

        cat2 = classify_category("account_service", "profile_lookup_completed")
        self.assertEqual(cat2, "USER_PROFILE")

        cat3 = classify_category("account_service", "secondary_emails")
        self.assertEqual(cat3, "SECONDARY_IDENTIFIER")

    def test_search_service(self):
        cat = classify_category("search_service", "customer_search_documents")
        self.assertEqual(cat, "SEARCH_INDEX_ENTRY")

        cat2 = classify_category("search_service", "customer_directory_v3")
        self.assertEqual(cat2, "SEARCH_INDEX_ENTRY")

    def test_support_platform_message_vs_attachment(self):
        cat_msg = classify_category("support_platform", "support_conversations")
        self.assertEqual(cat_msg, "SUPPORT_MESSAGE")

        cat_att = classify_category("support_platform", "attachment_pii_scan", state={"file": "receipt.pdf"})
        self.assertEqual(cat_att, "SUPPORT_ATTACHMENT")

        cat_att2 = classify_category("support_platform", "support_conversations", state={"attachment_url": "s3://..."})
        self.assertEqual(cat_att2, "SUPPORT_ATTACHMENT")

    def test_analytics_platform_profile_vs_telemetry(self):
        cat_prof = classify_category("analytics_platform", "customer_analytics_profiles")
        self.assertEqual(cat_prof, "ANALYTICS_PROFILE")

        cat_tel = classify_category("analytics_platform", "client_telemetry_events")
        self.assertEqual(cat_tel, "PRODUCT_TELEMETRY")

    def test_export_service(self):
        cat = classify_category("export_service", "customer_export_jobs")
        self.assertEqual(cat, "USER_EXPORT")

    def test_backup_service(self):
        cat = classify_category("backup_service", "backup_catalog")
        self.assertEqual(cat, "BACKUP_ARCHIVE")

        cat2 = classify_category("backup_service", "restore_authorization_completed")
        self.assertEqual(cat2, "BACKUP_ARCHIVE")

    def test_security_service(self):
        cat = classify_category("security_service", "security_audit_events")
        self.assertEqual(cat, "SECURITY_AUDIT_LOG")

        cat2 = classify_category("security_service", "audit_record_read_completed")
        self.assertEqual(cat2, "SECURITY_AUDIT_LOG")

    def test_legal_service(self):
        cat = classify_category("legal_service", "retained_order_records")
        self.assertEqual(cat, "LEGAL_HOLD_RECORD")

    def test_identity_service_tombstone(self):
        cat = classify_category("identity_service", "deleted_customer_references")
        self.assertEqual(cat, "ACCOUNT_TOMBSTONE")

    def test_integration_service_flow(self):
        cat = classify_category("integration_service", "connector_configurations")
        self.assertEqual(cat, "DATA_FLOW")

    def test_explicit_record_type_in_state_wins(self):
        cat = classify_category("unknown_service", "raw_records", state={"record_type": "CACHE_ENTRY"})
        self.assertEqual(cat, "CACHE_ENTRY")


if __name__ == "__main__":
    unittest.main()
