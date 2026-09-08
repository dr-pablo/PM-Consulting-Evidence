/*
Classification: sanitized_derivative
Production status: generalized Gold SQL pattern with synthetic entities

Grain: one row per asset_id. Event behavior is supplied through a neutral
reference policy rather than private literals embedded in the query.
*/

WITH normalized_events AS (
    SELECT
        e.asset_id,
        e.event_ts,
        e.source_record_id,
        p.is_processing_event,
        p.is_completion_event,
        p.resulting_status,
        ROW_NUMBER() OVER (
            PARTITION BY e.asset_id
            ORDER BY e.event_ts DESC, e.source_record_id DESC
        ) AS latest_event_number
    FROM silver.asset_events AS e
    INNER JOIN reference.event_policy AS p ON p.event_type = e.event_type
),
event_bounds AS (
    SELECT
        asset_id,
        MIN(CASE WHEN is_processing_event = 1 THEN event_ts END) AS first_processing_ts,
        MAX(CASE WHEN is_completion_event = 1 THEN event_ts END) AS completion_ts,
        COUNT(*) AS event_count
    FROM normalized_events
    GROUP BY asset_id
),
latest_status AS (
    SELECT asset_id, resulting_status
    FROM normalized_events
    WHERE latest_event_number = 1
),
ranked_assets AS (
    SELECT
        a.asset_id,
        a.customer_program,
        a.product_family,
        a.received_ts,
        a.source_record_id,
        ROW_NUMBER() OVER (
            PARTITION BY a.asset_id
            ORDER BY a.updated_ts DESC, a.source_record_id DESC
        ) AS row_number
    FROM silver.assets AS a
),
canonical AS (
    SELECT
        a.asset_id,
        a.customer_program,
        a.product_family,
        a.received_ts,
        e.first_processing_ts,
        e.completion_ts,
        e.event_count,
        s.resulting_status
    FROM ranked_assets AS a
    LEFT JOIN event_bounds AS e ON e.asset_id = a.asset_id
    LEFT JOIN latest_status AS s ON s.asset_id = a.asset_id
    WHERE a.row_number = 1
)
SELECT
    asset_id,
    customer_program,
    product_family,
    received_ts,
    first_processing_ts,
    completion_ts,
    resulting_status AS processing_status,
    DATEFROMPARTS(YEAR(completion_ts), MONTH(completion_ts), 1) AS reporting_month,
    event_count
FROM canonical;
