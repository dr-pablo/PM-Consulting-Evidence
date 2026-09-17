/*
Classification: sanitized_derivative
Evidence status: generalized Gold SQL pattern with synthetic entities

Grain: one row per operational cycle. Container processing is keyed by
(facility_code, rack_id, container_id, processing_cycle_id); component recovery
is keyed by (facility_code, host_id, component_id, recovery_cycle_id).
*/

WITH container_events AS (
    SELECT
        'CONTAINER_PROCESSING' AS process_stream,
        e.facility_code,
        e.rack_id AS parent_unit_id,
        e.container_id AS child_unit_id,
        e.processing_cycle_id AS process_cycle_id,
        e.event_ts,
        e.event_sequence,
        p.is_start_event,
        p.is_terminal_event,
        p.resulting_status,
        e._source_id
    FROM silver.container_events AS e
    INNER JOIN reference.container_event_policy AS p ON p.event_type = e.event_type
),
recovery_events AS (
    SELECT
        'COMPONENT_RECOVERY' AS process_stream,
        e.facility_code,
        e.host_id AS parent_unit_id,
        e.component_id AS child_unit_id,
        e.recovery_cycle_id AS process_cycle_id,
        e.event_ts,
        e.event_sequence,
        p.is_start_event,
        p.is_terminal_event,
        p.resulting_status,
        e._source_id
    FROM silver.component_recovery_events AS e
    INNER JOIN reference.recovery_event_policy AS p ON p.event_type = e.event_type
),
all_events AS (
    SELECT * FROM container_events
    UNION ALL
    SELECT * FROM recovery_events
),
ranked_events AS (
    SELECT
        e.*,
        ROW_NUMBER() OVER (
            PARTITION BY process_stream, facility_code, parent_unit_id,
                         child_unit_id, process_cycle_id
            ORDER BY event_ts DESC, event_sequence DESC, _source_id DESC
        ) AS latest_event_number
    FROM all_events AS e
),
cycle_milestones AS (
    SELECT
        process_stream,
        facility_code,
        parent_unit_id,
        child_unit_id,
        process_cycle_id,
        MIN(CASE WHEN is_start_event = 1 THEN event_ts END) AS started_ts,
        MAX(CASE WHEN is_terminal_event = 1 THEN event_ts END) AS terminal_ts,
        MAX(CASE WHEN latest_event_number = 1 THEN resulting_status END) AS cycle_status,
        COUNT(*) AS event_count
    FROM ranked_events
    GROUP BY process_stream, facility_code, parent_unit_id, child_unit_id, process_cycle_id
)
SELECT
    process_stream,
    facility_code,
    parent_unit_id,
    child_unit_id,
    process_cycle_id,
    started_ts,
    terminal_ts,
    cycle_status,
    DATEDIFF(MINUTE, started_ts, terminal_ts) AS elapsed_minutes,
    event_count
FROM cycle_milestones;
