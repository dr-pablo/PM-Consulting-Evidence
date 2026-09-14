# Governed Analytics Architecture

Classification: `reconstructed_from_context`

Status: reconstructed target design; implementation and deployment are not
present in this evidence set.

```text
hypothetical channel
        |
        v
trusted broker boundary ----> authenticate + coarse authorize
        |                      attach opaque actor, tenant, scope, correlation
        v
intent parser ------------ ambiguous/materially incomplete? --> clarification
        |
        +-- direct_explanation --> approved reference context
        |
        +-- semantic_query -----> Fabric data-agent adapter
        |                         descriptive measures only
        |
        +-- calculation --------> deterministic planning tool
                                  versioned inputs and arithmetic trace
        |
        v
evidence normalizer --> classification/redaction --> approval/export policy
        |
        +--> channel-neutral answer envelope
        +--> minimal, redacted audit events
```

The labels describe responsibilities, not recovered services, SDK objects, or
infrastructure coordinates. In particular, the diagram does not assert an
implemented channel, identity provider, Fabric agent, or tool protocol.

## Typed Boundaries

| Boundary | Model may propose | Trusted code must enforce |
| --- | --- | --- |
| Intent | Route and structured analytical arguments | Enum/schema validation, ambiguity threshold, and allowed transitions |
| Authorization | Nothing | Actor/tenant context, entity permission, filter scope, and export permission |
| Semantic query | Entity, measures, dimensions, filters, time grain, row limit | Allowlists, operator/value types, semantic security, timeout, and row/size limits |
| Calculation | Scenario inputs and requested calculation | Units, ranges, assumption versions, formulas, rounding, and trace |
| Evidence | Plain-language synthesis | Source/measure references, classification ceiling, redaction, and warning propagation |
| Export | Requested format | Trusted request binding, authorization recheck, audience, expiry, and revocation |

## Design Boundaries

- Coarse authorization occurs before routing and argument-level authorization is
  repeated immediately before every tool execution; the model never grants access.
- Semantic queries use approved entities and measures rather than arbitrary physical SQL.
- Consequential calculations execute in deterministic tools, not in model prose.
- Tool results carry status, source version, assumptions, warnings, and a
  calculation trace where arithmetic occurred.
- Downloads are bound to actor, tenant, authorization scope, and expiry rather
  than trusting a caller-supplied request identifier.
- Audit events distinguish request receipt, authorization decision, route,
  tool outcome, redaction, approval, and export without storing raw prompts,
  tokens, result rows, or generated files.
- Higher-impact recommendations carry an explicit human-approval state.

## Failure Behavior

- Unknown or conflicting intent returns `clarification_required`; it does not
  silently fall through to a broad query.
- Invalid fields, measures, operators, time grains, and limits are rejected
  before invocation.
- Denied authorization returns no result rows and is not retried by the model.
- Timeout and transient upstream failures may be retried only by trusted code
  under a bounded policy; partial results are marked incomplete.
- Source-version drift, incompatible grains, stale periods, truncation, and
  suppressed values become explicit warnings or block the answer when material.
- A calculation failure cannot be replaced with arithmetic improvised in prose.
- Redaction or approval failure prevents export and may replace the answer with
  a policy-safe response.

## Implementation Gap

The contracts and mockup in this folder illustrate these boundaries. Broker,
identity runtime, data-agent invocation, deterministic calculation engine,
audit sink, approval workflow, export service, channel integrations, semantic
model artifacts, and deployment configuration remain absent and unverified.
