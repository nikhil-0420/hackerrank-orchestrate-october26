# Failure Log & Remediation Tracker

This document records failure modes, edge cases, regression findings, and remediation fixes discovered during development and evaluation of the deletion-audit agent.

## Log Entries

*No failure modes recorded yet. Entries will be appended as test cases and pipeline runs identify discrepancies.*

## Phase 1 gate

`	ext
================================================================================
PHASE 1 EVIDENCE INGESTION REPORT
================================================================================

--- Per-File Ingestion Stats ---
File ID       Kind   Obs    Unparsed  File Path
--------------------------------------------------------------------------------
evidence_01   log    36     0         evidence/logs/service_events_ap_south_20260915.log
evidence_02   json   41     0         evidence/records/customer_data_snapshot_bundle_20260917.json
evidence_03   txt    41     0         evidence/records/customer_account_handover_20261001.txt
evidence_04   png    0      0         evidence/images/account_admin_console_20260926.png
evidence_05   sql    61     0         evidence/databases/customer_data_read_replica_20260921.sql
evidence_06   log    37     0         evidence/logs/structured_service_events_eu_west_20260918.log
evidence_07   json   30     0         evidence/records/customer_data_snapshot_bundle_20260913.json
evidence_08   log    36     0         evidence/logs/search_index_diagnostic_20260906.log
evidence_09   png    0      0         evidence/images/search_index_inspector_20260901.png
evidence_10   sql    59     0         evidence/databases/customer_data_read_replica_20260827.sql
evidence_11   log    36     0         evidence/logs/syslog_archive_us_east_20260824.log
evidence_12   json   29     0         evidence/records/customer_data_snapshot_bundle_20260819.json
evidence_13   json   39     0         evidence/records/connector_configurations_20260812.json
evidence_14   png    0      0         evidence/images/connector_management_console_20260807.png
evidence_15   sql    49     0         evidence/databases/customer_data_read_replica_20260802.sql
evidence_16   log    36     0         evidence/logs/application_trace_ap_northeast_20260730.log
evidence_17   json   36     0         evidence/records/customer_data_snapshot_bundle_20260725.json
evidence_18   pdf    0      0         evidence/documents/account_history_report_20260718.pdf
evidence_19   png    0      0         evidence/images/analytics_profile_view_20260713.png
evidence_20   sql    63     0         evidence/databases/customer_data_read_replica_20260708.sql
evidence_21   log    41     0         evidence/logs/operations_stream_eu_central_20260705.log
evidence_22   json   71     0         evidence/records/customer_data_snapshot_bundle_20260630.json
evidence_23   png    0      0         evidence/images/customer_export_console_20260618.png
evidence_24   sql    50     0         evidence/databases/customer_data_read_replica_20260613.sql
evidence_25   log    43     0         evidence/logs/cloud_runtime_export_us_west_20260608.log
evidence_26   json   32     0         evidence/records/customer_data_snapshot_bundle_20260605.json
evidence_27   pdf    0      0         evidence/documents/legal_retention_register_20260529.pdf
evidence_28   png    0      0         evidence/images/support_ticket_console_20260524.png
evidence_29   sql    85     0         evidence/databases/customer_data_regional_replicas_20260519.sql
evidence_30   log    38     0         evidence/logs/service_events_sa_east_20260516.log
evidence_31   json   74     0         evidence/records/customer_data_snapshot_bundle_20260511.json
evidence_32   png    0      0         evidence/images/backup_restore_console_20260429.png
evidence_33   sql    89     0         evidence/databases/customer_data_regional_replicas_20260424.sql
evidence_34   log    44     0         evidence/logs/structured_service_events_ca_central_20260419.log
evidence_35   json   28     0         evidence/records/customer_data_snapshot_bundle_20260416.json
evidence_36   json   46     0         evidence/records/customer_export_manifest_20260409.json
evidence_37   png    0      0         evidence/images/security_audit_explorer_20260905.png
evidence_38   sql    85     0         evidence/databases/customer_data_regional_replicas_20260330.sql
evidence_39   log    40     0         evidence/logs/syslog_archive_ap_southeast_20260325.log
evidence_40   json   31     0         evidence/records/customer_data_snapshot_bundle_20260322.json
evidence_41   log    39     0         evidence/logs/notification_delivery_20260315.log
evidence_42   png    0      0         evidence/images/deleted_account_reference_20260310.png
evidence_43   sql    51     0         evidence/databases/customer_data_reporting_replica_20260305.sql
evidence_44   log    41     0         evidence/logs/application_trace_eu_north_20260302.log
evidence_45   json   75     0         evidence/records/customer_data_snapshot_bundle_20260223.json
evidence_46   png    0      0         evidence/images/object_storage_browser_20260213.png
evidence_47   sql    49     0         evidence/databases/customer_data_reporting_replica_20260208.sql
evidence_48   log    36     0         evidence/logs/operations_stream_me_central_20260203.log
evidence_49   json   34     0         evidence/records/customer_data_snapshot_bundle_20260131.json
evidence_50   json   20     0         evidence/records/security_audit_ledger_20261001.json
evidence_51   json   4      0         evidence/records/customer_data_snapshot_bundle_20260915.json
evidence_52   sql    32     0         evidence/databases/customer_data_failover_replica_20260920.sql
evidence_53   log    300    0         evidence/logs/cloud_runtime_export_af_south_20260930.log
evidence_54   sql    7      0         evidence/databases/customer_accounts_failover_replica_20260902.sql
evidence_55   pdf    0      0         evidence/documents/security_retention_extract.pdf
evidence_56   json   2      0         evidence/records/customer_analytics_report_20260907.json
evidence_57   sql    3      0         evidence/databases/customer_search_primary_20260910.sql
evidence_58   pdf    0      0         evidence/documents/delivery_correction_attachment.pdf
evidence_59   json   2      0         evidence/records/customer_export_jobs_20260914.json
evidence_60   png    0      0         evidence/images/marketing_profile_console.png
evidence_61   log    4      0         evidence/logs/support_replica.log
evidence_62   json   29     0         evidence/records/service_resource_export_20260129_114459.json
evidence_63   sql    17     0         evidence/databases/customer_data_inventory_20260213.sql
evidence_64   log    26     0         evidence/logs/resource_lookup_trace_20260218_083911.log
evidence_65   json   27     0         evidence/records/service_resource_export_20260228_103637.json
evidence_66   sql    23     0         evidence/databases/customer_data_inventory_20260310.sql
evidence_67   log    1      0         evidence/logs/resource_lookup_trace_20260310_061801.log
evidence_68   json   25     0         evidence/records/service_resource_export_20260320_072349.json
evidence_69   sql    18     0         evidence/databases/customer_data_inventory_20260404.sql
evidence_70   log    24     0         evidence/logs/resource_lookup_trace_20260414_054007.log
evidence_71   json   28     0         evidence/records/service_resource_export_20260429_083222.json
evidence_72   sql    21     0         evidence/databases/customer_data_inventory_20260504.sql
evidence_73   log    33     0         evidence/logs/resource_lookup_trace_20260509_104353.log
evidence_74   json   25     0         evidence/records/service_resource_export_20260514_114454.json
evidence_75   sql    24     0         evidence/databases/customer_data_inventory_20260524.sql
evidence_76   log    23     0         evidence/logs/resource_lookup_trace_20260529_074313.log
evidence_77   json   27     0         evidence/records/service_resource_export_20260603_083457.json
evidence_78   sql    19     0         evidence/databases/customer_data_inventory_20260618.sql
evidence_79   log    29     0         evidence/logs/resource_lookup_trace_20260623_053726.log
evidence_80   json   24     0         evidence/records/service_resource_export_20260628_062556.json
evidence_81   sql    24     0         evidence/databases/customer_data_inventory_20260703.sql
evidence_82   log    26     0         evidence/logs/resource_lookup_trace_20260713_093359.log
evidence_83   json   29     0         evidence/records/service_resource_export_20260718_104335.json
evidence_84   sql    26     0         evidence/databases/customer_data_inventory_20260723.sql
evidence_85   log    22     0         evidence/logs/resource_lookup_trace_20260728_054417.log
evidence_86   json   23     0         evidence/records/service_resource_export_20260807_074104.json
evidence_87   sql    19     0         evidence/databases/customer_data_inventory_20260817.sql
evidence_88   log    22     0         evidence/logs/resource_lookup_trace_20260822_103910.log
evidence_89   json   23     0         evidence/records/service_resource_export_20260901_053316.json
evidence_90   sql    0      0         evidence/databases/customer_data_inventory_20260905.sql
evidence_91   log    30     0         evidence/logs/resource_lookup_trace_20260911_074253.log
evidence_92   json   36     0         evidence/records/service_resource_export_20260915_114455.json
evidence_93   sql    17     0         evidence/databases/customer_data_inventory_20260916.sql
evidence_94   log    28     0         evidence/logs/resource_lookup_trace_20260926_103856.log
--------------------------------------------------------------------------------
Total Evidence Files : 94
Total Observations   : 2893
Total Coverage Scopes: 364
Total Unparsed Lines : 0
================================================================================

--- 10 Sampled Observations Traced to Source Text (Seed=42) ---

[1/10] Observation: account_5375 (File: evidence_83)
  System / Collection : account_service / profile_lookups
  Obs Time / File Time: 2026-07-18T10:24:53Z / 2026-07-18T10:43:35Z
  Source Kind / Ref   : json (service_export:account_service.profile_lookups idx:1 id:account_5375)
  Identifiers         : email='ethan.b9744@outlook.com', phone=None, user_ref=None, name=None, masked=False
  State Sample        : {'observed_at': '2026-07-18T10:24:53Z', 'profile': {'customer_reference': None, 'email': 'ethan.b9744@outlook.com', 'email_hash': None, 'full_name': None, 'phon...
  Raw Source Snippet  :
    {
      "observed_at": "2026-07-18T10:24:53Z",
      "profile": {
        "customer_reference": null,
        "email": "ethan.b9744@outlook.com",
        "email_hash": null,
        "full_name": null,
        "phone": null
      },
      "resource_id": "account_5375",
      "status_code": 200
    }
--------------------------------------------------------------------------------
[2/10] Observation: audit_record_9665 (File: evidence_15)
  System / Collection : security_service / security_audit_events
  Obs Time / File Time: 2026-08-02T07:00:00Z / 2026-08-02T07:00:00Z
  Source Kind / Ref   : sql (table:customer_data_primary row_id:audit_record_9665)
  Identifiers         : email=None, phone=None, user_ref='user_156', name=None, masked=False
  State Sample        : {'resource_id': 'audit_record_9665', 'subject_reference': 'user_156', 'event_name': 'account_deletion_reviewed', 'actor_type': 'automated_privacy_workflow', 'in...
  Raw Source Snippet  :
    SQL Record from table:customer_data_primary row_id:audit_record_9665: {'resource_id': 'audit_record_9665', 'subject_reference': 'user_156', 'event_name': 'account_deletion_reviewed', 'actor_type': 'automated_privacy_workflow', 'integrity_seal': 'sha256:00000000000000000000000000000000000000000000000000000000000025c1', 'replica_of': 'customer_data_primary', 'table_name': 'customer_data_primary', 'row_updated_at': '2026-08-02T07:00:00Z'}
--------------------------------------------------------------------------------
[3/10] Observation: search_7078 (File: evidence_03)
  System / Collection : search_service / search_index_entry
  Obs Time / File Time: 2026-10-01T12:00:00Z / 2026-10-01T12:00:00Z
  Source Kind / Ref   : txt (line:31 id:search_7078)
  Identifiers         : email='asingh1489@gmail.com', phone=None, user_ref=None, name=None, masked=False
  State Sample        : {'category': 'SEARCH_INDEX_ENTRY', 'state': 'FOUND', 'result': 'FOUND', 'raw_identifier': 'asingh1489@gmail.com'}...
  Raw Source Snippet  :
    - 2026-10-01T12:00:00Z | search_service | search_7078 | SEARCH_INDEX_ENTRY | FOUND | asingh1489@gmail.com
--------------------------------------------------------------------------------
[4/10] Observation: analytics_8011 (File: evidence_33)
  System / Collection : analytics_platform / customer_analytics_reports
  Obs Time / File Time: 2026-04-24T08:00:00Z / 2026-04-24T08:00:00Z
  Source Kind / Ref   : sql (table:customer_data_replica_eu_west row_id:analytics_8011)
  Identifiers         : email='thiago-nascimento@gmail.com', phone='+55 31 95213-2663', user_ref='user_351', name=None, masked=False
  State Sample        : {'resource_id': 'analytics_8011', 'user_id': 'user_351', 'email': 'thiago-nascimento@gmail.com', 'phone': '+55 31 95213-2663', 'email_hash': '86f7583a771020f5ca...
  Raw Source Snippet  :
    SQL Record from table:customer_data_replica_eu_west row_id:analytics_8011: {'resource_id': 'analytics_8011', 'user_id': 'user_351', 'email': 'thiago-nascimento@gmail.com', 'phone': '+55 31 95213-2663', 'email_hash': '86f7583a771020f5ca68e00c3be6dc5abcfa194d12f361f7082676cd6fd53529', 'reporting_window': 'last_90_days', 'metrics': {'sessions_30d': 3, 'products_viewed_30d': 17, 'orders_completed_90d': 1, 'revenue_90d_usd': 59.98}, 'recent_activity': [{'event': 'product_viewed', 'product': 'Mechanical keyboard'}, {'event': 'added_to_cart', 'product': 'Mechanical keyboard'}, {'event': 'purchase_completed', 'product': 'Mechanical keyboard', 'quantity': 2}], 'replica_of': 'customer_data_replica_eu_west', 'table_name': 'customer_data_replica_eu_west', 'row_updated_at': '2026-04-24T08:00:00Z'}
--------------------------------------------------------------------------------
[5/10] Observation: search_4054 (File: evidence_31)
  System / Collection : search_service / customer_search_documents
  Obs Time / File Time: 2026-05-09T11:00:00Z / 2026-05-11T11:00:00Z
  Source Kind / Ref   : json (snapshot:customer_search_documents idx:0 id:search_4054)
  Identifiers         : email='aoi.i256693@zoho.com', phone=None, user_ref='user_323', name='Aoi Ito', masked=False
  State Sample        : {'resource_id': 'search_4054', 'index_name': 'customer_directory_v3', 'document': {'display_name': 'Aoi Ito', 'email': 'aoi.i256693@zoho.com', 'customer_referen...
  Raw Source Snippet  :
    {
      "resource_id": "search_4054",
      "index_name": "customer_directory_v3",
      "document": {
        "display_name": "Aoi Ito",
        "email": "aoi.i256693@zoho.com",
        "customer_reference": "user_323"
      }
    }
--------------------------------------------------------------------------------
[6/10] Observation: search_6265 (File: evidence_29)
  System / Collection : search_service / customer_search_documents
  Obs Time / File Time: 2026-05-19T06:00:00Z / 2026-05-19T06:00:00Z
  Source Kind / Ref   : sql (table:customer_data_replica_ap_south row_id:search_6265)
  Identifiers         : email='amponsah.akosua@icloud.com', phone=None, user_ref='user_308', name='Akosua Amponsah', masked=False
  State Sample        : {'resource_id': 'search_6265', 'index_name': 'customer_directory_v3', 'document': {'display_name': 'Akosua Amponsah', 'email': 'amponsah.akosua@icloud.com', 'cu...
  Raw Source Snippet  :
    SQL Record from table:customer_data_replica_ap_south row_id:search_6265: {'resource_id': 'search_6265', 'index_name': 'customer_directory_v3', 'document': {'display_name': 'Akosua Amponsah', 'email': 'amponsah.akosua@icloud.com', 'customer_reference': 'user_308'}, 'replica_of': 'customer_data_replica_ap_south', 'table_name': 'customer_data_replica_ap_south', 'row_updated_at': '2026-05-19T06:00:00Z'}
--------------------------------------------------------------------------------
[7/10] Observation: audit_record_2736 (File: evidence_20)
  System / Collection : security_service / security_audit_events
  Obs Time / File Time: 2026-07-08T09:00:00Z / 2026-07-08T09:00:00Z
  Source Kind / Ref   : sql (table:customer_data_primary row_id:audit_record_2736)
  Identifiers         : email=None, phone=None, user_ref='user_202', name=None, masked=False
  State Sample        : {'resource_id': 'audit_record_2736', 'subject_reference': 'user_202', 'event_name': 'account_deletion_reviewed', 'actor_type': 'automated_privacy_workflow', 'in...
  Raw Source Snippet  :
    SQL Record from table:customer_data_primary row_id:audit_record_2736: {'resource_id': 'audit_record_2736', 'subject_reference': 'user_202', 'event_name': 'account_deletion_reviewed', 'actor_type': 'automated_privacy_workflow', 'integrity_seal': 'sha256:0000000000000000000000000000000000000000000000000000000000000ab0', 'replica_of': 'customer_data_primary', 'table_name': 'customer_data_primary', 'row_updated_at': '2026-07-08T09:00:00Z'}
--------------------------------------------------------------------------------
[8/10] Observation: data_flow_7812 (File: evidence_13)
  System / Collection : integration_service / connector_configurations_20260812
  Obs Time / File Time: 2026-08-12T09:00:00Z / 2026-08-12T09:00:00Z
  Source Kind / Ref   : json (records:connector_configurations_20260812 idx:13 id:data_flow_7812)
  Identifiers         : email='mateo.alvarez@gmail.com', phone=None, user_ref=None, name=None, masked=False
  State Sample        : {'recorded_at': '2026-08-12T09:00:00Z', 'system': 'integration_service', 'resource_id': 'data_flow_7812', 'record_type': 'DATA_FLOW', 'result': 'ACTIVE', 'subje...
  Raw Source Snippet  :
    {
      "recorded_at": "2026-08-12T09:00:00Z",
      "system": "integration_service",
      "resource_id": "data_flow_7812",
      "record_type": "DATA_FLOW",
      "result": "ACTIVE",
      "subject_reference": "mateo.alvarez@gmail.com"
    }
--------------------------------------------------------------------------------
[9/10] Observation: search_5672 (File: evidence_89)
  System / Collection : search_service / index_queries
  Obs Time / File Time: 2026-09-01T03:05:19Z / 2026-09-01T05:33:16Z
  Source Kind / Ref   : json (service_export:search_service.index_queries idx:3 id:search_5672)
  Identifiers         : email='smorgan9115@fastmail.com', phone=None, user_ref=None, name=None, masked=False
  State Sample        : {'hits': {'documents': [{'customer_reference': None, 'display_name': None, 'email': 'smorgan9115@fastmail.com', 'email_hash': None, 'phone': None, 'resource_id'...
  Raw Source Snippet  :
    {
      "hits": {
        "documents": [
          {
            "customer_reference": null,
            "display_name": null,
            "email": "smorgan9115@fastmail.com",
            "email_hash": null,
            "phone": null,
            "resource_id": "search_5672"
          }
        ],
        "total": 1
      },
      "observed_at": "2026-09
--------------------------------------------------------------------------------
[10/10] Observation: analytics_8202 (File: evidence_66)
  System / Collection : analytics_platform / customer_analytics_profiles
  Obs Time / File Time: 2026-03-10T03:35:06Z / 2026-03-10T05:38:48Z
  Source Kind / Ref   : sql (table:customer_analytics_profiles row_id:analytics_8202)
  Identifiers         : email='advorak2441@gmail.com', phone=None, user_ref=None, name=None, masked=False
  State Sample        : {'resource_id': 'analytics_8202', 'customer_reference': None, 'email': 'advorak2441@gmail.com', 'phone': None, 'email_hash': None, 'audience_cohort': 'returning...
  Raw Source Snippet  :
    SQL Record from table:customer_analytics_profiles row_id:analytics_8202: {'resource_id': 'analytics_8202', 'customer_reference': None, 'email': 'advorak2441@gmail.com', 'phone': None, 'email_hash': None, 'audience_cohort': 'returning_customer', 'updated_at': '2026-03-10T03:35:06Z', 'replica_of': 'customer_analytics_profiles', 'table_name': 'customer_analytics_profiles'}
--------------------------------------------------------------------------------

ACCEPTANCE CHECK: All files parsed successfully with unparsed lines == 0.
```

## Phase 2b linker lab

### Linker Performance Summary vs Naive Baseline

| Metric | Naive Baseline (S1 only) | Phase 2b Linker | Delta / Gain |
|---|---|---|---|
| Target Ground Truth Resources | 111 | 111 | - |
| True Positives (TP) | 50 | 109 | +59 |
| False Positives (FP) | 1 | 0 | -1 |
| False Negatives (FN) | 61 | 2 | -59 |
| **Precision** | **98.04%** | **100.00%** | **+1.96%** |
| **Recall** | **45.05%** | **98.20%** | **+53.15%** |
| **F1 Score** | **61.73%** | **99.09%** | **+37.36%** |

### Per-Resource-Type Precision and Recall

| Resource Type | System | Ground Truth | TP | FP | FN | Precision | Recall |
|---|---|---|---|---|---|---|---|
| `account` | `account_service` | 32 | 32 | 0 | 0 | 100.00% | 100.00% |
| `search` | `search_service` | 12 | 12 | 0 | 0 | 100.00% | 100.00% |
| `support` | `support_platform` | 11 | 11 | 0 | 0 | 100.00% | 100.00% |
| `export` | `export_service` | 2 | 2 | 0 | 0 | 100.00% | 100.00% |
| `analytics` | `analytics_platform` | 13 | 13 | 0 | 0 | 100.00% | 100.00% |
| `flow` | `integration_service` | 9 | 9 | 0 | 0 | 100.00% | 100.00% |
| `backup` | `backup_service` | 6 | 6 | 0 | 0 | 100.00% | 100.00% |
| `audit` | `security_service` | 24 | 22 | 0 | 2 | 100.00% | 91.67% |
| `tombstone` | `identity_service` | 2 | 2 | 0 | 0 | 100.00% | 100.00% |

### Signal Ablation Study (Drop Each Signal)

| Ablation Experiment | Precision | Recall | F1 Score | Recall Loss (Delta) |
|---|---|---|---|---|
| **Full Linker (S1-S8)** | **100.00%** | **98.20%** | **99.09%** | **Baseline (0.00%)** |
| Drop S1 (Record Identifiers) | 100.00% | 87.39% | 93.27% | -10.81% |
| Drop S2 (User ID Joins) | 100.00% | 74.77% | 85.57% | -23.42% |
| Drop S3 (Merged Traces) | 100.00% | 98.20% | 99.09% | -0.00% |
| Drop S4 (Link Rows) | 100.00% | 98.20% | 99.09% | -0.00% |
| Drop S5 (Chain Keys) | 100.00% | 98.20% | 99.09% | -0.00% |
| Drop S6 (Handover Docs) | 100.00% | 97.30% | 98.63% | -0.90% |
| Drop S7 (Account Anchors) | 100.00% | 87.39% | 93.27% | -10.81% |
| Drop S8 (Activity Chain / Offsets) | 100.00% | 90.99% | 95.28% | -7.21% |

### Leave-One-Family-Out Check

| Excluded Evidence Family | Files Excluded | Precision | Recall | Recall Loss (Delta) |
|---|---|---|---|---|
| **None (Full Manifest)** | 0 | **100.00%** | **98.20%** | **0.00%** |
| `evidence/databases/` | 24 | 100.00% | 92.79% | -5.41% |
| `evidence/documents/` | 4 | 100.00% | 98.20% | -0.00% |
| `evidence/images/` | 11 | 100.00% | 98.20% | -0.00% |
| `evidence/logs/` | 26 | 97.78% | 79.28% | -18.92% |
| `evidence/records/` | 29 | 91.67% | 49.55% | -48.65% |

### Unattributed Ground Truth Resources on Samples

| Case ID | Resource ID | Expected System | Reason / Candidates |
|---|---|---|---|
| `case_18` | `audit_record_6645` | `security_service` | Absent in evidence files (evidence_id='') |
| `case_20` | `audit_record_5569` | `security_service` | Absent in evidence files (evidence_id='') |

