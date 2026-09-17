# Architecture

Classification: `reconstructed_from_context`

```text
synthetic managed file transfers
                 |
                 v
      multi-dataset intake registry
       + file manifest/checksum
       + malformed-file quarantine
                 |
                 v
  Bronze rows + rejects + source lineage
                 |
       +---------+------------------+
       |                            |
       v                            v
complete inventory snapshot    keyed history upsert
validated replacement          container processing events
                               component recovery events
                               inventory movements
       |                            |
       +-------------+--------------+
                     v
               Silver contracts
                     |
          +----------+-----------+
          |                      |
          v                      v
cycle milestones        current inventory +
and recovery status     movement history/backlog
          |                      |
          +----------+-----------+
                     v
       dependency freshness gate + calendar
                     |
                     v
        WBR weekly and rolling measures
                     |
                     v
          semantic/reporting layer
```

The example builds a pending manifest entry for each eligible discovered file
and uses `(dataset, checksum)` as content-based source identity. The intended
Bronze key is source identity plus source row number. Duplicate-safe retries
depend on deterministic row numbering, durable manifest state, and a merge
callback that enforces that key; those persistence details are not shown.
Registered CSV inputs that are empty, have header or schema mismatches, fail
parsing, or contain null keys or invalid timestamps are expected to produce
quarantine or reject records with bounded diagnostics.

Current inventory is snapshot state at
`(facility_code, storage_location, container_id)` and is replaced only after
completeness and uniqueness checks. Container, recovery, and movement history
use deterministic keyed upserts; their composite keys and source ordering are
declared in the dataset contract rather than inferred from one generic identifier.
Gold processing remains at processing-cycle or recovery-cycle grain. Inventory
aging starts from the latest eligible snapshot, uses movement history for
backlog-entry context, and never treats movement rows as current-state rows.

WBR output is calendar-complete and includes weekly flow, ending backlog, age
mix, normalized targets, and four-week rolling throughput. Publication is
blocked unless current inventory, movement history, both event streams,
calendar, and target-plan dependencies are ready. Lineage, reconciliation,
quarantine review, governance, and deployment controls remain explicit design
concerns, but no private configuration or claimed production result is included.
