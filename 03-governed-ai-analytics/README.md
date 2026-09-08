# Governed AI Analytics

Case study: [Turning analyst requests into governed, self-service answers](https://paulymurph.com/work/governed-ai-analytics)

This folder illustrates the boundary between conversational orchestration and
governed analytics. Recovered evidence covered early Foundry/Fabric patterns and
domain-grounding rules, but not the complete web, Teams, MCP, identity,
deployment, or monitoring implementation described by the case study.

## Evidence

| File | Classification | What it demonstrates |
| --- | --- | --- |
| [`foundry_routing_pattern.md`](prior-patterns/foundry_routing_pattern.md) | `sanitized_derivative` | Route, retrieve, and explain orchestration without copying unverified SDK calls |
| [`fabric_agent_adapter_pattern.md`](prior-patterns/fabric_agent_adapter_pattern.md) | `sanitized_derivative` | A narrow semantic-agent adapter boundary with identity and evidence requirements |
| [`planning_grounding_rules.md`](prior-patterns/planning_grounding_rules.md) | `sanitized_derivative` | Grain, field precedence, anti-double-counting, and response constraints |
| [`intent_and_query_pattern.md`](prior-patterns/intent_and_query_pattern.md) | `sanitized_derivative` | Structured analytical intent separated from allowlisted query execution |
| [`analytics_tools.reconstructed.yaml`](contracts/analytics_tools.reconstructed.yaml) | `reconstructed_from_context` | Human-readable semantic-query and deterministic-calculation interface design |
| [`answer_evidence.mock.schema.json`](contracts/answer_evidence.mock.schema.json) | `synthetic_portfolio_example` | An answer envelope carrying citations, assumptions, warnings, trace, and approval state |
| [`channel_responses.mock.json`](mockups/channel_responses.mock.json) | `synthetic_portfolio_example` | One synthetic evidence envelope rendered through web and Teams channels |

## Coverage Boundary

This folder is architecture evidence, not a recovered production service. It
does not claim that the examples authenticate through Entra, invoke a live
Fabric agent, expose a deployed MCP server, enforce RLS, run in Container Apps,
or emit Azure Monitor telemetry. Those elements are shown only in the
reconstructed target architecture.
