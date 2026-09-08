# Fabric Agent Adapter Pattern

Classification: `sanitized_derivative`

Production status: interface pattern; recovered SDK invocation was unverified

## Intended Boundary

```python
class SemanticQueryAdapter:
    async def query(self, request, actor_context):
        validated_request = validate_allowlisted_arguments(request)
        authorize(actor_context, validated_request)
        result = await semantic_agent.execute(validated_request)
        return {
            "result": allowlisted_fields(result),
            "semantic_model_version": result.model_version,
            "evidence": result.measure_references,
        }
```

The adapter isolates service-specific invocation from orchestration. A real
implementation must add delegated or service identity behavior, authorization,
timeouts, retries, cancellation, response normalization, evidence metadata, and
contract tests against one pinned Fabric/Foundry SDK generation.

No original endpoint, agent ID, user query, exception text, or physical data
object is reproduced here.
