"""Record immutable file identity before appending staged data to Bronze.

Classification: sanitized_derivative
Production status: generalized Fabric/Spark implementation pattern
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Callable, Iterable
from uuid import uuid4


@dataclass(frozen=True)
class SourceFile:
    dataset: str
    path: Path
    size_bytes: int
    modified_ns: int
    checksum: str

    @property
    def source_identity(self) -> str:
        identity = f"{self.dataset}|{self.checksum}"
        return sha256(identity.encode()).hexdigest()


@dataclass(frozen=True)
class DatasetSpec:
    name: str
    source_root: Path
    required_columns: tuple[str, ...]
    silver_behavior: str


DATASET_REGISTRY = (
    DatasetSpec("inventory_snapshot", Path("staged/inventory"),
                ("facility_code", "storage_location", "container_id", "snapshot_date"),
                "replace_validated_snapshot"),
    DatasetSpec("container_events", Path("staged/container-events"),
                ("facility_code", "rack_id", "container_id", "processing_cycle_id", "event_sequence"),
                "keyed_upsert"),
    DatasetSpec("component_recovery_events", Path("staged/recovery-events"),
                ("facility_code", "host_id", "component_id", "recovery_cycle_id", "event_sequence"),
                "keyed_upsert"),
    DatasetSpec("inventory_movements", Path("staged/inventory-movements"),
                ("facility_code", "movement_id", "container_id", "movement_ts"),
                "keyed_upsert"),
)


def discover_csv_files(spec: DatasetSpec) -> list[SourceFile]:
    """Discover a registered dataset and retain content-aware file identity."""
    discovered: list[SourceFile] = []
    for path in sorted(spec.source_root.rglob("*.csv")):
        stat = path.stat()
        discovered.append(
            SourceFile(
                dataset=spec.name,
                path=path,
                size_bytes=stat.st_size,
                modified_ns=stat.st_mtime_ns,
                checksum=sha256(path.read_bytes()).hexdigest(),
            )
        )
    return discovered


def discover_registered_files(registry: Iterable[DatasetSpec]) -> list[SourceFile]:
    return [source_file for spec in registry for source_file in discover_csv_files(spec)]


def build_ingestion_batch(
    files: list[SourceFile], completed_source_ids: set[str]
) -> tuple[dict[str, object], list[SourceFile]]:
    """Create lineage metadata before a transactional Bronze write."""
    new_files = [row for row in files if row.source_identity not in completed_source_ids]
    batch = {
        "batch_id": str(uuid4()),
        "discovered_at_utc": datetime.now(timezone.utc).isoformat(),
        "file_count": len(new_files),
        "files": [
            {
                "source_id": row.source_identity,
                "dataset": row.dataset,
                "file_name": row.path.name,
                "size_bytes": row.size_bytes,
                "checksum": row.checksum,
                "status": "pending",
                "reject_reason": None,
            }
            for row in new_files
        ],
        "status": "pending",
    }
    return batch, new_files


def bronze_columns(
    batch_id: str, source_file: SourceFile, source_row_number: int
) -> dict[str, object]:
    """Lineage columns attached to each ingested record."""
    return {
        "_batch_id": batch_id,
        "_source_id": source_file.source_identity,
        "_source_row_number": source_row_number,
        "_source_file": source_file.path.name,
        "_ingested_at_utc": datetime.now(timezone.utc).isoformat(),
    }


def commit_bronze_batch(
    batch: dict[str, object],
    files: list[SourceFile],
    parse_and_merge: Callable[[str, list[SourceFile]], dict[str, str]],
    set_file_statuses: Callable[[str, dict[str, str]], None],
) -> None:
    """Merge valid rows and persist per-file complete or quarantine outcomes."""
    batch_id = str(batch["batch_id"])
    set_file_statuses(batch_id, {row.source_identity: "in_progress" for row in files})
    try:
        # The callback validates headers, types, required keys, and timestamps;
        # its value is either "complete" or a bounded quarantine reason code.
        outcomes = parse_and_merge(batch_id, files)
    except Exception:
        set_file_statuses(batch_id, {row.source_identity: "failed" for row in files})
        raise
    missing = {row.source_identity for row in files} - outcomes.keys()
    if missing:
        raise ValueError("Parser did not return an outcome for every manifest file")
    set_file_statuses(batch_id, outcomes)


# The merge implementation uses (_source_id, _source_row_number) as its
# idempotency key. A retry after manifest failure therefore cannot append the
# same source rows twice. File-level states permit valid files to complete while
# empty, malformed, schema-mismatched, or key-invalid inputs remain quarantined.
