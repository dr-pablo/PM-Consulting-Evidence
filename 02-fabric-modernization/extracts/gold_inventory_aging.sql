/*
Classification: sanitized_derivative
Production status: corrected and generalized Gold SQL pattern

The latest snapshot is isolated before enrichment to preserve one row per asset.
Use a bound @as_of_date in production so results remain reproducible.
*/

WITH latest_snapshot_date AS (
    SELECT MAX(snapshot_date) AS snapshot_date
    FROM silver.inventory_snapshot
    WHERE snapshot_date <= CAST(@as_of_date AS date)
),
latest_inventory AS (
    SELECT
        i.asset_id,
        i.received_date,
        i.closed_date,
        i.product_family,
        i.storage_area,
        ROW_NUMBER() OVER (
            PARTITION BY i.asset_id
            ORDER BY i.updated_ts DESC, i.source_record_id DESC
        ) AS row_number
    FROM silver.inventory_snapshot AS i
    INNER JOIN latest_snapshot_date AS d ON d.snapshot_date = i.snapshot_date
),
canonical_inventory AS (
    SELECT *
    FROM latest_inventory
    WHERE row_number = 1
)
SELECT
    asset_id,
    product_family,
    storage_area,
    received_date,
    CASE
        WHEN closed_date <= CAST(@as_of_date AS date) THEN closed_date
        ELSE NULL
    END AS closed_date,
    CASE
        WHEN closed_date <= CAST(@as_of_date AS date) THEN 'CLOSED'
        ELSE 'OPEN'
    END AS inventory_status,
    DATEDIFF(
        DAY,
        received_date,
        CASE
            WHEN closed_date <= CAST(@as_of_date AS date) THEN closed_date
            ELSE CAST(@as_of_date AS date)
        END
    ) AS age_days
FROM canonical_inventory
WHERE received_date IS NOT NULL
  AND received_date <= CAST(@as_of_date AS date);
