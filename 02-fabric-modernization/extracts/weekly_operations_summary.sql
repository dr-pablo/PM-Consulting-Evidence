/*
Classification: sanitized_derivative
Production status: generalized weekly reporting pattern

Calendar-first WBR aggregation preserves zero-activity reporting weeks and the
workday denominator. Publication requires every declared dependency to be ready.
*/

WITH required_dependencies AS (
    SELECT dependency_name
    FROM (VALUES
        ('inventory_current'), ('inventory_movements'), ('container_events'),
        ('component_recovery_events'), ('business_calendar'), ('target_plan')
    ) AS required(dependency_name)
),
dependency_gate AS (
    SELECT CASE WHEN COUNT(*) = SUM(CASE WHEN s.is_ready = 1 THEN 1 ELSE 0 END)
                THEN 1 ELSE 0 END AS is_ready
    FROM required_dependencies AS r
    LEFT JOIN reporting.dependency_status AS s
      ON s.dependency_name = r.dependency_name
     AND s.reporting_date = CAST(@as_of_date AS date)
),
reporting_dates AS (
    SELECT calendar_date, week_start
    FROM reference.calendar
    WHERE calendar_date <= CAST(@as_of_date AS date)
),
workdays AS (
    SELECT calendar_date, week_start
    FROM reference.calendar
    WHERE is_workday = 1
      AND calendar_date <= CAST(@as_of_date AS date)
),
weekly_calendar AS (
    SELECT week_start, COUNT(*) AS workday_count
    FROM workdays
    GROUP BY week_start
),
terminal_events AS (
    SELECT
        facility_code,
        container_id,
        processing_cycle_id,
        MIN(CAST(event_ts AS date)) AS completed_date
    FROM silver.container_events AS e
    INNER JOIN reference.container_event_policy AS p ON p.event_type = e.event_type
    WHERE p.is_terminal_event = 1
    GROUP BY facility_code, container_id, processing_cycle_id
),
weekly_completions AS (
    SELECT week_start, COUNT(*) AS completed_containers
    FROM (
        SELECT DISTINCT d.week_start, e.facility_code, e.container_id
        FROM terminal_events AS e
        INNER JOIN reporting_dates AS d ON d.calendar_date = e.completed_date
    ) AS completed
    GROUP BY week_start
),
weekly_receipts AS (
    SELECT week_start, COUNT(*) AS received_containers
    FROM (
        SELECT DISTINCT d.week_start, m.facility_code, m.container_id
        FROM silver.inventory_movements AS m
        INNER JOIN reference.movement_policy AS p ON p.movement_type = m.movement_type
        INNER JOIN reporting_dates AS d ON d.calendar_date = CAST(m.movement_ts AS date)
        WHERE p.enters_backlog = 1
    ) AS received
    GROUP BY week_start
),
weekly_activity AS (
    SELECT
        w.week_start,
        w.workday_count,
        COALESCE(r.received_containers, 0) AS received_containers,
        COALESCE(c.completed_containers, 0) AS completed_containers,
        CAST(COALESCE(c.completed_containers, 0) AS decimal(18, 2))
            / NULLIF(w.workday_count, 0) AS average_completed_per_workday
    FROM weekly_calendar AS w
    LEFT JOIN weekly_receipts AS r ON r.week_start = w.week_start
    LEFT JOIN weekly_completions AS c ON c.week_start = w.week_start
),
weekly_targets AS (
    SELECT
        t.week_start,
        t.daily_target * w.workday_count AS weekly_target
    FROM planning.production_targets AS t
    INNER JOIN weekly_calendar AS w ON w.week_start = t.week_start
),
weekly_backlog AS (
    SELECT
        w.week_start,
        COUNT(a.container_id) AS ending_backlog,
        SUM(CASE WHEN a.backlog_age_days > 7 THEN 1 ELSE 0 END) AS backlog_over_7_days
    FROM (
        SELECT DISTINCT
            week_start,
            CASE
                WHEN DATEADD(DAY, 6, week_start) > CAST(@as_of_date AS date)
                    THEN CAST(@as_of_date AS date)
                ELSE DATEADD(DAY, 6, week_start)
            END AS backlog_as_of_date
        FROM workdays
    ) AS w
    LEFT JOIN gold.inventory_aging AS a ON a.as_of_date = w.backlog_as_of_date
    GROUP BY w.week_start
),
wbr AS (
    SELECT
        a.*,
        b.ending_backlog,
        b.backlog_over_7_days,
        t.weekly_target,
        SUM(a.completed_containers) OVER (
            ORDER BY a.week_start ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
        ) AS rolling_4_week_completed,
        AVG(CAST(a.completed_containers AS decimal(18, 2))) OVER (
            ORDER BY a.week_start ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
        ) AS rolling_4_week_average
    FROM weekly_activity AS a
    LEFT JOIN weekly_backlog AS b ON b.week_start = a.week_start
    LEFT JOIN weekly_targets AS t ON t.week_start = a.week_start
)
SELECT
    a.week_start,
    a.workday_count,
    a.received_containers,
    a.completed_containers,
    a.average_completed_per_workday,
    a.ending_backlog,
    a.backlog_over_7_days,
    a.weekly_target,
    a.completed_containers - a.weekly_target AS variance_to_target,
    a.rolling_4_week_completed,
    a.rolling_4_week_average
FROM wbr AS a
CROSS JOIN dependency_gate AS g
WHERE g.is_ready = 1;
