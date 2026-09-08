"""Separate current-state snapshot publication from keyed Delta upserts.

Classification: sanitized_derivative
Production status: corrected and generalized PySpark/Delta design extract
"""

from delta.tables import DeltaTable
from pyspark.sql import DataFrame, Window, functions as F


def validate_required_keys(frame: DataFrame, keys: list[str]) -> DataFrame:
    missing = sorted(set(keys) - set(frame.columns))
    if missing:
        raise ValueError(f"Missing required keys: {missing}")
    null_condition = F.lit(False)
    for key in keys:
        null_condition = null_condition | F.col(key).isNull()
    if frame.filter(null_condition).limit(1).count():
        raise ValueError("Null business keys must be quarantined before merge")
    return frame


def latest_records(
    frame: DataFrame,
    keys: list[str],
    event_ts: str = "event_ts",
    source_id: str = "_source_id",
    source_row_number: str = "_source_row_number",
) -> DataFrame:
    """Choose one deterministic latest record at the declared business-key grain."""
    validate_required_keys(frame, keys + [event_ts, source_id, source_row_number])
    order = Window.partitionBy(*keys).orderBy(
        F.col(event_ts).desc(),
        F.col(source_id).desc(),
        F.col(source_row_number).desc(),
    )
    return frame.withColumn("_row_number", F.row_number().over(order)).filter(
        F.col("_row_number") == 1
    ).drop("_row_number")


def upsert_delta(
    source: DataFrame,
    target_path: str,
    keys: list[str],
    event_ts: str = "event_ts",
    source_id: str = "_source_id",
    source_row_number: str = "_source_row_number",
) -> None:
    """Merge a validated incremental batch into an existing Silver table."""
    source = latest_records(source, keys, event_ts, source_id, source_row_number)
    if not DeltaTable.isDeltaTable(source.sparkSession, target_path):
        source.write.format("delta").mode("overwrite").save(target_path)
        return
    condition = " AND ".join(f"target.`{key}` = source.`{key}`" for key in keys)
    source_is_newer = (
        f"source.`{event_ts}` > target.`{event_ts}` OR "
        f"(source.`{event_ts}` = target.`{event_ts}` "
        f"AND (source.`{source_id}` > target.`{source_id}` OR "
        f"(source.`{source_id}` = target.`{source_id}` "
        f"AND source.`{source_row_number}` > target.`{source_row_number}`)))"
    )
    (
        DeltaTable.forPath(source.sparkSession, target_path)
        .alias("target")
        .merge(source.alias("source"), condition)
        .whenMatchedUpdateAll(condition=source_is_newer)
        .whenNotMatchedInsertAll()
        .execute()
    )


def publish_current_snapshot(
    source: DataFrame,
    target_path: str,
    keys: list[str],
    expected_row_count: int,
    snapshot_date: str = "snapshot_date",
) -> None:
    """Publish only the latest snapshot when the contract is current state."""
    latest = source.select(F.max(snapshot_date).alias("value")).first()["value"]
    if latest is None:
        raise ValueError("Snapshot batch contains no valid snapshot date")
    if DeltaTable.isDeltaTable(source.sparkSession, target_path):
        existing_latest = (
            source.sparkSession.read.format("delta")
            .load(target_path)
            .select(F.max(snapshot_date).alias("value"))
            .first()["value"]
        )
        if existing_latest is not None and latest < existing_latest:
            raise ValueError("Incoming snapshot is older than the published current state")
    current = source.filter(F.col(snapshot_date) == F.lit(latest))
    validate_required_keys(current, keys)
    actual_row_count = current.count()
    unique_row_count = current.select(*keys).distinct().count()
    if actual_row_count != expected_row_count or unique_row_count != expected_row_count:
        raise ValueError("Snapshot completeness or key-uniqueness check failed")
    current.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save(
        target_path
    )
