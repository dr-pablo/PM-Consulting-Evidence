# Fabric Agent Adapter Pattern

Classification: `sanitized_derivative`

Evidence status: recovered adapter concept; SDK invocation and runtime unverified

## Recovered Prior Pattern

```python
class SemanticQueryAdapter:
    async def query(self, request, actor_context):
        result = await data_agent.execute(request)
        return normalize(result)
```

The useful recovered idea was a narrow adapter isolating service-specific
invocation from orchestration. The exact client, method names, request shape,
and response shape were not sufficiently verified and are pseudocode here.

## Known Defects And Risks

- Passing natural language directly through the adapter could bypass entity,
  measure, filter, and time-grain allowlists.
- The prior shape did not establish whether caller identity, service identity,
  or authorization scope reached the data layer.
- Evidence fields, truncation, source-version drift, cancellation, retries, and
  stable error mapping were incomplete or absent.
- Retrying a denied or invalid request could leak policy behavior; retrying an
  unbounded query could amplify load.
- Returning provider-native payloads would couple the orchestrator to an
  unpinned SDK and risk exposing fields outside the requested projection.

## Reconstructed Correction

```python
class SemanticQueryAdapter:
    async def query(self, request, trusted_context):
        validated = validate_semantic_query(request)
        authorize_entity_and_arguments(trusted_context, validated)
        provider_result = await invoke_with_timeout(validated, trusted_context)
        return normalize_allowlisted_result(provider_result)
```

`request` contains only `planning_inventory`, approved descriptive measures,
approved dimensions/filters, an explicit time grain, and a bounded row limit.
`trusted_context` is broker-supplied and contains opaque actor, tenant,
authorization-scope, and correlation references; model output cannot populate
or modify it. The normalized result is one of:

- `succeeded`: rows, semantic source version, measure references, warnings,
  applied time grain, and truncation state.
- `partial`: the same shape with an incompleteness warning; never represented as
  a complete answer.
- `denied`, `invalid_request`, `timeout`, `upstream_unavailable`, or
  `source_version_mismatch`: code and safe message only, with no rows.

Only transient upstream outcomes are candidates for bounded retries. Identity
tokens, provider exception text, and raw result rows are excluded from audit
events. Contract tests would need to pin one supported SDK generation and test
cancellation, limits, type normalization, warning propagation, and error maps.

## Implementation Still Absent

No original endpoint, agent ID, user query, exception text, or physical data
object is reproduced here. No live Fabric data agent, semantic-model file,
identity runtime, adapter implementation, or verified invocation outcome is
present in this evidence set.
