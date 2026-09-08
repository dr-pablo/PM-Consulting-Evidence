# Governed Analytics Architecture

Classification: `reconstructed_from_context`

```text
web client --------------------\
                                > identity provider
Teams channel -----------------/         |
                                          v
                              authorized API broker
                         policy + correlation context
                                          |
                                          v
                                 model orchestrator
                               /                    \
                    semantic query              typed tools
                  descriptive analytics    deterministic calculations
                          |                         |
                    governed model          versioned assumptions
                               \                    /
                                evidence envelope
                                       |
                           answer + authorized export
                                       |
                         redacted operational telemetry
```

## Design Boundaries

- Coarse authorization occurs before routing and argument-level authorization is
  repeated immediately before every tool execution; the model never grants access.
- Semantic queries use approved entities and measures rather than arbitrary physical SQL.
- Consequential calculations execute in deterministic tools, not in model prose.
- Tool results carry source version, assumptions, warnings, and calculation trace.
- Downloads are bound to actor, tenant, authorization scope, and expiry rather
  than trusting a caller-supplied request identifier.
- Telemetry records correlation and outcome metadata without raw prompts or payloads.
- Higher-impact recommendations carry an explicit human-approval state.
