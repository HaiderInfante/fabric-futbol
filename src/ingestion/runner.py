"""Ejecuta una configuración de ctl_source_config de principio a fin.

El almacenamiento se inyecta (`BronzeWriter`): en Fabric es `bronze_io.SparkBronzeWriter`, en
los tests uno en memoria. Así el bucle completo (incluido el procesamiento por bloques de la
carga por archivos) se prueba en local.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field
from datetime import date
from typing import Any, Protocol

from src.ingestion.batch import build_batch
from src.ingestion.handlers import (
    ConfigRow,
    HandlerResult,
    fetch_statsbomb_match_files,
    plan_statsbomb_match_files,
    run_handler,
)

DEFAULT_CHUNK_SIZE = 10


class BronzeWriter(Protocol):
    def write_files(self, files: list[tuple[str, Any]]) -> int: ...

    def append(self, table: str, rows: list[dict]) -> int: ...

    def read_manifest(self, source: str) -> dict[str, str]: ...

    def write_manifest(
        self, source: str, updates: list[tuple[str, str]], batch_id: str
    ) -> None: ...


@dataclass
class RunStats:
    files_written: int = 0
    records_read: int = 0
    records_inserted: int = 0
    inserted_by_table: dict[str, int] = field(default_factory=dict)
    watermark_after: str | None = None
    watermark_type: str | None = None

    def add(self, other: RunStats) -> None:
        self.files_written += other.files_written
        self.records_read += other.records_read
        self.records_inserted += other.records_inserted
        for table, count in other.inserted_by_table.items():
            self.inserted_by_table[table] = self.inserted_by_table.get(table, 0) + count


def _chunks(items: list, size: int) -> Iterator[list]:
    for start in range(0, len(items), size):
        yield items[start : start + size]


def persist(
    writer: BronzeWriter,
    result: HandlerResult,
    config: ConfigRow,
    *,
    batch_id: str,
    ingest_date: date,
) -> RunStats:
    """Escribe crudo + Bronze de un resultado y devuelve los contadores."""
    batch = build_batch(
        result,
        source=config.source,
        config_id=config.config_id,
        batch_id=batch_id,
        ingest_date=ingest_date,
    )
    stats = RunStats(files_written=writer.write_files(batch.files), records_read=batch.records_read)
    for table, rows in batch.rows_by_table.items():
        inserted = writer.append(table, rows)
        stats.inserted_by_table[table] = inserted
        stats.records_inserted += inserted
    return stats


def _run_file_incremental(
    writer: BronzeWriter,
    client: Any,
    config: ConfigRow,
    watermark: str | None,
    *,
    batch_id: str,
    today: date,
) -> RunStats:
    manifest = writer.read_manifest(config.source)
    pending = plan_statsbomb_match_files(client, config, manifest)
    chunk_size = config.params.get("chunk_size", DEFAULT_CHUNK_SIZE)
    total = RunStats(watermark_after=watermark, watermark_type="max_last_updated")
    for chunk in _chunks(pending, chunk_size):
        result = fetch_statsbomb_match_files(client, chunk)
        total.add(persist(writer, result, config, batch_id=batch_id, ingest_date=today))
        # El manifiesto se actualiza por bloque: si la ejecución falla a mitad, lo ya escrito
        # no se vuelve a descargar.
        writer.write_manifest(config.source, result.manifest_updates, batch_id)
        processed = [version.split("|")[0] for _, version in result.manifest_updates]
        total.watermark_after = max([total.watermark_after or "", *processed]) or None
    return total


def run_config(
    writer: BronzeWriter,
    client: Any,
    config: ConfigRow,
    watermark: str | None,
    *,
    batch_id: str,
    today: date,
) -> RunStats:
    if config.load_type == "file_incremental":
        return _run_file_incremental(
            writer, client, config, watermark, batch_id=batch_id, today=today
        )
    result = run_handler(client, config, watermark, today)
    stats = persist(writer, result, config, batch_id=batch_id, ingest_date=today)
    stats.watermark_after = result.watermark_after
    stats.watermark_type = result.watermark_type
    return stats
