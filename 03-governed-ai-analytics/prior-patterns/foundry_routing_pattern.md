# Foundry Routing Pattern

Classification: `sanitized_derivative`

Evidence status: recovered prior orchestration pattern; runtime unverified

## Recovered Prior Pattern

```text
classify request
    |
    +-- semantic data required --> retrieve data context
    |                                  |
    +-- direct explanation ------------+
                                       v
                              construct evidence prompt
                                       |
                                       v
                              answer with source metadata
```

The recoverable idea was separation of route selection, backend retrieval,
context construction, and final explanation. It also distinguished a
data-backed route from a direct explanatory route. Private labels, identifiers,
endpoint details, and unverified SDK calls are intentionally omitted.

## Known Defects And Risks

- Route selection appeared dependent on free text rather than a closed enum, so
  overlapping planning language could select the wrong branch.
- Retrieval and answer generation did not expose a durable typed boundary for
  measures, dimensions, filters, time grain, or result provenance.
- Authorization, prompt-injection treatment, timeout behavior, and partial
  result handling were not demonstrably enforced by the recovered pattern.
- A failed data route could plausibly degrade into an unsupported explanation
  unless failure states were made explicit.
- The available material did not establish compatible async clients, pinned SDK
  versions, or end-to-end audit behavior.

## Reconstructed Correction

Use a schema-validated decision with these routes:

| Route | Required condition | Next boundary |
| --- | --- | --- |
| `direct_explanation` | No current governed measure or scenario arithmetic is needed | Approved reference context only |
| `semantic_query` | Descriptive facts are requested and entity, measure, and period are resolved | Fabric data-agent adapter |
| `calculation` | Scenario arithmetic is requested and required inputs/versions are resolved | Deterministic tool |
| `clarification_required` | A material term, period, grain, unit, or comparison is missing/conflicting | No data tool call |

The trusted broker attaches opaque actor, tenant, authorization-scope, and
correlation references. The model cannot create or widen those values. Retrieved
text is delimited as untrusted data, and only normalized typed results enter the
answer context.

## Required Controls

- Fail closed when routing, authorization, or retrieval fails.
- Validate route transitions and every tool argument against an allowlist.
- Use one client concurrency model and pin the selected SDK generation before implementation.
- Treat retrieved content as untrusted data, not model instructions.
- Return typed citations and tool metadata instead of inserting raw payloads.
- Record route, policy version, tool status, latency class, and warning codes
  against an opaque correlation reference, not prompts or operational rows.
- Preserve `denied`, `invalid_request`, `timeout`, `upstream_unavailable`,
  `partial`, and `source_version_mismatch` as distinct outcomes.

## Implementation Still Absent

No recovered code demonstrates the corrected router, Foundry agent runtime,
identity flow, live retrieval, audit sink, channel integration, deployment, or
production service. This document is not evidence of any of those outcomes.
