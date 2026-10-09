"""Escritura en lh_bronze desde un notebook de Fabric (Spark).

Supone que lh_bronze es el lakehouse por defecto del notebook: los archivos van al punto de
montaje /lakehouse/default y las tablas se nombran sin prefijo. No tiene tests locales
(necesita Spark); la lógica testeable vive en handlers.py, batch.py y records.py.
"""

from __future__ import annotations

import json
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

LAKEHOUSE_MOUNT = Path("/lakehouse/default")

BRONZE_SCHEMA = (
    "record_key string, record_hash string, record_context string, payload string, "
    "_source string, _config_id string, _batch_id string, _file_name string"
)


# --- Archivos crudos ---------------------------------------------------------------------------


def write_raw_files(files: list[tuple[str, Any]]) -> int:
    """Guarda cada respuesta tal cual (JSON) en Files/raw/…; devuelve cuántos archivos."""
    for relative_path, payload in files:
        target = LAKEHOUSE_MOUNT / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return len(files)


# --- Tablas Bronze -----------------------------------------------------------------------------


def ensure_bronze_table(spark: SparkSession, table: str) -> None:
    spark.sql(
        f"CREATE TABLE IF NOT EXISTS {table} ({BRONZE_SCHEMA}, _ingested_at timestamp) USING DELTA"
    )


def append_new_versions(spark: SparkSession, table: str, rows: list[dict]) -> int:
    """Añade solo los registros nuevos o cuyo contenido cambió respecto a su ÚLTIMA versión.

    Comparar con la última versión (y no con cualquier versión anterior) hace que un cambio
    A → B → A quede registrado. Reejecutar el mismo lote no inserta nada: es idempotente.
    """
    ensure_bronze_table(spark, table)
    columns = [c.split()[0] for c in BRONZE_SCHEMA.split(", ")]
    incoming: DataFrame = (
        spark.createDataFrame([tuple(r[c] for c in columns) for r in rows], BRONZE_SCHEMA)
        .dropDuplicates(["record_key", "record_hash"])
        .withColumn("_ingested_at", F.current_timestamp())
    )
    latest = (
        spark.table(table)
        .groupBy("record_key")
        .agg(F.max_by("record_hash", "_ingested_at").alias("_last_hash"))
    )
    new_versions = (
        incoming.join(latest, "record_key", "left")
        .where(F.col("_last_hash").isNull() | (F.col("_last_hash") != F.col("record_hash")))
        .drop("_last_hash")
        .cache()
    )
    inserted = new_versions.count()
    if inserted:
        new_versions.write.mode("append").saveAsTable(table)
    new_versions.unpersist()
    return inserted


# --- Control: watermark y log de ejecución -----------------------------------------------------


def read_watermark(spark: SparkSession, config_id: str) -> str | None:
    row = (
        spark.table("ctl_watermark")
        .where(F.col("config_id") == config_id)
        .select("watermark_value")
        .first()
    )
    return row["watermark_value"] if row else None


def write_watermark(
    spark: SparkSession, config_id: str, value: str | None, value_type: str | None, batch_id: str
) -> None:
    spark.createDataFrame(
        [(config_id, value, value_type, batch_id)],
        "config_id string, watermark_value string, watermark_type string, last_batch_id string",
    ).createOrReplaceTempView("wm_new")
    spark.sql("""
        MERGE INTO ctl_watermark AS t
        USING wm_new AS s ON t.config_id = s.config_id
        WHEN MATCHED THEN UPDATE SET
            watermark_value = s.watermark_value, watermark_type = s.watermark_type,
            last_batch_id = s.last_batch_id, updated_at = current_timestamp()
        WHEN NOT MATCHED THEN INSERT
            (config_id, watermark_value, watermark_type, last_batch_id, updated_at)
            VALUES (s.config_id, s.watermark_value, s.watermark_type, s.last_batch_id,
                    current_timestamp())
    """)


RUN_LOG_SCHEMA = (
    "run_id string, batch_id string, pipeline_run_id string, config_id string, source string, "
    "entity string, load_type string, started_at timestamp, finished_at timestamp, "
    "status string, api_calls int, files_written int, records_read bigint, "
    "records_inserted bigint, watermark_before string, watermark_after string, "
    "error_message string"
)


def append_run_log(spark: SparkSession, entry: dict) -> None:
    """Una fila por ejecución (se escribe al final, también si falla)."""
    columns = [c.split()[0] for c in RUN_LOG_SCHEMA.split(", ")]
    spark.createDataFrame([tuple(entry.get(c) for c in columns)], RUN_LOG_SCHEMA).write.mode(
        "append"
    ).saveAsTable("ctl_run_log")


def read_manifest(spark: SparkSession, source: str) -> dict[str, str]:
    rows = (
        spark.table("ctl_file_manifest")
        .where(F.col("source") == source)
        .select("file_key", "source_last_updated")
        .collect()
    )
    return {r["file_key"]: r["source_last_updated"] for r in rows}


def write_manifest(
    spark: SparkSession, source: str, updates: list[tuple[str, str]], batch_id: str
) -> None:
    if not updates:
        return
    spark.createDataFrame(
        [(source, key, version, batch_id) for key, version in updates],
        "source string, file_key string, source_last_updated string, batch_id string",
    ).createOrReplaceTempView("manifest_new")
    spark.sql("""
        MERGE INTO ctl_file_manifest AS t
        USING manifest_new AS s ON t.source = s.source AND t.file_key = s.file_key
        WHEN MATCHED THEN UPDATE SET
            source_last_updated = s.source_last_updated, batch_id = s.batch_id,
            processed_at = current_timestamp()
        WHEN NOT MATCHED THEN INSERT
            (source, file_key, source_last_updated, batch_id, processed_at)
            VALUES (s.source, s.file_key, s.source_last_updated, s.batch_id, current_timestamp())
    """)


class SparkBronzeWriter:
    """Implementación de `runner.BronzeWriter` sobre lh_bronze."""

    def __init__(self, spark: SparkSession) -> None:
        self.spark = spark

    def write_files(self, files: list[tuple[str, Any]]) -> int:
        return write_raw_files(files)

    def append(self, table: str, rows: list[dict]) -> int:
        return append_new_versions(self.spark, table, rows)

    def read_manifest(self, source: str) -> dict[str, str]:
        return read_manifest(self.spark, source)

    def write_manifest(self, source: str, updates: list[tuple[str, str]], batch_id: str) -> None:
        write_manifest(self.spark, source, updates, batch_id)


def utc_now() -> datetime:
    return datetime.now(UTC)


def utc_today() -> date:
    return utc_now().date()
