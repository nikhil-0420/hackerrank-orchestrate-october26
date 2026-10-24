# Phase 3 Step 0: State & Category Diagnosis

Comprehensive reality-based analysis of dataset collections, deletion rules, sample resource states, retention horizons, legal holds, and resource prefixes.

## (a) Distinct (system_id, collection) Pairs Across All Observations

Total distinct pairs: 102

| system_id | collection | Count | Resource Prefixes | Example Fields | Files |
|---|---|---|---|---|---|
| `account_service` | `"profile_lookup_completed"` | 10 | `"account` | `attempt`, `cache`, `dependency`, `duration_ms`, `event` | 1 files |
| `account_service` | `USER_PROFILE` | 21 | `account` | `event`, `level`, `record_type`, `resource_id`, `result` | 2 files |
| `account_service` | `connector_configurations_20260812` | 11 | `account` | `record_type`, `recorded_at`, `resource_id`, `result`, `subject_reference` | 1 files |
| `account_service` | `customer_export_manifest_20260409` | 12 | `account` | `record_type`, `recorded_at`, `resource_id`, `result`, `subject_reference` | 1 files |
| `account_service` | `customer_profiles` | 45 | `account` | `account_status`, `customer_reference`, `email`, `email_hash`, `full_name` | 27 files |
| `account_service` | `customer_profiles_failover_replica` | 4 | `account` | `account_status`, `email`, `full_name`, `phone`, `replica_of` | 1 files |
| `account_service` | `customer_profiles_primary` | 3 | `account` | `account_status`, `email`, `full_name`, `phone`, `replica_of` | 1 files |
| `account_service` | `profile_lookup_completed` | 156 | `account` | `attempt`, `cache`, `correlation_key`, `dependency`, `duration_ms` | 21 files |
| `account_service` | `profile_lookups` | 47 | `account` | `observed_at`, `profile`, `resource_id`, `status_code` | 11 files |
| `account_service` | `security_audit_ledger_20261001` | 10 | `account` | `record_type`, `recorded_at`, `resource_id`, `result`, `subject_reference` | 1 files |
| `account_service` | `user_profile` | 10 | `account` | `category`, `raw_identifier`, `result`, `state` | 1 files |
| `analytics_identity_store` | `customer_analytics_reports` | 2 | `analytics` | `email`, `email_hash`, `metrics`, `phone`, `recent_activity` | 1 files |
| `analytics_platform` | `"analytics_identity_scan"` | 2 | `"analytics` | `attempt`, `detector`, `direct_identifiers`, `event`, `instance` | 1 files |
| `analytics_platform` | `"analytics_profile_read"` | 2 | `"analytics` | `attempt`, `direct_identifiers`, `email`, `event`, `instance` | 1 files |
| `analytics_platform` | `ANALYTICS_PROFILE` | 7 | `analytics` | `event`, `level`, `record_type`, `resource_id`, `result` | 2 files |
| `analytics_platform` | `analytics_identity_scan` | 12 | `analytics` | `attempt`, `cache`, `dependency`, `detector`, `direct_identifiers` | 8 files |
| `analytics_platform` | `analytics_profile` | 3 | `analytics` | `category`, `raw_identifier`, `result`, `state` | 1 files |
| `analytics_platform` | `analytics_profile_read` | 19 | `analytics` | `attempt`, `cache`, `dependency`, `direct_identifiers`, `event` | 8 files |
| `analytics_platform` | `analytics_profile_read_completed` | 39 | `analytics` | `audience_cohort`, `email`, `event`, `level`, `lookup_key` | 10 files |
| `analytics_platform` | `connector_configurations_20260812` | 2 | `analytics` | `record_type`, `recorded_at`, `resource_id`, `result`, `subject_reference` | 1 files |
| `analytics_platform` | `contact_lookup_completed` | 1 | `analytics` | `correlation_key`, `email_opt_in`, `event`, `instance`, `level` | 1 files |
| `analytics_platform` | `customer_analytics_profiles` | 41 | `analytics` | `audience_cohort`, `customer_reference`, `email`, `email_hash`, `phone` | 10 files |
| `analytics_platform` | `customer_analytics_reports` | 143 | `analytics` | `email`, `email_hash`, `metrics`, `phone`, `recent_activity` | 21 files |
| `analytics_platform` | `customer_export_manifest_20260409` | 6 | `analytics` | `record_type`, `recorded_at`, `resource_id`, `result`, `subject_reference` | 1 files |
| `analytics_platform` | `profiles` | 48 | `analytics` | `audience_cohort`, `customer_reference`, `email`, `email_hash`, `observed_at` | 11 files |
| `attachment_preview` | `record_lookup` | 1 | `support` | `event`, `instance`, `level`, `pod`, `reason` | 1 files |
| `backup_restore_service` | `operational_record_history` | 43 | `account`, `analytics`, `audit_record`, `backup`, `data_flow`, `export`, `search`, `support` | `lookup_value`, `record_type`, `recorded_at`, `resource_id`, `result` | 1 files |
| `backup_service` | `"restore_authorization_completed"` | 1 | `"backup` | `attempt`, `decision`, `event`, `instance`, `level` | 1 files |
| `backup_service` | `BACKUP_ARCHIVE` | 2 | `backup` | `event`, `level`, `record_type`, `resource_id`, `result` | 2 files |
| `backup_service` | `backup_archive` | 2 | `backup` | `category`, `raw_identifier`, `result`, `state` | 1 files |
| `backup_service` | `backup_catalog` | 42 | `backup` | `archive_path`, `encryption`, `replica_of`, `resource_id`, `restore_allowed` | 17 files |
| `backup_service` | `backup_restore_entries` | 10 | `backup` | `archive_key`, `customer_email`, `customer_reference`, `replica_of`, `resource_id` | 9 files |
| `backup_service` | `customer_export_manifest_20260409` | 2 | `backup` | `record_type`, `recorded_at`, `resource_id`, `result`, `subject_reference` | 1 files |
| `backup_service` | `restore_authorization_completed` | 4 | `backup` | `attempt`, `cache`, `decision`, `dependency`, `event` | 3 files |
| `backup_service` | `restore_candidate_evaluated` | 8 | `backup` | `attempt`, `cache`, `correlation_key`, `deletion_block`, `dependency` | 7 files |
| `backup_service` | `restore_entries` | 17 | `backup` | `archive_key`, `customer_email`, `customer_reference`, `observed_at`, `resource_id` | 10 files |
| `backup_service` | `restore_policy_read_completed` | 15 | `backup` | `archive_key`, `archive_present`, `customer_email`, `customer_reference`, `event` | 7 files |
| `export_service` | `customer_export_jobs` | 16 | `export` | `created_at`, `download_available`, `expires_at`, `file_name`, `included_sections` | 10 files |
| `export_service` | `customer_export_manifest_20260409` | 1 | `export` | `record_type`, `recorded_at`, `resource_id`, `result`, `subject_reference` | 1 files |
| `export_service` | `customer_exports` | 8 | `export` | `customer_reference`, `object_key`, `owner_email`, `owner_phone`, `replica_of` | 8 files |
| `export_service` | `export_download_check_completed` | 8 | `export` | `attempt`, `available`, `cache`, `correlation_key`, `dependency` | 8 files |
| `export_service` | `export_metadata_read_completed` | 5 | `export` | `available`, `event`, `level`, `lookup_key`, `object_key` | 5 files |
| `export_service` | `exports` | 9 | `export` | `customer_reference`, `object_key`, `observed_at`, `owner_email`, `owner_phone` | 9 files |
| `export_service` | `user_export` | 1 | `export` | `category`, `raw_identifier`, `result`, `state` | 1 files |
| `identity_service` | `deleted_customer_references` | 18 | `tombstone` | `account_status`, `email`, `email_hash`, `name`, `phone` | 2 files |
| `integration_service` | `"connector_config_loaded"` | 1 | `"data` | `attempt`, `cache`, `enabled`, `event`, `instance` | 1 files |
| `integration_service` | `"connector_heartbeat"` | 3 | `"data` | `attempt`, `cache`, `correlation_key`, `dependency`, `enabled` | 1 files |
| `integration_service` | `DATA_FLOW` | 7 | `data_flow` | `event`, `level`, `record_type`, `resource_id`, `result` | 2 files |
| `integration_service` | `connector_config_loaded` | 4 | `data_flow` | `attempt`, `cache`, `correlation_key`, `dependency`, `enabled` | 3 files |
| `integration_service` | `connector_config_read_completed` | 34 | `data_flow` | `connector_name`, `customer_email`, `customer_reference`, `enabled`, `event` | 10 files |
| `integration_service` | `connector_configurations` | 91 | `data_flow` | `connector_name`, `destination`, `enabled`, `mode`, `replica_of` | 21 files |
| `integration_service` | `connector_configurations_20260812` | 3 | `data_flow` | `record_type`, `recorded_at`, `resource_id`, `result`, `subject_reference` | 1 files |
| `integration_service` | `connector_heartbeat` | 21 | `data_flow` | `attempt`, `cache`, `correlation_key`, `dependency`, `enabled` | 10 files |
| `integration_service` | `connector_subscriptions` | 25 | `data_flow` | `connector_name`, `customer_email`, `customer_reference`, `enabled`, `last_delivery_status` | 10 files |
| `integration_service` | `connectors` | 35 | `data_flow` | `connector_name`, `customer_email`, `customer_reference`, `enabled`, `last_delivery_status` | 11 files |
| `integration_service` | `customer_export_manifest_20260409` | 4 | `data_flow` | `record_type`, `recorded_at`, `resource_id`, `result`, `subject_reference` | 1 files |
| `integration_service` | `data_flow` | 4 | `data_flow` | `category`, `raw_identifier`, `result`, `state` | 1 files |
| `legal_service` | `customer_export_manifest_20260409` | 1 | `legal_hold` | `record_type`, `recorded_at`, `resource_id`, `result`, `subject_reference` | 1 files |
| `legal_service` | `retained_order_loaded` | 1 | `legal_hold` | `access`, `attempt`, `event`, `instance`, `level` | 1 files |
| `legal_service` | `retained_order_records` | 10 | `legal_hold` | `order_reference`, `replica_of`, `resource_id`, `retained_until`, `retention_reason` | 5 files |
| `privacy_treatment_service` | `operational_record_history` | 42 | `account`, `analytics`, `audit_record`, `backup`, `data_flow`, `export`, `search`, `support` | `lookup_value`, `record_type`, `recorded_at`, `resource_id`, `result` | 1 files |
| `profile_service` | `"profile_lookup_completed"` | 300 | `"account` | `correlation_key`, `duration_ms`, `event`, `http_status`, `instance` | 1 files |
| `search_service` | `"customer_directory_v3"` | 8 | `"search` | `attempt`, `correlation_key`, `dependency`, `event`, `index` | 1 files |
| `search_service` | `SEARCH_INDEX_ENTRY` | 11 | `search` | `event`, `level`, `record_type`, `resource_id`, `result` | 2 files |
| `search_service` | `connector_configurations_20260812` | 8 | `search` | `record_type`, `recorded_at`, `resource_id`, `result`, `subject_reference` | 1 files |
| `search_service` | `customer_directory_v3` | 115 | `search` | `attempt`, `cache`, `correlation_key`, `dependency`, `email` | 20 files |
| `search_service` | `customer_export_manifest_20260409` | 7 | `search` | `record_type`, `recorded_at`, `resource_id`, `result`, `subject_reference` | 1 files |
| `search_service` | `customer_search_documents` | 248 | `search` | `customer_reference`, `display_name`, `document`, `email`, `email_hash` | 31 files |
| `search_service` | `index_queries` | 58 | `search` | `hits`, `observed_at`, `query`, `resource_id` | 11 files |
| `search_service` | `search_documents_primary` | 3 | `search` | `display_name`, `email`, `indexed_at`, `replica_of`, `resource_id` | 1 files |
| `search_service` | `search_index_entry` | 6 | `search` | `category`, `raw_identifier`, `result`, `state` | 1 files |
| `security_service` | `"audit_record_read_completed"` | 10 | `"audit` | `attempt`, `cache`, `correlation_key`, `dependency`, `event` | 1 files |
| `security_service` | `SECURITY_AUDIT_LOG` | 20 | `audit_record` | `event`, `level`, `record_type`, `resource_id`, `result` | 2 files |
| `security_service` | `audit_record_read_completed` | 137 | `audit_record` | `attempt`, `cache`, `correlation_key`, `dependency`, `event` | 20 files |
| `security_service` | `audit_records` | 37 | `audit_record` | `event_code`, `observed_at`, `resource_id`, `retention_until`, `subject_reference` | 11 files |
| `security_service` | `connector_configurations_20260812` | 10 | `audit_record` | `record_type`, `recorded_at`, `resource_id`, `result`, `subject_reference` | 1 files |
| `security_service` | `customer_export_manifest_20260409` | 10 | `audit_record` | `record_type`, `recorded_at`, `resource_id`, `result`, `subject_reference` | 1 files |
| `security_service` | `security_audit_events` | 358 | `audit_record` | `actor_type`, `event_name`, `integrity_seal`, `replica_of`, `resource_id` | 23 files |
| `security_service` | `security_audit_ledger_20261001` | 10 | `audit_record` | `record_type`, `recorded_at`, `resource_id`, `result`, `subject_reference` | 1 files |
| `security_service` | `security_audit_log` | 10 | `audit_record` | `category`, `raw_identifier`, `result`, `state` | 1 files |
| `security_service` | `security_audit_records` | 30 | `audit_record` | `event_code`, `replica_of`, `resource_id`, `retention_until`, `subject_reference` | 10 files |
| `support_platform` | `"attachment_pii_scan"` | 1 | `"support` | `attempt`, `cache`, `detector`, `event`, `file` | 1 files |
| `support_platform` | `"message_pii_scan"` | 4 | `"support` | `attempt`, `cache`, `detector`, `event`, `instance` | 1 files |
| `support_platform` | `"message_read"` | 1 | `"support` | `attempt`, `cache`, `event`, `instance`, `level` | 1 files |
| `support_platform` | `SUPPORT_MESSAGE` | 7 | `support` | `event`, `level`, `record_type`, `resource_id`, `result` | 2 files |
| `support_platform` | `attachment_pii_scan` | 6 | `support` | `attempt`, `cache`, `detector`, `event`, `file` | 6 files |
| `support_platform` | `connector_configurations_20260812` | 5 | `support` | `record_type`, `recorded_at`, `resource_id`, `result`, `subject_reference` | 1 files |
| `support_platform` | `customer_export_manifest_20260409` | 3 | `support` | `record_type`, `recorded_at`, `resource_id`, `result`, `subject_reference` | 1 files |
| `support_platform` | `message_pii_scan` | 26 | `support` | `attempt`, `cache`, `dependency`, `detector`, `event` | 10 files |
| `support_platform` | `message_read` | 4 | `support` | `attempt`, `cache`, `dependency`, `event`, `instance` | 3 files |
| `support_platform` | `support_attachment` | 1 | `support` | `category`, `raw_identifier`, `result`, `state` | 1 files |
| `support_platform` | `support_conversations` | 102 | `support` | `channel`, `message_text`, `replica_of`, `resource_id`, `row_updated_at` | 21 files |
| `support_platform` | `support_message` | 4 | `support` | `category`, `raw_identifier`, `result`, `state` | 1 files |
| `support_platform` | `support_records` | 33 | `support` | `customer_reference`, `message_excerpt`, `replica_of`, `requester_email`, `requester_name` | 10 files |
| `support_platform` | `support_ticket_read_completed` | 34 | `support` | `customer_reference`, `event`, `level`, `lookup_key`, `requester_email` | 10 files |
| `support_platform` | `ticket_attachments` | 22 | `support` | `file_name`, `replica_of`, `resource_id`, `row_updated_at`, `storage_class` | 13 files |
| `support_platform` | `tickets` | 45 | `support` | `customer_reference`, `message_excerpt`, `observed_at`, `requester_email`, `requester_name` | 11 files |
| `support_replica` | `contact_query_completed` | 1 | `support` | `event`, `instance`, `latency_ms`, `level`, `lookup_key` | 1 files |
| `support_replica` | `deletion_marker_check` | 1 | `support` | `event`, `instance`, `last_write`, `latency_ms`, `level` | 1 files |
| `support_replica` | `record_lookup` | 1 | `support` | `event`, `instance`, `latency_ms`, `level`, `lookup_key` | 1 files |
| `support_storage_service` | `operational_record_history` | 39 | `account`, `analytics`, `audit_record`, `backup`, `data_flow`, `search`, `support` | `lookup_value`, `record_type`, `recorded_at`, `resource_id`, `result` | 1 files |
| `user_export_store` | `customer_export_jobs` | 2 | `export` | `created_at`, `download_available`, `expires_at`, `file_name`, `included_sections` | 1 files |

## (b) 15 Deletion Rules from `dataset/deletion_rules.csv`

| Rule ID | Data Category | Required Action | Condition | Target Treatment |
|---|---|---|---|---|
| `rule_01` | `USER_PROFILE` | **DELETE** | Always | DELETE |
| `rule_02` | `SECONDARY_IDENTIFIER` | **DELETE** | Always | DELETE |
| `rule_03` | `SEARCH_INDEX_ENTRY` | **DELETE** | Always | DELETE |
| `rule_04` | `CACHE_ENTRY` | **DELETE** | Always | DELETE |
| `rule_05` | `SUPPORT_MESSAGE` | **REDACT** | Conversation contains shared customer, agent, or order context that must be retained | REDACT |
| `rule_06` | `SUPPORT_ATTACHMENT` | **DELETE** | Attachment belongs only to the deletion subject | DELETE |
| `rule_07` | `ANALYTICS_PROFILE` | **ANONYMIZE** | Record is still attributable to a user | ANONYMIZE |
| `rule_08` | `PRODUCT_TELEMETRY` | **ANONYMIZE** | Record is still attributable to a user | ANONYMIZE |
| `rule_09` | `USER_EXPORT` | **DELETE** | Always | DELETE |
| `rule_10` | `MARKETING_PROFILE` | **DELETE** | Always | DELETE |
| `rule_11` | `EMAIL_DELIVERY_LOG` | **REDACT** | Log contains a user email address | REDACT |
| `rule_12` | `SECURITY_AUDIT_LOG` | **RETAIN** | Record is within the supplied retention period | RETAIN |
| `rule_13` | `LEGAL_HOLD_RECORD` | **RETAIN** | A supplied legal hold is active | RETAIN |
| `rule_14` | `BACKUP_ARCHIVE` | **RETAIN** | Restore access can be blocked | RETAIN |
| `rule_15` | `ACCOUNT_TOMBSTONE` | **REDACT** | Account is deleted and only a stable internal user_id is needed to preserve references to retained records | REDACT |

## (c) Sample Resource Analysis (Labels vs Observed State & Activity)

Total sample labeled resources analyzed: 193

| Case ID | Resource ID | System | Role | Shape Category | Activity Event Types | Observed State at audit_at | Latest File |
|---|---|---|---|---|---|---|---|
| `case_01` | `account_001` | `account_service` | `verification` | `USER_PROFILE` | DELETE_RECORD | `ABSENT_OR_UNOBSERVED` | `none` |
| `case_02` | `account_002` | `account_service` | `verification` | `USER_PROFILE` | DELETE_RECORD | `ABSENT_OR_UNOBSERVED` | `none` |
| `case_03` | `account_7566` | `account_service` | `verification` | `USER_PROFILE` | DELETE_RECORD | `PRESENT` | `evidence_94` |
| `case_03` | `analytics_9406` | `analytics_platform` | `verification` | `ANALYTICS_PROFILE` | ANONYMIZE_RECORD | `PRESENT` | `evidence_94` |
| `case_03` | `audit_record_2016` | `security_service` | `verification` | `SECURITY_AUDIT_LOG` | *(none)* | `PRESENT` | `evidence_94` |
| `case_04` | `account_004` | `account_service` | `verification` | `USER_PROFILE` | *(none)* | `ABSENT_OR_UNOBSERVED` | `none` |
| `case_04` | `analytics_901` | `analytics_platform` | `verification` | `ANALYTICS_PROFILE` | ANONYMIZE_RECORD | `PRESENT` | `evidence_56` |
| `case_05` | `account_005` | `account_service` | `verification` | `USER_PROFILE` | DELETE_RECORD, SYNC_RECORD | `PRESENT` | `evidence_54` |
| `case_05` | `account_005` | `account_service` | `finding` | `USER_PROFILE` | DELETE_RECORD, SYNC_RECORD | `PRESENT` | `evidence_54` |
| `case_05` | `account_005` | `account_service` | `remediation` | `USER_PROFILE` | DELETE_RECORD, SYNC_RECORD | `PRESENT` | `evidence_54` |
| `case_06` | `account_006` | `account_service` | `verification` | `USER_PROFILE` | DELETE_RECORD | `ABSENT_OR_UNOBSERVED` | `none` |
| `case_06` | `search_001` | `search_service` | `remediation` | `SEARCH_INDEX_ENTRY` | DELETE_RECORD | `PRESENT` | `evidence_57` |
| `case_06` | `search_001` | `search_service` | `verification` | `SEARCH_INDEX_ENTRY` | DELETE_RECORD | `PRESENT` | `evidence_57` |
| `case_06` | `search_001` | `search_service` | `finding` | `SEARCH_INDEX_ENTRY` | DELETE_RECORD | `PRESENT` | `evidence_57` |
| `case_07` | `account_007` | `account_service` | `verification` | `USER_PROFILE` | DELETE_RECORD | `ABSENT_OR_UNOBSERVED` | `none` |
| `case_07` | `support_001` | `support_platform` | `finding` | `SUPPORT_MESSAGE` | *(none)* | `ABSENT_OR_UNOBSERVED` | `none` |
| `case_07` | `support_001` | `support_platform` | `verification` | `SUPPORT_MESSAGE` | *(none)* | `ABSENT_OR_UNOBSERVED` | `none` |
| `case_07` | `support_001` | `support_platform` | `remediation` | `SUPPORT_MESSAGE` | *(none)* | `ABSENT_OR_UNOBSERVED` | `none` |
| `case_08` | `account_008` | `account_service` | `verification` | `USER_PROFILE` | DELETE_RECORD | `ABSENT_OR_UNOBSERVED` | `none` |
| `case_08` | `export_001` | `export_service` | `remediation` | `USER_EXPORT` | DELETE_RECORD | `PRESENT` | `evidence_59` |
| `case_08` | `export_001` | `export_service` | `verification` | `USER_EXPORT` | DELETE_RECORD | `PRESENT` | `evidence_59` |
| `case_08` | `export_001` | `export_service` | `finding` | `USER_EXPORT` | DELETE_RECORD | `PRESENT` | `evidence_59` |
| `case_09` | `account_3960` | `account_service` | `verification` | `USER_PROFILE` | DELETE_RECORD | `PRESENT` | `evidence_06` |
| `case_09` | `audit_record_4902` | `security_service` | `verification` | `SECURITY_AUDIT_LOG` | *(none)* | `PRESENT` | `evidence_06` |
| `case_09` | `backup_4978` | `backup_service` | `finding` | `BACKUP_ARCHIVE` | CHECK_RESTORE_ACCESS | `PRESENT` | `evidence_06` |
| `case_09` | `backup_4978` | `backup_service` | `remediation` | `BACKUP_ARCHIVE` | CHECK_RESTORE_ACCESS | `PRESENT` | `evidence_06` |
| `case_09` | `backup_4978` | `backup_service` | `verification` | `BACKUP_ARCHIVE` | CHECK_RESTORE_ACCESS | `PRESENT` | `evidence_06` |
| `case_10` | `account_010` | `account_service` | `verification` | `USER_PROFILE` | DELETE_RECORD | `ABSENT_OR_UNOBSERVED` | `none` |
| `case_10` | `support_002` | `support_platform` | `finding` | `SUPPORT_MESSAGE` | DELETE_RECORD | `PRESENT` | `evidence_61` |
| `case_10` | `support_002` | `support_platform` | `remediation` | `SUPPORT_MESSAGE` | DELETE_RECORD | `PRESENT` | `evidence_61` |
| `case_10` | `support_002` | `support_platform` | `verification` | `SUPPORT_MESSAGE` | DELETE_RECORD | `PRESENT` | `evidence_61` |
| `case_11` | `account_4248` | `account_service` | `verification` | `USER_PROFILE` | DELETE_RECORD | `PRESENT` | `evidence_03` |
| `case_11` | `analytics_2034` | `analytics_platform` | `finding` | `ANALYTICS_PROFILE` | ANONYMIZE_RECORD | `PRESENT` | `evidence_03` |
| `case_11` | `analytics_2034` | `analytics_platform` | `remediation` | `ANALYTICS_PROFILE` | ANONYMIZE_RECORD | `PRESENT` | `evidence_03` |
| `case_11` | `analytics_2034` | `analytics_platform` | `verification` | `ANALYTICS_PROFILE` | ANONYMIZE_RECORD | `PRESENT` | `evidence_03` |
| `case_11` | `audit_record_9394` | `security_service` | `verification` | `SECURITY_AUDIT_LOG` | *(none)* | `PRESENT` | `evidence_03` |
| `case_11` | `data_flow_9522` | `integration_service` | `remediation` | `DATA_FLOW` | CHECK_DATA_FLOW | `PRESENT` | `evidence_03` |
| `case_11` | `data_flow_9522` | `integration_service` | `verification` | `DATA_FLOW` | CHECK_DATA_FLOW | `PRESENT` | `evidence_03` |
| `case_11` | `data_flow_9522` | `integration_service` | `finding` | `DATA_FLOW` | CHECK_DATA_FLOW | `PRESENT` | `evidence_03` |
| `case_11` | `search_052` | `search_service` | `finding` | `SEARCH_INDEX_ENTRY` | DELETE_RECORD | `PRESENT` | `evidence_03` |
| ... | ... | ... | ... | ... | ... | ... | *(and 153 more sample resources)* |

## (d) `retention_until` Values vs Case `audit_at`

Total retention checks on sample cited resources: 6

| Case ID | Resource ID | audit_at | retention_until | Active at audit_at? | Remaining Time | File |
|---|---|---|---|---|---|---|
| `case_03` | `audit_record_2016` | `2026-09-26T11:00:00Z` | `2034-09-30T23:59:59Z` | **True** | +8.0 years | `evidence_94` |
| `case_21` | `audit_record_3737` | `2026-09-15T12:00:00Z` | `2034-09-30T23:59:59Z` | **True** | +8.0 years | `evidence_92` |
| `case_25` | `audit_record_451` | `2026-09-15T12:00:00Z` | `2031-12-31T23:59:59Z` | **True** | +5.3 years | `evidence_92` |
| `case_26` | `audit_record_5416` | `2026-09-15T12:00:00Z` | `2032-06-30T23:59:59Z` | **True** | +5.8 years | `evidence_92` |
| `case_27` | `audit_record_3830` | `2026-09-15T12:00:00Z` | `2034-09-30T23:59:59Z` | **True** | +8.0 years | `evidence_92` |
| `case_28` | `audit_record_9265` | `2026-09-15T12:00:00Z` | `2033-12-31T23:59:59Z` | **True** | +7.3 years | `evidence_92` |

## (e) Legal Hold Records Analysis

- **Files containing legal hold records (7)**: evidence_21, evidence_24, evidence_36, evidence_40, evidence_43, evidence_45, evidence_47
- **Total legal observations**: 12
- **Total activity rows involving legal_service**: 10

### Example Legal Hold Observations
```json
{
  "resource_id": "legal_hold_4961",
  "system_id": "legal_service",
  "collection": "retained_order_loaded",
  "file_id": "evidence_21",
  "state": {
    "instance": "legal-3",
    "pod": "legal-d9a5",
    "region": "eu-west-1",
    "subject_ref": "user_218",
    "attempt": "1",
    "level": "INFO",
    "event": "retained_order_loaded",
    "pool": "legal_service_primary",
    "wait_ms": "6",
    "resource_id": "legal_hold_4961",
    "reason": "payment_dispute_and_tax_record",
    "access": "allowed",
    "trace_id": "tr-2637487"
  }
}
{
  "resource_id": "legal_hold_8017",
  "system_id": "legal_service",
  "collection": "retained_order_records",
  "file_id": "evidence_24",
  "state": {
    "resource_id": "legal_hold_8017",
    "subject_reference": "user_259",
    "order_reference": "ORD-20268017",
    "retention_reason": "payment_dispute_and_tax_record",
    "retained_until": "2033-12-31T23:59:59Z",
    "replica_of": "customer_data_primary",
    "table_name": "customer_data_primary",
    "row_updated_at": "2026-06-13T11:00:00Z"
  }
}
{
  "resource_id": "legal_hold_8017",
  "system_id": "legal_service",
  "collection": "retained_order_records",
  "file_id": "evidence_24",
  "state": {
    "resource_id": "legal_hold_8017",
    "subject_reference": "user_259",
    "order_reference": "ORD-20268017",
    "retention_reason": "payment_dispute_and_tax_record",
    "retained_until": "2033-12-31T23:59:59Z",
    "replica_of": "customer_data_read_replica",
    "table_name": "customer_data_read_replica",
    "row_updated_at": "2026-06-13T11:00:00Z"
  }
}
{
  "resource_id": "legal_hold_8049",
  "system_id": "legal_service",
  "collection": "customer_export_manifest_20260409",
  "file_id": "evidence_36",
  "state": {
    "recorded_at": "2026-04-09T12:00:00Z",
    "system": "legal_service",
    "resource_id": "legal_hold_8049",
    "record_type": "LEGAL_HOLD_RECORD",
    "result": "FOUND",
    "subject_reference": "user_388"
  }
}
```

### All 10 `legal_service` Activity Rows
| activity_id | event_time | event_type | source -> target | resource_id | reported_result | details |
|---|---|---|---|---|---|---|
| `activity_264` | `2026-01-23T06:31:34Z` | `RETAIN_RECORD` | `deletion_worker` -> `legal_service` | `legal_hold_4887` | `SUCCESS` | Policy action completed for legal_hold_4887. |
| `activity_336` | `2026-01-29T06:31:28Z` | `RETAIN_RECORD` | `deletion_worker` -> `legal_service` | `legal_hold_2227` | `SUCCESS` | Policy action completed for legal_hold_2227. |
| `activity_410` | `2026-02-03T09:31:01Z` | `RETAIN_RECORD` | `deletion_worker` -> `legal_service` | `legal_hold_4743` | `SUCCESS` | Policy action completed for legal_hold_4743. |
| `activity_478` | `2026-02-08T11:31:35Z` | `RETAIN_RECORD` | `deletion_worker` -> `legal_service` | `legal_hold_5622` | `SUCCESS` | Policy action completed for legal_hold_5622. |
| `activity_801` | `2026-03-02T07:31:13Z` | `RETAIN_RECORD` | `deletion_worker` -> `legal_service` | `legal_hold_438` | `SUCCESS` | Policy action completed for legal_hold_438. |
| `activity_1120` | `2026-03-24T11:31:08Z` | `RETAIN_RECORD` | `deletion_worker` -> `legal_service` | `legal_hold_8049` | `SUCCESS` | Policy action completed for legal_hold_8049. |
| `activity_1902` | `2026-05-15T07:31:05Z` | `RETAIN_RECORD` | `deletion_worker` -> `legal_service` | `legal_hold_1745` | `SUCCESS` | Policy action completed for legal_hold_1745. |
| `activity_1942` | `2026-05-17T10:31:45Z` | `RETAIN_RECORD` | `deletion_worker` -> `legal_service` | `legal_hold_8017` | `SUCCESS` | Policy action completed for legal_hold_8017. |
| `activity_2264` | `2026-06-08T07:31:54Z` | `RETAIN_RECORD` | `deletion_worker` -> `legal_service` | `legal_hold_4961` | `SUCCESS` | Policy action completed for legal_hold_4961. |
| `activity_3138` | `2026-08-07T05:31:15Z` | `RETAIN_RECORD` | `deletion_worker` -> `legal_service` | `legal_hold_668` | `SUCCESS` | Policy action completed for legal_hold_668. |

## (f) Resource Prefixes in Observations vs Samples

- **All Observation Prefixes (17)**: `"account`, `"analytics`, `"audit`, `"backup`, `"data`, `"search`, `"support`, `account`, `analytics`, `audit_record`, `backup`, `data_flow`, `export`, `legal_hold`, `search`, `support`, `tombstone`
- **Sample Ground Truth Prefixes (9)**: `account`, `analytics`, `audit_record`, `backup`, `data_flow`, `export`, `search`, `support`, `tombstone`
- **Prefixes in Observations but NEVER in Samples (8)**: `"account`, `"analytics`, `"audit`, `"backup`, `"data`, `"search`, `"support`, `legal_hold`
