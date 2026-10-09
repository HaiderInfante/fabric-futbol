"""Configuración versionada de la ingesta Bronze: el contenido de ctl_source_config.

Los datos no viajan entre entornos (solo las definiciones), así que la configuración vive en
código y `nb_bronze_setup` la carga con un MERGE idempotente en cada workspace.

Tipos de carga (`load_type`):
- full: se relee todo en cada ejecución; el MERGE de Bronze solo inserta lo que cambió.
- window: ventana de fechas desde el watermark, con margen hacia atrás (football-data).
- season_full: temporada completa; se repite hasta marcarla como completada.
- snapshot: foto diaria (tablas de posiciones, goleadores).
- budgeted_backfill: elementos pendientes hasta agotar el presupuesto diario (API-Football).
- file_incremental: archivos nuevos o con `last_updated` distinto (StatsBomb).

Alcance según ADR-005. El orden de `targets` en API-Football fija la prioridad del relleno:
Euro 2024 → Premier League → La Liga. `daily_quota` es la cuota de llamadas de cada
configuración por ejecución (ADR-010): así ninguna depende del orden en que la pipeline las
ejecute. La suma puede superar las 90 llamadas útiles; el presupuesto diario manda.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

LOAD_TYPES = frozenset(
    {"full", "window", "season_full", "snapshot", "budgeted_backfill", "file_incremental"}
)

FD_CURRENT = [
    {"competition": "PL", "season": "current"},
    {"competition": "PD", "season": "current"},
]
FD_HISTORY = [
    {"competition": "PL", "season": 2024},
    {"competition": "PD", "season": 2024},
    {"competition": "EC", "season": 2024},
]
AF_TARGETS = [
    {"league": 4, "season": 2024},
    {"league": 39, "season": 2024},
    {"league": 140, "season": 2024},
]
SB_TARGETS = [
    {"competition_id": 55, "season_id": 282},
    {"competition_id": 2, "season_id": 27},
    {"competition_id": 11, "season_id": 90},
]


@dataclass(frozen=True)
class SourceConfig:
    config_id: str
    source: str
    entity: str
    load_type: str
    priority: int
    description: str
    params: dict[str, Any] = field(default_factory=dict)
    watermark_column: str | None = None
    is_active: bool = True

    def as_row(self) -> dict[str, Any]:
        return {
            "config_id": self.config_id,
            "source": self.source,
            "entity": self.entity,
            "load_type": self.load_type,
            "params": json.dumps(self.params, sort_keys=True),
            "watermark_column": self.watermark_column,
            "priority": self.priority,
            "is_active": self.is_active,
            "description": self.description,
        }


def _fd(config_id: str, entity: str, load_type: str, priority: int, description: str, **kw):
    return SourceConfig(config_id, "football_data", entity, load_type, priority, description, **kw)


def _af(config_id: str, entity: str, load_type: str, priority: int, description: str, **kw):
    return SourceConfig(config_id, "api_football", entity, load_type, priority, description, **kw)


def _sb(config_id: str, entity: str, load_type: str, priority: int, description: str, **kw):
    return SourceConfig(config_id, "statsbomb", entity, load_type, priority, description, **kw)


# Argumentos: config_id, entidad, tipo de carga, prioridad (orden en la pipeline), descripción.
# fmt: off
SOURCE_CONFIGS: list[SourceConfig] = [
    # --- football-data.org (10/min, sin límite diario) ------------------------------------
    _fd("fd_competitions", "competitions", "full", 10,
        "Catálogo de competiciones del plan (1 llamada; Bronze guarda las 13)"),
    _fd("fd_matches_current", "matches", "window", 20,
        "Partidos de la temporada en curso por ventana de fechas con margen hacia atrás",
        params={"targets": FD_CURRENT, "lookback_days": 7, "lookahead_days": 14},
        watermark_column="utcDate"),
    _fd("fd_matches_history", "matches", "season_full", 30,
        "Partidos de 2024/25 (temporada cerrada, una sola vez)",
        params={"targets": FD_HISTORY}),
    _fd("fd_teams", "teams", "season_full", 40, "Equipos, plantillas y entrenador por temporada",
        params={"targets": FD_HISTORY + FD_CURRENT}),
    _fd("fd_standings", "standings", "snapshot", 50, "Tabla de posiciones (foto diaria)",
        params={"targets": FD_CURRENT}),
    _fd("fd_scorers", "scorers", "snapshot", 60, "Goleadores (foto diaria)",
        params={"targets": FD_CURRENT, "limit": 50}),
    # --- API-Football (100/día, 10/min; solo 2022-2024) -------------------------------------
    _af("af_fixtures", "fixtures", "season_full", 110,
        "Partidos por liga y temporada (1 llamada por temporada)",
        params={"targets": AF_TARGETS, "daily_quota": 5}),
    _af("af_teams", "teams", "season_full", 120, "Equipos y estadio por liga y temporada",
        params={"targets": AF_TARGETS, "daily_quota": 5}),
    _af("af_injuries", "injuries", "season_full", 130, "Lesiones y bajas por partido",
        params={"targets": AF_TARGETS, "daily_quota": 5}),
    _af("af_players", "players", "budgeted_backfill", 140,
        "Jugadores de la temporada (páginas pendientes)",
        params={"targets": AF_TARGETS, "daily_quota": 10}),
    _af("af_fixture_statistics", "fixture_statistics", "budgeted_backfill", 150,
        "Estadísticas de equipo por partido (fixture_id pendientes)",
        params={"targets": AF_TARGETS, "daily_quota": 40}),
    _af("af_fixture_players", "fixture_players", "budgeted_backfill", 160,
        "Estadísticas de jugador por partido (fixture_id pendientes)",
        params={"targets": AF_TARGETS, "daily_quota": 40}),
    # --- StatsBomb Open Data (sin límite; restricción de volumen) ---------------------------
    _sb("sb_competitions", "competitions", "full", 210, "Competiciones y temporadas disponibles"),
    _sb("sb_matches", "matches", "full", 220,
        "Partidos por competición y temporada (incluye last_updated por partido)",
        params={"targets": SB_TARGETS}),
    _sb("sb_match_files", "match_files", "file_incremental", 230,
        "Eventos, alineaciones y 360 de partidos nuevos o actualizados",
        params={"targets": SB_TARGETS, "max_matches_per_run": 120, "chunk_size": 10},
        watermark_column="last_updated"),
]
# fmt: on


def validate(configs: list[SourceConfig]) -> None:
    """Falla si hay ids duplicados o tipos de carga desconocidos."""
    ids = [c.config_id for c in configs]
    duplicates = {i for i in ids if ids.count(i) > 1}
    if duplicates:
        raise ValueError(f"config_id duplicados: {sorted(duplicates)}")
    unknown = {c.load_type for c in configs} - LOAD_TYPES
    if unknown:
        raise ValueError(f"load_type desconocidos: {sorted(unknown)}")


def config_rows() -> list[dict[str, Any]]:
    validate(SOURCE_CONFIGS)
    return [c.as_row() for c in SOURCE_CONFIGS]
