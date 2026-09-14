# Architecture

Classification: `reconstructed_from_context`

```text
host + parent item + component BOM ---- component time standards
                  |                                  |
                  +-> effort + coverage/model status-+
                                   |
                         recovered rack/container
                                   |
                  complexity band + synthetic rate
                                   |
versioned forecast by period + model + recovery form
                  |                                  |
                  v                                  v
 stage/workstation/department scenario      unit-economics rows
                  |                                  |
       selected plan version                         |
                  |                                  |
 identifier/model routing -> exception audit         |
                  |                                  |
 workstation host/minute capacities                  |
                  |                                  |
      scheduled/unscheduled result ------------------+
                  |
 same-grain quantity/headcount actuals
```

Authoritative arithmetic belongs in deterministic transformations. Forecasts,
assumptions, synthetic rates, and version keys travel with every scenario so a
result can be reproduced and reviewed independently of any narrative layer.

## Grain And Controls

| Transformation | Input grain | Preserved control |
| --- | --- | --- |
| BOM effort | host, parent item, model, recovery form, component | component-standard coverage and model status |
| Forecast economics | forecast version, period, model, recovery form | one output per forecast row and additive reconciliation |
| Labor capacity | scenario, period, stage, workstation, labor department | positive productive capacity and workload additive only within scenario |
| Plan versus actual | plan version plus the labor-capacity grain | explicit missing-actual status; no cross-version multiplication |
| Routing and scheduling | recovery item, identifier/model, workstation | first-match audit, exceptions, per-day capacities, and input conservation |

The entity relationships and processing controls are recovered patterns expressed
as sanitized derivatives. The architecture and all values shown here are a
corrected reconstruction; they do not assert an exact deployed topology,
production configuration, or realized numeric outcome.
