/*
Classification: sanitized_derivative
Production status: generalized weekly reporting pattern

Calendar-first aggregation preserves zero-activity workdays and makes target
units explicit before weekly comparison.
*/

WITH workdays AS (
    SELECT calendar_date, week_start
    FROM reference.calendar
    WHERE is_workday = 1
      AND calendar_date <= CAST(@as_of_date AS date)
),
event_dates AS (
    SELECT
        asset_id,
        MIN(CASE WHEN event_type = 'RECEIVED' THEN CAST(event_ts AS date) END) AS received_date,
        MIN(CASE WHEN event_type = 'COMPLETE' THEN CAST(event_ts AS date) END) AS completed_date
    FROM silver.asset_events
    GROUP BY asset_id
),
daily_activity AS (
    SELECT
        w.calendar_date,
        w.week_start,
        COUNT(DISTINCT r.asset_id) AS received_units,
        COUNT(DISTINCT c.asset_id) AS completed_units
    FROM workdays AS w
    LEFT JOIN event_dates AS r ON r.received_date = w.calendar_date
    LEFT JOIN event_dates AS c ON c.completed_date = w.calendar_date
    GROUP BY w.calendar_date, w.week_start
),
weekly_activity AS (
    SELECT
        week_start,
        COUNT(*) AS workday_count,
        SUM(received_units) AS received_units,
        SUM(completed_units) AS completed_units,
        AVG(CAST(completed_units AS decimal(18, 2))) AS average_completed_per_workday
    FROM daily_activity
    GROUP BY week_start
),
weekly_targets AS (
    SELECT
        t.week_start,
        t.daily_target * w.workday_count AS weekly_target
    FROM planning.production_targets AS t
    INNER JOIN (
        SELECT week_start, COUNT(*) AS workday_count
        FROM workdays
        GROUP BY week_start
    ) AS w ON w.week_start = t.week_start
)
SELECT
    a.week_start,
    a.workday_count,
    a.received_units,
    a.completed_units,
    a.average_completed_per_workday,
    t.weekly_target,
    a.completed_units - t.weekly_target AS variance_to_target
FROM weekly_activity AS a
LEFT JOIN weekly_targets AS t ON t.week_start = a.week_start;
