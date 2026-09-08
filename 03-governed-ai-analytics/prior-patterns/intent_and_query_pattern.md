# Intent and Query Pattern

Classification: `sanitized_derivative`

Production status: generalized request-to-query design evidence

## Structured Intent

```json
{
  "schema_version": "1.0",
  "route": "semantic_query",
  "entity": "planning_inventory",
  "filters": [
    {"field": "is_ready", "operator": "equals", "value": true}
  ],
  "measures": ["inventory_count", "average_complexity_score"],
  "group_by": ["equipment_category"],
  "limit": 100
}
```

## Safe Compilation Boundary

```sql
SELECT
    equipment_category,
    COUNT(DISTINCT asset_group_id) AS inventory_count,
    AVG(complexity_score) AS average_complexity_score
FROM governed.PlanningInventory
WHERE is_ready = 1
GROUP BY equipment_category;
```

The request is validated against allowlisted entities, fields, filters, and
measures before execution. Authorization predicates and semantic-model security
remain outside model control. The recovered query example did not fully match
its requested metrics; this derivative makes that contract explicit.
