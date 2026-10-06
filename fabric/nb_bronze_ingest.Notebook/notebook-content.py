# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "42cf2182-c8c5-4e6d-a043-92d7345b6a05",
# META       "default_lakehouse_name": "lh_bronze",
# META       "default_lakehouse_workspace_id": "c4f26779-2d34-4985-be4a-c97051d56fc6",
# META       "known_lakehouses": [
# META         {
# META           "id": "42cf2182-c8c5-4e6d-a043-92d7345b6a05"
# META         }
# META       ]
# META     },
# META     "environment": {
# META       "environmentId": "9af8fb61-0bc5-b929-4da1-be8e5f9e4aeb",
# META       "workspaceId": "00000000-0000-0000-0000-000000000000"
# META     }
# META   }
# META }

# PARAMETERS CELL ********************

env = "dev"
config_id = "fd_competitions"
pipeline_run_id = ""
max_api_calls = 0

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# nb_bronze_ingest: ejecuta UNA fila de ctl_source_config (la pipeline lo llama una vez por
# fila desde un ForEach). Flujo:
#   watermark → handler (llamadas a la API) → archivos crudos en Files/raw → versiones nuevas
#   en la tabla Bronze → watermark nuevo → una fila en ctl_run_log (también si falla).
# Reejecutarlo no duplica datos: Bronze solo añade registros cuyo contenido cambió.
import importlib.metadata
import json

from pyspark.sql import functions as F

from src.clients.budget import InMemoryBudget
from src.clients.football_data import FootballDataClient
from src.ingestion import bronze_io
from src.ingestion.batch import build_batch
from src.ingestion.control import RUN_STATUS_FAILED, RUN_STATUS_SKIPPED, RUN_STATUS_SUCCEEDED
from src.ingestion.handlers import ConfigRow, run_handler
from src.ingestion.raw_layout import new_batch_id

config_row = spark.table("ctl_source_config").where(F.col("config_id") == config_id).first()
if config_row is None:
    raise ValueError(f"config_id desconocido: {config_id}. ¿Se ejecutó nb_bronze_setup?")
config = ConfigRow.from_table_row(config_row.asDict())

print(f"Entorno: {env} · fabric_futbol {importlib.metadata.version('fabric_futbol')}")
print(f"{config.config_id}: {config.source}/{config.entity} ({config.load_type})")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Clientes por fuente. Las keys se leen del Key Vault cuya URL está en vl_futbol; nunca se
# imprimen ni se pasan como parámetro.
key_vault_url = notebookutils.variableLibrary.get("$(/**/vl_futbol/key_vault_url)")
run_budgets = [InMemoryBudget(int(max_api_calls), name="ejecución")] if int(max_api_calls) else []


def build_client(source):
    if source == "football_data":
        api_key = notebookutils.credentials.getSecret(key_vault_url, "football-data-api-key")
        return FootballDataClient(api_key, budgets=run_budgets)
    raise NotImplementedError(f"Fuente sin cliente todavía: {source}")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

started_at = bronze_io.utc_now()
batch_id = new_batch_id(started_at)
client = None
summary = {"config_id": config_id, "batch_id": batch_id}
log_entry = {
    "run_id": f"{config_id}:{batch_id}",
    "batch_id": batch_id,
    "pipeline_run_id": pipeline_run_id or None,
    "config_id": config.config_id,
    "source": config.source,
    "entity": config.entity,
    "load_type": config.load_type,
    "started_at": started_at,
}

try:
    if not config_row["is_active"]:
        log_entry["status"] = RUN_STATUS_SKIPPED
    else:
        watermark_before = bronze_io.read_watermark(spark, config_id)
        client = build_client(config.source)
        result = run_handler(client, config, watermark_before, started_at.date())
        batch = build_batch(
            result,
            source=config.source,
            config_id=config_id,
            batch_id=batch_id,
            ingest_date=started_at.date(),
        )
        files_written = bronze_io.write_raw_files(batch.files)
        inserted_by_table = {
            table: bronze_io.append_new_versions(spark, table, rows)
            for table, rows in batch.rows_by_table.items()
        }
        if result.watermark_after is not None:
            bronze_io.write_watermark(
                spark, config_id, result.watermark_after, result.watermark_type, batch_id
            )
        log_entry.update(
            status=RUN_STATUS_SUCCEEDED,
            files_written=files_written,
            records_read=batch.records_read,
            records_inserted=sum(inserted_by_table.values()),
            watermark_before=watermark_before,
            watermark_after=result.watermark_after,
        )
        summary["inserted_by_table"] = inserted_by_table
except Exception as exc:
    log_entry.update(status=RUN_STATUS_FAILED, error_message=f"{type(exc).__name__}: {exc}"[:2000])
    raise
finally:
    log_entry["api_calls"] = client.calls_made if client is not None else 0
    log_entry["finished_at"] = bronze_io.utc_now()
    bronze_io.append_run_log(spark, log_entry)
    summary.update(
        {k: log_entry.get(k) for k in ("status", "api_calls", "files_written", "records_read")}
    )
    summary["records_inserted"] = log_entry.get("records_inserted")
    print(json.dumps(summary, indent=2, default=str))

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Valor de salida para la pipeline (activity('…').output.result.exitValue).
notebookutils.notebook.exit(json.dumps(summary, default=str))

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
