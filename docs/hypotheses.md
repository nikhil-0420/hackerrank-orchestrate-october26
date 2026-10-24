# Hypotheses & Investigation Notes

This document tracks hypotheses, investigation paths, and validation outcomes for auditing deletion requests in the Ghost Data Still Exists challenge.

## Core Hypotheses

1. **Authorization Verification**:
   - Some deletion requests may only request account access, data export, or marketing opt-outs rather than deletion, requiring a `NOT_APPLICABLE` classification.

2. **Identity Resolution & Historical Aliases**:
   - Users may have changed emails, phone numbers, or user handles over time, as recorded in `user_audit_log.csv`. Failure to trace previous identifiers could lead to false-negative findings for remaining ghost data.

3. **Replication Drift & Secondary Stores**:
   - Workflows reporting `COMPLETE` may only delete from primary stores, leaving active records in regional replicas, reporting databases, logs, search indexes, or support attachments.

4. **Recreation via Sync & Restore**:
   - Active synchronization pipelines or pending backup restores may actively resurrect deleted personal data, necessitating proactive `DISABLE_DATA_FLOW` and `BLOCK_RESTORE` remediation.

## Phase 1 Evidence Ingestion Diagnostics

### Distinct Log Line Grammars (7 Identified, 0 Unparsed Across 2,211 Lines)

1. **APPLICATION_TRACE_BRACKETED**:
   - *Sample* (`application_trace_ap_northeast_20260730.log:1`):
     ```text
     2026-07-28T05:51:16Z [DEBUG] [log_router] [collector-9] export_started: instance="collector-9" sources="platform_services" expected_source_events="87"
     ```
   - *Trace format*: `[tr-XXXXXXX]` bracketed token or `trace_id=...` in key-values.

2. **CLOUD_RUNTIME_EXPORT** (Lambda / CloudWatch structured export):
   - *Sample* (`cloud_runtime_export_af_south_20260930.log:1`):
     ```text
     2026-09-30T11:51:01Z requestId=collector-4 level=DEBUG function=log_router message="instance=\"collector-4\" event=\"export_started\" sources=\"platform_services\" expected_source_events=\"300\""
     ```
   - *Trace format*: `requestId=tr-XXXXXXX` where message contains escaped key-values.

3. **RECORD_LOOKUP_LOG**:
   - *Sample* (`notification_delivery_20260315.log:1`):
     ```text
     2026-03-15T07:00:00Z INFO service=downstream_delivery_service event=record_lookup seq=1 system="account_service" resource_id="account_022" record_type="USER_PROFILE" result="NOT_FOUND" subject_reference="zofia-novak@gmail.com"
     ```
   - *Trace format*: Direct atomic line with `system`, `resource_id`, `result`, and `subject_reference`.

4. **OPERATIONS_STREAM_PIPED**:
   - *Sample* (`operations_stream_eu_central_20260705.log:1`):
     ```text
     2026-07-03T07:51:30Z | DEBUG | log_router | collector-5 | export_started | instance="collector-5" sources="platform_services" expected_source_events="122"
     ```
   - *Trace format*: Delimited pipe fields `time | level | service | trace_id/instance | event | key=value...`.

5. **STANDARD_KEY_VALUE**:
   - *Sample* (`resource_lookup_trace_20260218_083911.log:1`):
     ```text
     2026-02-18T05:47:12Z level=INFO service=readback_collector event=export_started target_count=26 mode=point_in_time
     ```
   - *Trace format*: ISO timestamp followed by space-separated `key=value` or `key="value"`, carrying `trace_id=tr-...`.

6. **TIMESTAMP_PREFIXED_JSON**:
   - *Sample* (`structured_service_events_ca_central_20260419.log:1`):
     ```text
     2026-04-19T06:51:11Z {"severity":"DEBUG","logger":"log_router","service":"log_router","instance":"collector-2","event":"export_started","sources":"platform_services","expected_source_events":"130"}
     ```
   - *Trace format*: ISO timestamp followed by JSON object containing trace and identifier fields.

7. **SYSLOG_RFC5424**:
   - *Sample* (`syslog_archive_ap_southeast_20260325.log:1`):
     ```text
     2026-03-25T08:51:13Z <15>1 node-8 log_router collector-7 - - level=DEBUG instance="collector-7" event="export_started" sources="platform_services" expected_source_events="109"
     ```
   - *Trace format*: RFC5424 header `<PRI>VER HOST APP PROCID MSGID SD` where `PROCID` is trace ID (`tr-XXXXXXX`) followed by key-values.

### Distinct SQL Table Schemas (18 Tables Across 24 SQL Files)

1. `snapshot_scope`:
   ```sql
   CREATE TABLE snapshot_scope (origin_system TEXT PRIMARY KEY, captured_at TEXT NOT NULL)
   ```
2. `customer_data_primary`:
   ```sql
   CREATE TABLE customer_data_primary (resource_id TEXT PRIMARY KEY, origin_system TEXT NOT NULL, collection_name TEXT NOT NULL, record_json TEXT NOT NULL CHECK (json_valid(record_json)), updated_at TEXT NOT NULL)
   ```
3. `customer_data_read_replica`:
   ```sql
   CREATE TABLE customer_data_read_replica (resource_id TEXT PRIMARY KEY, origin_system TEXT NOT NULL, collection_name TEXT NOT NULL, record_json TEXT NOT NULL CHECK (json_valid(record_json)), updated_at TEXT NOT NULL)
   ```
4. `customer_data_failover_replica`:
   ```sql
   CREATE TABLE customer_data_failover_replica (resource_id TEXT PRIMARY KEY, origin_system TEXT NOT NULL, collection_name TEXT NOT NULL, record_json TEXT NOT NULL CHECK (json_valid(record_json)), updated_at TEXT NOT NULL)
   ```
5. `customer_data_replica_ap_south`:
   ```sql
   CREATE TABLE customer_data_replica_ap_south (resource_id TEXT PRIMARY KEY, origin_system TEXT NOT NULL, collection_name TEXT NOT NULL, record_json TEXT NOT NULL CHECK (json_valid(record_json)), updated_at TEXT NOT NULL)
   ```
6. `customer_data_replica_eu_west`:
   ```sql
   CREATE TABLE customer_data_replica_eu_west (resource_id TEXT PRIMARY KEY, origin_system TEXT NOT NULL, collection_name TEXT NOT NULL, record_json TEXT NOT NULL CHECK (json_valid(record_json)), updated_at TEXT NOT NULL)
   ```
7. `customer_data_reporting_replica`:
   ```sql
   CREATE TABLE customer_data_reporting_replica (resource_id TEXT PRIMARY KEY, origin_system TEXT NOT NULL, collection_name TEXT NOT NULL, record_json TEXT NOT NULL CHECK (json_valid(record_json)), updated_at TEXT NOT NULL)
   ```
8. `customer_profiles`:
   ```sql
   CREATE TABLE customer_profiles (resource_id TEXT PRIMARY KEY, customer_reference TEXT, full_name TEXT, email TEXT, phone TEXT, email_hash TEXT, account_status TEXT NOT NULL, updated_at TEXT NOT NULL)
   ```
9. `customer_profiles_primary`:
   ```sql
   CREATE TABLE customer_profiles_primary (resource_id TEXT PRIMARY KEY, user_id TEXT NOT NULL, full_name TEXT NOT NULL, email TEXT NOT NULL, phone TEXT NOT NULL, account_status TEXT NOT NULL, updated_at TEXT NOT NULL)
   ```
10. `customer_profiles_failover_replica`:
   ```sql
   CREATE TABLE customer_profiles_failover_replica (resource_id TEXT PRIMARY KEY, user_id TEXT NOT NULL, full_name TEXT NOT NULL, email TEXT NOT NULL, phone TEXT NOT NULL, account_status TEXT NOT NULL, updated_at TEXT NOT NULL)
   ```
11. `customer_analytics_profiles`:
   ```sql
   CREATE TABLE customer_analytics_profiles (resource_id TEXT PRIMARY KEY, customer_reference TEXT, email TEXT, phone TEXT, email_hash TEXT, audience_cohort TEXT NOT NULL, updated_at TEXT NOT NULL)
   ```
12. `customer_search_documents`:
   ```sql
   CREATE TABLE customer_search_documents (resource_id TEXT PRIMARY KEY, customer_reference TEXT, display_name TEXT, email TEXT, phone TEXT, email_hash TEXT, index_name TEXT NOT NULL, updated_at TEXT NOT NULL)
   ```
13. `search_documents_primary`:
   ```sql
   CREATE TABLE search_documents_primary (resource_id TEXT PRIMARY KEY, display_name TEXT, email TEXT, source_resource_id TEXT, indexed_at TEXT)
   ```
14. `connector_subscriptions`:
   ```sql
   CREATE TABLE connector_subscriptions (resource_id TEXT PRIMARY KEY, customer_reference TEXT, customer_email TEXT, connector_name TEXT NOT NULL, enabled INTEGER NOT NULL CHECK (enabled IN (0,1)), last_delivery_status TEXT NOT NULL, updated_at TEXT NOT NULL)
   ```
15. `backup_restore_entries`:
   ```sql
   CREATE TABLE backup_restore_entries (resource_id TEXT PRIMARY KEY, customer_reference TEXT, customer_email TEXT, archive_key TEXT NOT NULL, restore_allowed INTEGER NOT NULL CHECK (restore_allowed IN (0,1)), updated_at TEXT NOT NULL)
   ```
16. `customer_exports`:
   ```sql
   CREATE TABLE customer_exports (resource_id TEXT PRIMARY KEY, customer_reference TEXT, owner_email TEXT, owner_phone TEXT, object_key TEXT NOT NULL, updated_at TEXT NOT NULL)
   ```
17. `support_records`:
   ```sql
   CREATE TABLE support_records (resource_id TEXT PRIMARY KEY, customer_reference TEXT, requester_name TEXT, requester_email TEXT, requester_phone TEXT, message_excerpt TEXT NOT NULL, updated_at TEXT NOT NULL)
   ```
18. `security_audit_records`:
   ```sql
   CREATE TABLE security_audit_records (resource_id TEXT PRIMARY KEY, subject_reference TEXT NOT NULL, event_code TEXT NOT NULL, retention_until TEXT NOT NULL, updated_at TEXT NOT NULL)
   ```

