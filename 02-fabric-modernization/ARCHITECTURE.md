# Architecture

Classification: `reconstructed_from_context`

```text
source systems and managed transfers
                 |
                 v
          staged file intake
        + manifest + batch ID
                 |
                 v
        Bronze immutable history
                 |
       +---------+----------+
       |                    |
       v                    v
keyed incremental       current snapshot
    upsert               replacement
       |                    |
       +---------+----------+
                 v
           Silver contracts
                 |
                 v
          SQL Gold models
                 |
                 v
       semantic/reporting layer
```

Lineage, file identity, required-key checks, deterministic ordering, reject
handling, and source-to-target reconciliation are explicit processing concerns.
Workspace governance and deployment controls sit around this data path but are
not represented as recovered configuration in this repository.
