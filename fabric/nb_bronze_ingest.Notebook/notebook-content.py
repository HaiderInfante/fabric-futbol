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
#   watermark → run_config (handler + archivos crudos en Files/raw + versiones nuevas en la
#   tabla Bronze; por bloques en la carga por archivos) → watermark nuevo → una fila en
#   ctl_run_log (también si falla).
# Reejecutarlo no duplica datos: Bronze solo añade registros cuyo contenido cambió.
import importlib.metadata
import json

from pyspark.sql import functions as F

from src.clients.api_football import ApiFootballClient
from src.clients.budget import InMemoryBudget
from src.clients.football_data import FootballDataClient
from src.clients.statsbomb import StatsBombClient
from src.ingestion import bronze_io
from src.ingestion.control import (
    API_DAILY_BUDGETS,
    RUN_STATUS_BUDGET_EXHAUSTED,
    RUN_STATUS_FAILED,
    RUN_STATUS_SKIPPED,
    RUN_STATUS_SUCCEEDED,
)
from src.ingestion.errors import is_permanent_error
from src.ingestion.handlers import ConfigRow
from src.ingestion.raw_layout import new_batch_id
from src.ingestion.runner import run_config

config_row = spark.table("ctl_source_config").where(F.col("config_id") == config_id).first()
if config_row is None:
    raise ValueError(f"config_id desconocido: {config_id}. ¿Se ejecutó nb_bronze_setup?")
config = ConfigRow.from_table_row(config_row.asDict())

# Versión del wheel que realmente se cargó: queda en ctl_run_log.code_version (ADR-008)
code_version = importlib.metadata.version("fabric_futbol")
print(f"Entorno: {env} · fabric_futbol {code_version}")
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
daily_budget = None  # solo API-Football: presupuesto diario que se persiste en ctl_api_budget


def build_client(source):
    global daily_budget
    if source == "football_data":
        api_key = notebookutils.credentials.getSecret(key_vault_url, "football-data-api-key")
        return FootballDataClient(api_key, budgets=run_budgets)
    if source == "statsbomb":
        return StatsBombClient(budgets=run_budgets)  # datos públicos: sin key
    if source == "api_football":
        # Presupuesto diario (UTC) = límite - reserva, empezando por lo ya usado hoy según
        # ctl_api_budget; luego se alinea con /status (gratis) y con los headers de cada
        # respuesta. La cuota de la configuración (daily_quota) es un tope adicional.
        limits = API_DAILY_BUDGETS["api_football"]
        used_today = bronze_io.read_budget_used(spark, "api_football", started_at.date())
        daily_budget = InMemoryBudget(
            limits["daily_limit"] - limits["reserve"], name="api_football_diario", used=used_today
        )
        quota = config.params.get("daily_quota")
        quota_budgets = [InMemoryBudget(int(quota), name=f"cuota {config_id}")] if quota else []
        api_key = notebookutils.credentials.getSecret(key_vault_url, "api-football-api-key")
        af_client = ApiFootballClient(
            api_key, daily_budget=daily_budget, budgets=run_budgets + quota_budgets
        )
        af_client.sync_budget()
        print(f"Presupuesto API-Football hoy: {daily_budget.used}/{daily_budget.limit} usadas")
        return af_client
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
    "code_version": code_version,
}

try:
    if not config_row["is_active"]:
        log_entry["status"] = RUN_STATUS_SKIPPED
    else:
        watermark_before = bronze_io.read_watermark(spark, config_id)
        client = build_client(config.source)
        stats = run_config(
            bronze_io.SparkBronzeWriter(spark),
            client,
            config,
            watermark_before,
            batch_id=batch_id,
            today=started_at.date(),
        )
        if stats.watermark_after is not None:
            bronze_io.write_watermark(
                spark, config_id, stats.watermark_after, stats.watermark_type, batch_id
            )
        log_entry.update(
            status=RUN_STATUS_BUDGET_EXHAUSTED if stats.stopped_by_budget else RUN_STATUS_SUCCEEDED,
            files_written=stats.files_written,
            records_read=stats.records_read,
            records_inserted=stats.records_inserted,
            watermark_before=watermark_before,
            watermark_after=stats.watermark_after,
        )
        summary["inserted_by_table"] = stats.inserted_by_table
        if stats.error is not None:
            # El handler paró por un error, pero lo descargado y el watermark ya se guardaron
            raise stats.error
except Exception as exc:
    log_entry.update(status=RUN_STATUS_FAILED, error_message=f"{type(exc).__name__}: {exc}"[:2000])
    # Permanente (error de plan, 4xx): reintentar repetiría el error y gastaría cuota. Se
    # termina sin excepción y la pipeline lo marca con la actividad Fail (sin reintentos).
    # Transitorio (red, 5xx): se relanza para que actúe el retry de la actividad Notebook.
    if not is_permanent_error(exc):
        raise
finally:
    # Solo las llamadas que consumen cuota (/status es gratis)
    log_entry["api_calls"] = client.billable_calls if client is not None else 0
    log_entry["finished_at"] = bronze_io.utc_now()
    bronze_io.append_run_log(spark, log_entry)
    if daily_budget is not None:
        limits = API_DAILY_BUDGETS["api_football"]
        bronze_io.write_budget(
            spark,
            "api_football",
            started_at.date(),
            daily_limit=limits["daily_limit"],
            reserve=limits["reserve"],
            calls_used=daily_budget.used,
            provider_used=client.provider_used if client is not None else None,
        )
    summary.update(
        {k: log_entry.get(k) for k in ("status", "api_calls", "files_written", "records_read")}
    )
    summary["records_inserted"] = log_entry.get("records_inserted")
    summary["error_message"] = log_entry.get("error_message")
    print(json.dumps(summary, indent=2, default=str))

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Valor de salida para la pipeline (activity('…').output.result.exitValue). Si status es
# "failed" (error permanente), la pipeline lo convierte en fallo con la actividad Fail.
notebookutils.notebook.exit(json.dumps(summary, default=str))

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
