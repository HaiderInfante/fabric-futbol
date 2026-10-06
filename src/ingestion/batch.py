"""Convierte el resultado de un handler en un lote Bronze: archivos crudos y filas por tabla.

Es puro Python (sin Spark): el notebook solo escribe lo que esto devuelve.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any

from src.ingestion.handlers import HandlerResult
from src.ingestion.raw_layout import bronze_table_name, raw_relative_path
from src.ingestion.records import extract_records


@dataclass
class BronzeBatch:
    batch_id: str
    files: list[tuple[str, Any]] = field(default_factory=list)  # (ruta relativa, payload)
    rows_by_table: dict[str, list[dict]] = field(default_factory=dict)

    @property
    def records_read(self) -> int:
        return sum(len(rows) for rows in self.rows_by_table.values())


def build_batch(
    result: HandlerResult,
    *,
    source: str,
    config_id: str,
    batch_id: str,
    ingest_date: date,
) -> BronzeBatch:
    batch = BronzeBatch(batch_id=batch_id)
    for raw in result.raw_files:
        path = raw_relative_path(source, raw.entity, ingest_date, batch_id, raw.name)
        batch.files.append((path, raw.payload))
        table = bronze_table_name(source, raw.entity)
        for record in extract_records(source, raw.entity, raw.payload, raw.context):
            batch.rows_by_table.setdefault(table, []).append(
                {
                    "record_key": record.record_key,
                    "record_hash": record.record_hash,
                    "record_context": record.record_context,
                    "payload": record.payload,
                    "_source": source,
                    "_config_id": config_id,
                    "_batch_id": batch_id,
                    "_file_name": path,
                }
            )
    return batch
