# Fabric Modernization

Case study: [From fragmented Azure resources to a unified Fabric platform](https://paulymurph.com/work/fabric-modernization)

This folder presents sanitized patterns for a Fabric-oriented medallion design:
registered multi-dataset file intake, Bronze lineage and idempotency, Silver
snapshot/upsert processing, dependency freshness gating, and SQL reporting
models. Names and values are synthetic; the extracts are design evidence, not
deployable workspace artifacts or representations of production outcomes.

## Extracts

| File | What it demonstrates |
| --- | --- |
| [`incremental_file_ingestion.py`](extracts/incremental_file_ingestion.py) | Registers datasets, fingerprints files, builds manifest payloads, and defines obligations for duplicate-safe Bronze retries |
| [`silver_snapshot_and_upsert.py`](extracts/silver_snapshot_and_upsert.py) | Separates key rejects, requires their persistence, publishes validated snapshots, and applies ordered Delta upserts |
| [`reporting_freshness_check.py`](extracts/reporting_freshness_check.py) | Gates a reporting product on multiple timezone-aware dependencies and their individual SLAs |
| [`gold_asset_processing.sql`](extracts/gold_asset_processing.sql) | Models rack/container processing and host/component recovery at explicit composite-key grains |
| [`gold_inventory_aging.sql`](extracts/gold_inventory_aging.sql) | Distinguishes latest inventory state from movement history and bands open backlog age |
| [`weekly_operations_summary.sql`](extracts/weekly_operations_summary.sql) | Produces dependency-gated WBR measures, backlog, targets, and four-week rolling metrics |

## Operational Contracts

The illustrative registry separates inventory snapshots from append-oriented
container processing, component recovery, and inventory movement datasets. The
example builds pending manifest entries only for files whose content identity is
absent from the supplied completed set. Its callbacks are required to persist
file outcomes and rejects with bounded reason codes. The intended Bronze row key
is `(_source_id, _source_row_number)`; duplicate-safe retries also require stable
row numbering and a merge implementation that enforces that key.

Silver contracts intentionally differ by dataset. The snapshot function writes
a validated replacement of one complete snapshot at
`(facility_code, storage_location, container_id)`. Container events use
`(facility_code, rack_id, container_id, processing_cycle_id, event_sequence)`;
component recovery events use
`(facility_code, host_id, component_id, recovery_cycle_id, event_sequence)`;
inventory movements use `(facility_code, movement_id)`. The event and movement
tables preserve history through keyed upserts; they are not overwritten by a
later snapshot. Reject DataFrames are identified by the extract, but their
durable storage remains an implementation requirement outside the snippet.

Gold models expose processing-cycle milestones, recovery-cycle milestones,
latest inventory state, inventory movement context, backlog age bands, and
calendar-complete WBR metrics. WBR publication depends on current inventory,
movement history, both operational event streams, the business calendar, and
the target plan passing their declared freshness checks.

## Coverage Boundary

The extracts demonstrate Spark/Delta and SQL design patterns, not a released
Fabric workspace. Direct S3/SFTP connectors, dbt project files, semantic-model
metadata, deployment pipelines, access-control configuration, run logs, and
billing evidence were not recovered into this package. Cost, runtime, hourly
cadence, governance, and adoption outcomes remain case-study claims rather than
claims proven by these files alone.
