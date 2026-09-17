/*
Classification: sanitized_derivative
Evidence status: corrected and generalized Gold SQL pattern

Grain: one row per (facility_code, storage_location, container_id) in the latest
eligible snapshot. Movement history supplies backlog-entry context but never
replaces snapshot state. Use a bound @as_of_date for reproducibility.
*/

WITH latest_snapshot_date AS (
    SELECT MAX(snapshot_date) AS snapshot_date
    FROM silver.inventory_snapshot
    WHERE snapshot_date <= CAST(@as_of_date AS date)
),
latest_inventory AS (
    SELECT
        i.facility_code,
        i.storage_location,
        i.container_id,
        i.received_date,
        i.current_state,
        i.quantity_units,
        ROW_NUMBER() OVER (
            PARTITION BY i.facility_code, i.storage_location, i.container_id
            ORDER BY i.updated_ts DESC, i._source_id DESC, i._source_row_number DESC
        ) AS row_number
    FROM silver.inventory_snapshot AS i
    INNER JOIN latest_snapshot_date AS d ON d.snapshot_date = i.snapshot_date
),
canonical_inventory AS (
    SELECT *
    FROM latest_inventory
    WHERE row_number = 1
),
movement_events AS (
    SELECT
        m.facility_code,
        m.container_id,
        m.movement_ts,
        p.enters_backlog,
        p.exits_backlog
    FROM silver.inventory_movements AS m
    INNER JOIN reference.movement_policy AS p ON p.movement_type = m.movement_type
    WHERE m.movement_ts < DATEADD(DAY, 1, CAST(@as_of_date AS datetime2))
),
movement_bounds AS (
    SELECT
        facility_code,
        container_id,
        MAX(CASE WHEN exits_backlog = 1 THEN movement_ts END) AS latest_exit_ts,
        MAX(movement_ts) AS latest_movement_ts
    FROM movement_events
    GROUP BY facility_code, container_id
),
movement_context AS (
    SELECT
        e.facility_code,
        e.container_id,
        MIN(CASE WHEN e.enters_backlog = 1
                  AND (b.latest_exit_ts IS NULL OR e.movement_ts > b.latest_exit_ts)
                 THEN e.movement_ts END) AS backlog_entered_ts,
        b.latest_movement_ts
    FROM movement_events AS e
    INNER JOIN movement_bounds AS b
      ON b.facility_code = e.facility_code AND b.container_id = e.container_id
    GROUP BY e.facility_code, e.container_id, b.latest_movement_ts
)
SELECT
    CAST(@as_of_date AS date) AS as_of_date,
    i.facility_code,
    i.storage_location,
    i.container_id,
    i.current_state,
    i.quantity_units,
    received_date,
    m.backlog_entered_ts,
    m.latest_movement_ts,
    DATEDIFF(DAY, CAST(COALESCE(m.backlog_entered_ts, i.received_date) AS date),
             CAST(@as_of_date AS date)) AS backlog_age_days,
    CASE
        WHEN DATEDIFF(DAY, CAST(COALESCE(m.backlog_entered_ts, i.received_date) AS date),
                      CAST(@as_of_date AS date)) <= 2 THEN '00-02'
        WHEN DATEDIFF(DAY, CAST(COALESCE(m.backlog_entered_ts, i.received_date) AS date),
                      CAST(@as_of_date AS date)) <= 7 THEN '03-07'
        WHEN DATEDIFF(DAY, CAST(COALESCE(m.backlog_entered_ts, i.received_date) AS date),
                      CAST(@as_of_date AS date)) <= 14 THEN '08-14'
        ELSE '15+'
    END AS backlog_age_band
FROM canonical_inventory AS i
LEFT JOIN movement_context AS m
  ON m.facility_code = i.facility_code AND m.container_id = i.container_id
WHERE i.received_date IS NOT NULL
  AND i.received_date <= CAST(@as_of_date AS date)
  AND i.current_state IN ('AWAITING_PROCESSING', 'IN_PROCESS', 'RECOVERY_HOLD');
