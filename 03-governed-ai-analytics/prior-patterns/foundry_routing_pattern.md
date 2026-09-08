# Foundry Routing Pattern

Classification: `sanitized_derivative`

Production status: unverified prior orchestration pattern

## Pattern

```text
classify request
    |
    +-- semantic data required --> retrieve authorized context
    |                                  |
    +-- direct explanation ------------+
                                       v
                              construct evidence prompt
                                       |
                                       v
                              answer with source metadata
```

The useful recovered idea was separation of deterministic route selection,
backend retrieval, context construction, and final explanation. Private endpoint
labels and unverified Azure SDK calls are intentionally omitted.

## Required Corrections

- Route through schema-validated enums rather than substring inspection.
- Fail closed when routing, authorization, or retrieval fails.
- Use one async client model and pin the corresponding SDK versions.
- Treat retrieved content as untrusted data, not model instructions.
- Return typed citations and tool metadata instead of inserting raw payloads.
- Log correlation IDs and outcome classes, not prompts or operational data.

This pattern is not evidence of a deployed agent, web application, Teams bot,
identity flow, or production service.
