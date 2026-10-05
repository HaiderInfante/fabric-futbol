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

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# nb_bronze_setup: prepara lh_bronze para la ingesta. Es idempotente: se puede ejecutar
# las veces que haga falta y en cualquier entorno (los datos no viajan entre workspaces).
# 1) Comprueba que el wheel fabric_futbol del Environment env_futbol está instalado.
import importlib.metadata

from src.ingestion.control import CONTROL_TABLES_DDL
from src.ingestion.source_config import config_rows

print(f"Entorno: {env}")
print(f"fabric_futbol {importlib.metadata.version('fabric_futbol')}")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# 2) Crea las tablas de control en el lakehouse por defecto (lh_bronze) si no existen.
for table_name, ddl in CONTROL_TABLES_DDL.items():
    spark.sql(ddl)
    print(f"OK {table_name}")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# 3) Sincroniza ctl_source_config con la configuración versionada en src/ingestion.
#    - Inserta configuraciones nuevas y actualiza las que cambiaron (updated_at solo cambia
#      si cambia algún valor).
#    - Desactiva las que ya no existen en el código (no las borra: conservan su historial).
CONFIG_SCHEMA = (
    "config_id string, source string, entity string, load_type string, params string, "
    "watermark_column string, priority int, is_active boolean, description string"
)
COLUMNS = [c.split()[0] for c in CONFIG_SCHEMA.split(", ")]

rows = [tuple(row[c] for c in COLUMNS) for row in config_rows()]
spark.createDataFrame(rows, CONFIG_SCHEMA).createOrReplaceTempView("cfg_from_code")

changed = " OR ".join(f"NOT (t.{c} <=> s.{c})" for c in COLUMNS if c != "config_id")
update_set = ", ".join(f"{c} = s.{c}" for c in COLUMNS if c != "config_id")
insert_cols = ", ".join(COLUMNS)
insert_vals = ", ".join(f"s.{c}" for c in COLUMNS)

spark.sql(f"""
    MERGE INTO ctl_source_config AS t
    USING cfg_from_code AS s
    ON t.config_id = s.config_id
    WHEN MATCHED AND ({changed}) THEN
        UPDATE SET {update_set}, updated_at = current_timestamp()
    WHEN NOT MATCHED THEN
        INSERT ({insert_cols}, updated_at) VALUES ({insert_vals}, current_timestamp())
    WHEN NOT MATCHED BY SOURCE AND t.is_active THEN
        UPDATE SET is_active = false, updated_at = current_timestamp()
""")

display(
    spark.table("ctl_source_config")
    .select("config_id", "source", "entity", "load_type", "priority", "is_active", "updated_at")
    .orderBy("priority")
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# 4) Verifica el acceso a los secretos del Key Vault cuya URL está en la Variable Library.
#    Nunca se imprime el valor: solo si se pudo leer y no está vacío.
key_vault_url = notebookutils.variableLibrary.get("$(/**/vl_futbol/key_vault_url)")
print(f"Key Vault: {key_vault_url}")

for secret_name in ["football-data-api-key", "api-football-api-key"]:
    value = notebookutils.credentials.getSecret(key_vault_url, secret_name)
    status = "OK" if value else "VACÍO"
    print(f"{status} {secret_name}")
    del value

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# 5) Resumen: tablas presentes en lh_bronze.
display(spark.sql("SHOW TABLES"))

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
