# Fabric Modernization

Case study: [From fragmented Azure resources to a unified Fabric platform](https://paulymurph.com/work/fabric-modernization)

This folder presents sanitized patterns for a Fabric-oriented medallion design:
versioned file intake, Bronze lineage, Silver snapshot/upsert processing,
freshness gating, and SQL reporting models.

## Extracts

| File | What it demonstrates |
| --- | --- |
| [`incremental_file_ingestion.py`](extracts/incremental_file_ingestion.py) | Discovers staged files and records immutable source identity before Bronze append |
| [`silver_snapshot_and_upsert.py`](extracts/silver_snapshot_and_upsert.py) | Separates current-state snapshot publication from keyed Delta upserts |
| [`reporting_freshness_check.py`](extracts/reporting_freshness_check.py) | Evaluates timezone-aware data readiness against a configurable SLA |
| [`gold_asset_processing.sql`](extracts/gold_asset_processing.sql) | Consolidates operational events into a declared one-row-per-asset reporting model |
| [`gold_inventory_aging.sql`](extracts/gold_inventory_aging.sql) | Isolates the latest snapshot before calculating open and closed inventory age |
| [`weekly_operations_summary.sql`](extracts/weekly_operations_summary.sql) | Produces a calendar-complete weekly operating summary with normalized targets |

## Coverage Boundary

The extracts demonstrate Spark/Delta and SQL design patterns, not a released
Fabric workspace. Direct S3/SFTP connectors, dbt project files, semantic-model
metadata, deployment pipelines, access-control configuration, run logs, and
billing evidence were not recovered into this package. Cost, runtime, hourly
cadence, governance, and adoption outcomes remain case-study claims rather than
claims proven by these files alone.
