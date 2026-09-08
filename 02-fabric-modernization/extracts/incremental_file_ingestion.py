"""Record immutable file identity before appending staged data to Bronze.

Classification: sanitized_derivative
Production status: generalized Fabric/Spark implementation pattern
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Callable
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


def discover_csv_files(dataset: str, source_root: Path) -> list[SourceFile]:
    """Discover any-depth CSV input and retain content-aware file identity."""
    discovered = []
    for path in sorted(source_root.rglob("*.csv")):
        stat = path.stat()
        discovered.append(
            SourceFile(
                dataset=dataset,
                path=path,
                size_bytes=stat.st_size,
                modified_ns=stat.st_mtime_ns,
                checksum=sha256(path.read_bytes()).hexdigest(),
            )
        )
    return discovered


def build_ingestion_batch(
    files: list[SourceFile], processed_source_ids: set[str]
) -> tuple[dict[str, object], list[SourceFile]]:
    """Create lineage metadata before a transactional Bronze write."""
    new_files = [row for row in files if row.source_identity not in processed_source_ids]
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
    merge_files_by_source_row: Callable[[str, list[SourceFile]], None],
    set_manifest_status: Callable[[str, str], None],
) -> None:
    """Make retries safe through an idempotent source-ID/row-number Bronze merge."""
    batch_id = str(batch["batch_id"])
    set_manifest_status(batch_id, "in_progress")
    try:
        merge_files_by_source_row(batch_id, files)
    except Exception:
        set_manifest_status(batch_id, "failed")
        raise
    set_manifest_status(batch_id, "complete")


# The merge implementation uses (_source_id, _source_row_number) as its
# idempotency key. A retry after manifest failure therefore cannot append the
# same source rows twice.
