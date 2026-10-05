"""Tablas de control de la ingesta (Delta en lh_bronze).

- ctl_source_config: qué se ingiere, cómo y en qué orden (la lee la pipeline con Lookup).
- ctl_watermark: último valor procesado por configuración (fecha, temporada completada…).
- ctl_run_log: una fila por ejecución de una configuración; es la evidencia del incremental.
- ctl_api_budget: llamadas consumidas por fuente y día (UTC).
- ctl_file_manifest: archivos ya procesados en la carga incremental por archivos (StatsBomb).

Las sentencias son idempotentes (`CREATE TABLE IF NOT EXISTS`): `nb_bronze_setup` puede
ejecutarse las veces que haga falta.
"""

from __future__ import annotations

CONTROL_TABLES_DDL: dict[str, str] = {
    "ctl_source_config": """
        CREATE TABLE IF NOT EXISTS ctl_source_config (
            config_id STRING NOT NULL,
            source STRING NOT NULL,
            entity STRING NOT NULL,
            load_type STRING NOT NULL,
            params STRING,
            watermark_column STRING,
            priority INT,
            is_active BOOLEAN,
            description STRING,
            updated_at TIMESTAMP
        ) USING DELTA
    """,
    "ctl_watermark": """
        CREATE TABLE IF NOT EXISTS ctl_watermark (
            config_id STRING NOT NULL,
            watermark_value STRING,
            watermark_type STRING,
            last_batch_id STRING,
            updated_at TIMESTAMP
        ) USING DELTA
    """,
    "ctl_run_log": """
        CREATE TABLE IF NOT EXISTS ctl_run_log (
            run_id STRING NOT NULL,
            batch_id STRING,
            pipeline_run_id STRING,
            config_id STRING,
            source STRING,
            entity STRING,
            load_type STRING,
            started_at TIMESTAMP,
            finished_at TIMESTAMP,
            status STRING,
            api_calls INT,
            files_written INT,
            records_read BIGINT,
            records_inserted BIGINT,
            watermark_before STRING,
            watermark_after STRING,
            error_message STRING
        ) USING DELTA
    """,
    "ctl_api_budget": """
        CREATE TABLE IF NOT EXISTS ctl_api_budget (
            source STRING NOT NULL,
            budget_date DATE NOT NULL,
            daily_limit INT,
            reserve INT,
            calls_used INT,
            provider_used INT,
            updated_at TIMESTAMP
        ) USING DELTA
    """,
    "ctl_file_manifest": """
        CREATE TABLE IF NOT EXISTS ctl_file_manifest (
            source STRING NOT NULL,
            file_key STRING NOT NULL,
            source_last_updated STRING,
            batch_id STRING,
            processed_at TIMESTAMP
        ) USING DELTA
    """,
}

# Estados válidos de ctl_run_log.status
RUN_STATUS_RUNNING = "running"
RUN_STATUS_SUCCEEDED = "succeeded"
RUN_STATUS_FAILED = "failed"
RUN_STATUS_SKIPPED = "skipped"  # p. ej. presupuesto agotado antes de empezar
