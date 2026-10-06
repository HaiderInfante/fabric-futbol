"""Convenciones de nombres de Bronze: lotes, rutas de archivos crudos y tablas.

Archivos crudos: Files/raw/<fuente>/<entidad>/ingest_date=YYYY-MM-DD/<batch_id>/<nombre>.json
Tablas Delta:    <fuente>_<entidad>  (p. ej. football_data_matches)
"""

from __future__ import annotations

import re
import uuid
from datetime import date, datetime

RAW_ROOT = "Files/raw"
_UNSAFE = re.compile(r"[^A-Za-z0-9_-]+")


def new_batch_id(now: datetime) -> str:
    """Id de lote ordenable por tiempo y único: 20261005T171500Z_1a2b3c4d."""
    return f"{now:%Y%m%dT%H%M%SZ}_{uuid.uuid4().hex[:8]}"


def safe_name(name: str) -> str:
    return _UNSAFE.sub("_", name).strip("_") or "payload"


def raw_relative_path(source: str, entity: str, ingest_date: date, batch_id: str, name: str) -> str:
    return (
        f"{RAW_ROOT}/{source}/{entity}/ingest_date={ingest_date:%Y-%m-%d}/"
        f"{batch_id}/{safe_name(name)}.json"
    )


def bronze_table_name(source: str, entity: str) -> str:
    return f"{source}_{entity}"
