# Governed AI Analytics

Case study: [Turning analyst requests into governed, self-service answers](https://paulymurph.com/work/governed-ai-analytics)

This folder illustrates the boundary between conversational orchestration and
governed analytics. The source evidence preserved prior Foundry agent routing,
a Fabric data-agent adapter, intent/query routing, and planning-grounding
patterns. The documents identify defects in those patterns and clearly label
the safer corrections reconstructed for this portfolio.

## Evidence Key

- `sanitized_derivative`: a generalized prior pattern with sensitive and
  unverifiable implementation detail removed. Each document distinguishes the
  recovered idea, known risks, reconstructed correction, and missing work.
- `reconstructed_from_context`: a proposed contract or architecture inferred
  from the available patterns. It is design evidence, not recovered code.
- `synthetic_portfolio_example`: invented values and presentation shapes used
  only to exercise the reconstructed contract.

## Evidence

| File | Classification | What it demonstrates |
| --- | --- | --- |
| [`foundry_routing_pattern.md`](prior-patterns/foundry_routing_pattern.md) | `sanitized_derivative` | Foundry agent orchestration stages, route ambiguity, and fail-closed corrections |
| [`fabric_agent_adapter_pattern.md`](prior-patterns/fabric_agent_adapter_pattern.md) | `sanitized_derivative` | Fabric data-agent adapter boundary, typed normalization, identity context, and failure mapping |
| [`planning_grounding_rules.md`](prior-patterns/planning_grounding_rules.md) | `sanitized_derivative` | Planning entities, measures, time grains, field precedence, and anti-double-counting rules |
| [`intent_and_query_pattern.md`](prior-patterns/intent_and_query_pattern.md) | `sanitized_derivative` | Structured intent, ambiguity handling, and allowlisted query-plan compilation |
| [`analytics_tools.reconstructed.yaml`](contracts/analytics_tools.reconstructed.yaml) | `reconstructed_from_context` | Human-readable route and tool contracts with trusted-context boundaries and failure codes |
| [`answer_evidence.mock.schema.json`](contracts/answer_evidence.mock.schema.json) | `synthetic_portfolio_example` | A machine-checkable synthetic answer envelope with query context, tool evidence, warnings, audit, and approval state |
| [`channel_responses.mock.json`](mockups/channel_responses.mock.json) | `synthetic_portfolio_example` | One invented envelope plus hypothetical channel presentation bindings |

## Pattern Flow

1. Parse the request into a typed intent: route, entity, measures, dimensions,
   filters, and time grain.
2. Ask a clarifying question when a material entity, period, grain, unit, or
   comparison is missing; do not guess it from conversational wording.
3. Apply coarse authorization before routing and argument-level authorization
   immediately before an allowlisted tool call.
4. Use the Fabric adapter only for descriptive semantic queries. Use a
   deterministic calculation tool for scenario arithmetic.
5. Normalize successful and failed calls into an evidence envelope, then apply
   classification, redaction, approval, and export policy outside the model.
6. Record minimal audit events keyed by an opaque correlation reference; do not
   record raw prompts, result rows, credentials, or identity tokens.

## Coverage Boundary

This folder is architecture evidence, not a recovered production service. No
MCP or FastMCP implementation, Teams integration, Entra runtime, semantic-model
file, web application, deployed service, live Fabric invocation, data-layer
security configuration, or monitoring integration was recovered or verified.
Channel bindings are mockups, and identity, audit, authorization, export, and
telemetry behavior are reconstructed requirements whose implementation remains
absent.
