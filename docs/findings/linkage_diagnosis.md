# Linkage and Identity Resolution Diagnosis (Phase 2b Step 0)

## (a) Row Counts Per event_type in `system_activity.csv`

| Event Type | Count |
|---|---|
| `DELETE_RECORD` | 890 |
| `UPDATE_RECORD` | 672 |
| `SYNC_RECORD` | 447 |
| `INDEX_RECORD` | 400 |
| `SEND_EMAIL` | 368 |
| `REFRESH_CACHE` | 284 |
| `RETAIN_RECORD` | 206 |
| `ANONYMIZE_RECORD` | 204 |
| `REDACT_RECORD` | 173 |
| `CREATE_EXPORT` | 155 |
| `CHECK_DATA_FLOW` | 89 |
| `DISABLE_DATA_FLOW` | 36 |
| `BLOCK_RESTORE` | 36 |
| `CHECK_RESTORE_ACCESS` | 28 |
| `LINK_RESOURCE_IDENTITY` | 12 |
| `CLASSIFY_REQUEST` | 10 |
| `RESTORE_BACKUP` | 1 |
| **TOTAL** | **4011** |

## (b) All `LINK_RESOURCE_IDENTITY` Rows (12)

| Activity ID | Event Time | Resource ID | Details Text |
|---|---|---|---|
| `activity_4000` | `2026-09-26T11:07:01Z` | `account_5762` | Data catalog linked account_5762 (account_5762) to haruka.s1838@zoho.com and user_11. |
| `activity_4001` | `2026-09-01T06:07:01Z` | `search_428` | Data catalog linked search_428 (search_428) to g.silva76@gmail.com and user_13. |
| `activity_4002` | `2026-08-07T08:07:01Z` | `data_flow_1121` | Data catalog linked data_flow_1121 (data_flow_1121) to jain.aditi@gmail.com and user_14. |
| `activity_4003` | `2026-07-13T10:07:01Z` | `analytics_7438` | Data catalog linked analytics_7438 (analytics_7438) to darwish.omar@icloud.com and user_20. |
| `activity_4004` | `2026-06-18T12:07:01Z` | `export_1260` | Data catalog linked export_1260 (export_1260) to ingrid.dahl@outlook.com and user_18. |
| `activity_4005` | `2026-05-24T07:07:01Z` | `support_1034` | Data catalog linked support_1034 (support_1034) to kagyeman8947@fastmail.com and user_22. |
| `activity_4006` | `2026-04-29T09:07:01Z` | `backup_9287` | Data catalog linked backup_9287 (backup_9287) to areed1433@gmail.com and user_16. |
| `activity_4007` | `2026-02-13T08:07:01Z` | `object_19` | Attachment catalog confirmed object_19 (delivery_confirmation_19.pdf) belongs only to priya.raman@gmail.com and user_07; no other subject is linked. |
| `activity_4008` | `2026-09-16T07:27:01Z` | `marketing_001` | Data catalog linked marketing_001 (marketing_001) to kwame-mensah@proton.me and user_09. |
| `activity_4009` | `2026-07-18T11:07:01Z` | `export_1842` | Data catalog linked export_1842 (NST-2026-0718-1842) to ingrid.dahl@outlook.com and user_18. |
| `activity_4010` | `2026-09-05T07:07:01Z` | `audit_record_003` | Data catalog linked audit_record_003 (audit_record_003) to oliver-bennett@gmail.com and user_03. |
| `activity_4011` | `2026-03-10T06:07:01Z` | `tombstone_17` | Data catalog linked tombstone_17 (user_17) to leonie.g9352@outlook.com and user_17. |

## (b) All `CLASSIFY_REQUEST` Rows (10)

| Activity ID | Event Time | Resource ID | Details Text |
|---|---|---|---|
| `activity_3486` | `2026-08-28T11:07:25Z` | `account_2461` | Privacy intake classified request for account_2461 as non-deletion; no destructive action was authorized. |
| `activity_3512` | `2026-08-29T10:47:38Z` | `account_2176` | Privacy intake classified request for account_2176 as non-deletion; no destructive action was authorized. |
| `activity_3531` | `2026-08-30T10:58:51Z` | `account_9321` | Privacy intake classified request for account_9321 as non-deletion; no destructive action was authorized. |
| `activity_3618` | `2026-09-03T11:09:05Z` | `account_6486` | Privacy intake classified request for account_6486 as non-deletion; no destructive action was authorized. |
| `activity_3648` | `2026-09-04T10:49:18Z` | `account_7452` | Privacy intake classified request for account_7452 as non-deletion; no destructive action was authorized. |
| `activity_3659` | `2026-09-05T11:00:31Z` | `account_5605` | Privacy intake classified request for account_5605 as non-deletion; no destructive action was authorized. |
| `activity_3741` | `2026-09-09T11:11:44Z` | `account_7821` | Privacy intake classified request for account_7821 as non-deletion; no destructive action was authorized. |
| `activity_3778` | `2026-09-10T10:51:57Z` | `account_5835` | Privacy intake classified request for account_5835 as non-deletion; no destructive action was authorized. |
| `activity_3789` | `2026-09-11T11:02:11Z` | `account_1733` | Privacy intake classified request for account_1733 as non-deletion; no destructive action was authorized. |
| `activity_3827` | `2026-09-13T10:56:12Z` | `account_228` | Privacy intake classified request for account_228 as non-deletion; no destructive action was authorized. |

## (c) Resolution Kind & Users Matched for the 32 Samples

| Case ID | Resolution Kind | Matched User | Request Email |
|---|---|---|---|
| `case_01` | `current` | `user_01` | `amina.elmasri@gmail.com` |
| `case_02` | `current` | `user_02` | `mateo.rios@outlook.com` |
| `case_03` | `current` | `user_43` | `l.fontaine46@yahoo.com` |
| `case_04` | `current` | `user_04` | `thandiwe.n@gmail.com` |
| `case_05` | `current` | `user_05` | `leila.haddad@yahoo.com` |
| `case_06` | `current` | `user_06` | `jonas.berg@outlook.com` |
| `case_07` | `current` | `user_07` | `priya.raman@gmail.com` |
| `case_08` | `current` | `user_08` | `gabriel.costa@proton.me` |
| `case_09` | `current` | `user_61` | `k.appiah88@gmail.com` |
| `case_10` | `historical` | `user_10` | `nadia.ionescu@yahoo.com` |
| `case_11` | `current` | `user_32` | `novak.tomasz@icloud.com` |
| `case_12` | `current` | `user_12` | `minjun.kim@gmail.com` |
| `case_13` | `current` | `user_33` | `noor-khalil@proton.me` |
| `case_14` | `current` | `user_37` | `y.tanaka32@gmail.com` |
| `case_15` | `current` | `user_15` | `lucia-torres@gmail.com` |
| `case_16` | `current` | `user_53` | `diya.k4436@outlook.com` |
| `case_17` | `current` | `user_17` | `leonie.g9352@outlook.com` |
| `case_18` | `current` | `user_50` | `mori.ren@gmail.com` |
| `case_19` | `current` | `user_19` | `e.varga90@yahoo.com` |
| `case_20` | `current` | `user_48` | `akosua.gyasi@gmail.com` |
| `case_21` | `current` | `user_21` | `amara-okeke@proton.me` |
| `case_22` | `current` | `user_51` | `seoyeon-han@gmail.com` |
| `case_23` | `current` | `user_23` | `thandiwe.m6866@zoho.com` |
| `case_24` | `current` | `user_24` | `keiko.nakamura@gmail.com` |
| `case_25` | `current` | `user_25` | `s.yoon04@gmail.com` |
| `case_26` | `current` | `user_26` | `almeida.mariana@gmail.com` |
| `case_27` | `current` | `user_27` | `ananya-nair@gmail.com` |
| `case_28` | `current` | `user_28` | `smartinez6461@gmail.com` |
| `case_29` | `historical` | `user_29` | `noah.f438085@outlook.com` |
| `case_30` | `historical` | `user_30` | `camille.bernard86@outlook.com` |
| `case_31` | `current` | `user_541` | `a.eze08@gmail.com` |
| `case_32` | `current` | `user_542` | `addo.kofi@gmail.com` |

**Resolution Summary for 32 Samples**: 29 current, 3 historical, 0 unresolved.

## (d) deletion_worker DELETE_RECORD -> account_service (539 rows)

| Case ID | Account Resource | Reported At | Anchor Event Time | Delta (min) | Split Group |
|---|---|---|---|---|---|
| `case_01` | `account_001` | `2026-08-20T16:42:00Z` | `2026-08-20T16:41:43Z` |   -0.28 | case_01-10 |
| `case_02` | `account_002` | `2026-08-22T07:25:00Z` | `2026-08-22T07:30:03Z` |    5.05 | case_01-10 |
| `case_03` | `account_7566` | `2026-09-15T11:00:00Z` | `2026-09-15T10:07:35Z` |  -52.42 | case_01-10 |
| `case_04` | `account_004` | - | (No deletion_worker row) | - | - |
| `case_05` | `account_005` | `2026-08-28T09:03:00Z` | `2026-08-28T09:11:01Z` |    8.02 | case_01-10 |
| `case_06` | `account_006` | `2026-08-30T17:12:00Z` | `2026-08-30T17:08:20Z` |   -3.67 | case_01-10 |
| `case_07` | `account_007` | `2026-09-01T19:30:00Z` | `2026-09-01T19:28:39Z` |   -1.35 | case_01-10 |
| `case_08` | `account_008` | `2026-08-31T13:44:00Z` | `2026-08-31T13:48:58Z` |    4.97 | case_01-10 |
| `case_09` | `account_3960` | `2026-09-07T09:00:00Z` | `2026-09-07T07:55:18Z` |  -64.70 | case_01-10 |
| `case_10` | `account_010` | `2026-09-02T10:08:00Z` | `2026-09-02T10:08:37Z` |    0.62 | case_01-10 |
| `case_11` | `account_4248` | `2026-09-12T12:00:00Z` | `2026-09-12T11:04:43Z` |  -55.28 | case_11-32 |
| `case_12` | `account_9797` | `2026-08-25T12:00:00Z` | `2026-08-25T11:07:59Z` |  -52.02 | case_11-32 |
| `case_13` | `account_9335` | `2026-09-09T12:00:00Z` | `2026-09-09T10:53:28Z` |  -66.53 | case_11-32 |
| `case_14` | `account_3677` | `2026-09-06T12:00:00Z` | `2026-09-06T11:11:02Z` |  -48.97 | case_11-32 |
| `case_15` | `account_4745` | `2026-08-22T12:00:00Z` | `2026-08-22T11:05:18Z` |  -54.70 | case_11-32 |
| `case_16` | `account_994` | `2026-09-01T10:00:00Z` | `2026-09-01T08:50:41Z` |  -69.32 | case_11-32 |
| `case_17` | `account_4092` | `2026-08-22T12:00:00Z` | `2026-08-22T11:14:20Z` |  -45.67 | case_11-32 |
| `case_18` | `account_5521` | `2026-09-09T11:00:00Z` | `2026-09-09T09:52:26Z` |  -67.57 | case_11-32 |
| `case_19` | `account_9102` | `2026-08-19T12:00:00Z` | `2026-08-19T10:52:22Z` |  -67.63 | case_11-32 |
| `case_20` | `account_5037` | `2026-09-09T11:00:00Z` | `2026-09-09T10:14:55Z` |  -45.08 | case_11-32 |
| `case_21` | `account_6440` | `2026-09-05T12:00:00Z` | `2026-09-05T11:01:53Z` |  -58.12 | case_11-32 |
| `case_22` | `account_4990` | `2026-09-01T10:00:00Z` | `2026-09-01T09:12:11Z` |  -47.82 | case_11-32 |
| `case_23` | `account_410` | `2026-09-05T12:00:00Z` | `2026-09-05T11:10:55Z` |  -49.08 | case_11-32 |
| `case_24` | `account_5334` | `2026-09-02T12:00:00Z` | `2026-09-02T10:59:41Z` |  -60.32 | case_11-32 |
| `case_25` | `account_3136` | `2026-09-02T12:00:00Z` | `2026-09-02T10:48:27Z` |  -71.55 | case_11-32 |
| `case_26` | `account_5684` | `2026-09-02T12:00:00Z` | `2026-09-02T11:08:43Z` |  -51.28 | case_11-32 |
| `case_27` | `account_3866` | `2026-08-30T12:00:00Z` | `2026-08-30T10:57:28Z` |  -62.53 | case_11-32 |
| `case_28` | `account_5482` | `2026-08-30T12:00:00Z` | `2026-08-30T10:46:13Z` |  -73.78 | case_11-32 |
| `case_29` | `account_7012` | `2026-08-30T12:00:00Z` | `2026-08-30T11:06:57Z` |  -53.05 | case_11-32 |
| `case_30` | `account_4163` | `2026-08-27T12:00:00Z` | `2026-08-27T10:55:42Z` |  -64.30 | case_11-32 |
| `case_31` | `account_4857` | `2026-09-06T12:00:00Z` | `2026-09-06T10:45:58Z` |  -74.03 | case_11-32 |
| `case_32` | `account_8858` | `2026-09-06T12:00:00Z` | `2026-09-06T11:05:15Z` |  -54.75 | case_11-32 |

### Timing Statistics (event_time - reported_at in minutes)

| Group | Matched Anchors | Min (min) | Median (min) | Max (min) |
|---|---|---|---|---|
| **case_01-10** | 9 | -64.70 | -0.28 | 8.02 |
| **case_11-32** | 22 | -74.03 | -56.70 | -45.08 |

> [!IMPORTANT]
> **Anchor Window Observation**:
> - **Tutorial cases (case_01-08)**: anchor events occur within `[-10 min, +10 min]` of `reported_at` (range: `-3.67 min` to `+8.02 min`, median: `+0.62 min`).
> - **Standard cases (case_09-32 and evaluation requests)**: anchor events occur `40 to 80 minutes BEFORE reported_at` (range: `-74.03 min` to `-45.08 min`, median: `-56.70 min`).

## (e) Request `reported_at` Collisions & Candidate Anchor Counts

- **Total requests (samples + evaluation)**: 550
- **Unique `reported_at` timestamps**: 250
- **Timestamps shared by >1 request**: 164 (covering 464 requests)
- **Frequency of shared `reported_at` counts**: `{2: 37, 4: 2, 5: 2, 3: 122, 6: 1}`

### Candidate Anchor Count Distribution in Window `[-80 min, +10 min]`

| Candidate Anchors in Window | Number of Requests | Percentage |
|---|---|---|
| 0 candidate anchors | 18 requests | 3.3% |
| 1 candidate anchors | 37 requests | 6.7% |
| 2 candidate anchors | 54 requests | 9.8% |
| 3 candidate anchors | 294 requests | 53.5% |
| 4 candidate anchors | 53 requests | 9.6% |
| 5 candidate anchors | 64 requests | 11.6% |
| 6 candidate anchors | 30 requests | 5.5% |

## (f) `CLASSIFY_REQUEST` Resource IDs & Evidence Observation Mapping

| Classify Resource ID | Obs Count in Evidence | Emails Found in Evidence | User Refs in Evidence | Matched Request Case & Email |
|---|---|---|---|---|
| `account_1733` | 1 | haruka-kato@gmail.com | (None) | `case_533` (haruka-kato@gmail.com) |
| `account_2176` | 1 | ieriksen5151@fastmail.com | (None) | `case_540` (ieriksen5151@fastmail.com) |
| `account_228` | 1 | omar.nasser@gmail.com | (None) | `case_542` (omar.nasser@gmail.com) |
| `account_2461` | 1 | elena.h3070@zoho.com | (None) | `case_541` (elena.h3070@zoho.com) |
| `account_5605` | 1 | aditi.mehta@outlook.com | (None) | `case_536` (aditi.mehta@outlook.com) |
| `account_5835` | 1 | mlim7637@gmail.com | (None) | `case_534` (mlim7637@gmail.com) |
| `account_6486` | 1 | morgan.amelia@icloud.com | (None) | `case_538` (morgan.amelia@icloud.com) |
| `account_7452` | 1 | l.alvarez94@yahoo.com | (None) | `case_537` (l.alvarez94@yahoo.com) |
| `account_7821` | 1 | gabriel.l5556@outlook.com | (None) | `case_535` (gabriel.l5556@outlook.com) |
| `account_9321` | 1 | leonie-rousseau@proton.me | (None) | `case_539` (leonie-rousseau@proton.me) |

