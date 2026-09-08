# Architecture

Classification: `reconstructed_from_context`

```text
synthetic demand forecast
          |
          v
equipment model + component quantities ---- time standards
          |                                      |
          +------------> modeled effort <--------+
                              |
             +----------------+----------------+
             |                                 |
demand + labor assumptions          complexity band + unit rate
             |                                 |
      labor/capacity plan              contribution margin
             |                                 |
          schedule                    economic scenario
             |                                 |
             +-------- selected operating plan-+
                              |
                 quantity/headcount actuals
```

Authoritative arithmetic belongs in deterministic transformations. Forecasts,
assumptions, rates, and model versions should travel with every scenario so a
result can be reproduced and reviewed independently of any narrative layer.
