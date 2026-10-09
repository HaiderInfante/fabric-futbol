"""Handlers de ingesta: traducen una fila de ctl_source_config en llamadas a la API.

Un handler no escribe nada: devuelve las respuestas crudas (`RawFile`) y el watermark nuevo.
La escritura (archivos, Delta, control) la hace el notebook con `bronze_io`, así esta lógica
se prueba en local sin Spark.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date
from typing import Any

from src.clients.api_football import ApiFootballClient
from src.clients.budget import BudgetExceededError
from src.clients.football_data import FootballDataClient
from src.clients.statsbomb import StatsBombClient
from src.ingestion.planning import (
    compute_window,
    mark_completed,
    parse_completed,
    pending_targets,
    target_key,
)


@dataclass
class RawFile:
    entity: str  # entidad Bronze de destino (define carpeta y tabla)
    name: str  # nombre del archivo crudo
    payload: Any
    context: dict


@dataclass
class HandlerResult:
    raw_files: list[RawFile] = field(default_factory=list)
    watermark_after: str | None = None
    watermark_type: str | None = None
    # Carga por archivos: (file_key, versión) procesados, para ctl_file_manifest
    manifest_updates: list[tuple[str, str]] = field(default_factory=list)
    # True si el handler paró al agotar el presupuesto (lo descargado se guarda igual)
    stopped_by_budget: bool = False


@dataclass(frozen=True)
class ConfigRow:
    """Fila de ctl_source_config con `params` ya deserializado."""

    config_id: str
    source: str
    entity: str
    load_type: str
    params: dict

    @classmethod
    def from_table_row(cls, row: dict) -> ConfigRow:
        return cls(
            config_id=row["config_id"],
            source=row["source"],
            entity=row["entity"],
            load_type=row["load_type"],
            params=json.loads(row["params"] or "{}"),
        )


# --- football-data.org -------------------------------------------------------------------------


def _season_param(target: dict) -> int | None:
    """`None` = temporada en curso (la API la resuelve sola)."""
    return None if target["season"] == "current" else int(target["season"])


def _fd_full(client: FootballDataClient, config: ConfigRow, *_: Any) -> HandlerResult:
    payload = client.competitions()
    return HandlerResult([RawFile(config.entity, "competitions", payload, {})])


def _fd_window(
    client: FootballDataClient, config: ConfigRow, watermark: str | None, today: date
) -> HandlerResult:
    params = config.params
    result = HandlerResult(watermark_after=today.isoformat(), watermark_type="date")
    for target in params["targets"]:
        code = target["competition"]
        season = client.competition(code)["currentSeason"]
        date_from, date_to = compute_window(
            watermark=date.fromisoformat(watermark) if watermark else None,
            today=today,
            season_start=date.fromisoformat(season["startDate"]),
            season_end=date.fromisoformat(season["endDate"]),
            lookback_days=params["lookback_days"],
            lookahead_days=params["lookahead_days"],
        )
        payload = client.matches(code, date_from=date_from.isoformat(), date_to=date_to.isoformat())
        context = {
            "competition": code,
            "season": "current",
            "date_from": date_from.isoformat(),
            "date_to": date_to.isoformat(),
        }
        result.raw_files.append(
            RawFile(config.entity, f"{code}_{date_from}_{date_to}", payload, context)
        )
    return result


def _fd_season_full(
    client: FootballDataClient, config: ConfigRow, watermark: str | None, _today: date
) -> HandlerResult:
    completed = parse_completed(watermark)
    targets = pending_targets(config.params["targets"], completed)
    fetch = {"matches": client.matches, "teams": client.teams}[config.entity]
    result = HandlerResult(watermark_type="completed_targets")
    for target in targets:
        code = target["competition"]
        payload = fetch(code, season=_season_param(target))
        name = f"{code}_{target['season']}"
        result.raw_files.append(RawFile(config.entity, name, payload, dict(target)))
    result.watermark_after = mark_completed(completed, targets)
    return result


def _fd_snapshot(
    client: FootballDataClient, config: ConfigRow, _watermark: str | None, today: date
) -> HandlerResult:
    result = HandlerResult(watermark_after=today.isoformat(), watermark_type="date")
    for target in config.params["targets"]:
        code, season = target["competition"], _season_param(target)
        if config.entity == "standings":
            payload = client.standings(code, season=season)
        else:
            payload = client.scorers(code, season=season, limit=config.params.get("limit"))
        context = {**target, "snapshot_date": today.isoformat()}
        result.raw_files.append(
            RawFile(config.entity, f"{code}_{target['season']}", payload, context)
        )
    return result


# --- StatsBomb Open Data -----------------------------------------------------------------------


def _sb_full(client: StatsBombClient, config: ConfigRow, *_: Any) -> HandlerResult:
    if config.entity == "competitions":
        return HandlerResult([RawFile("competitions", "competitions", client.competitions(), {})])
    result = HandlerResult()
    for target in config.params["targets"]:
        comp, season = target["competition_id"], target["season_id"]
        payload = client.matches(comp, season)
        result.raw_files.append(RawFile("matches", f"{comp}_{season}", payload, dict(target)))
    return result


def match_version(match: dict) -> str:
    """Versión de los archivos de un partido: cambia si StatsBomb corrige eventos o 360."""
    return f"{match.get('last_updated') or ''}|{match.get('last_updated_360') or ''}"


def plan_statsbomb_match_files(
    client: StatsBombClient, config: ConfigRow, manifest: dict[str, str]
) -> list[dict]:
    """Partidos cuyos archivos hay que (re)descargar: nuevos o con versión distinta.

    Respeta el orden de `targets` (Euro → PL → La Liga) y el tope `max_matches_per_run`.
    """
    pending: list[dict] = []
    for target in config.params["targets"]:
        comp, season = target["competition_id"], target["season_id"]
        for match in sorted(client.matches(comp, season), key=lambda m: m["match_date"]):
            if match.get("match_status") != "available":
                continue
            version = match_version(match)
            file_key = f"match/{match['match_id']}"
            if manifest.get(file_key) != version:
                pending.append(
                    {
                        "match_id": match["match_id"],
                        "competition_id": comp,
                        "season_id": season,
                        "file_key": file_key,
                        "version": version,
                        "has_360": match.get("match_status_360") == "available",
                    }
                )
    return pending[: config.params.get("max_matches_per_run", len(pending))]


def fetch_statsbomb_match_files(client: StatsBombClient, matches: list[dict]) -> HandlerResult:
    """Descarga eventos, alineaciones y 360 (si existe) de un bloque de partidos."""
    result = HandlerResult(watermark_type="max_last_updated")
    for match in matches:
        match_id = match["match_id"]
        context = {k: match[k] for k in ("match_id", "competition_id", "season_id", "version")}
        result.raw_files.append(RawFile("events", str(match_id), client.events(match_id), context))
        result.raw_files.append(
            RawFile("lineups", str(match_id), client.lineups(match_id), context)
        )
        if match["has_360"]:
            three_sixty = client.three_sixty(match_id)
            if three_sixty is not None:
                result.raw_files.append(RawFile("three_sixty", str(match_id), three_sixty, context))
        result.manifest_updates.append((match["file_key"], match["version"]))
    return result


# --- API-Football (presupuesto diario + cuota por configuración) --------------------------------
#
# Todas las llamadas consumen presupuesto. Cuando el cliente lanza BudgetExceededError, el
# handler para, marca `stopped_by_budget` y devuelve lo ya descargado: la siguiente ejecución
# continúa donde se quedó (watermark o pendientes calculados desde Bronze).

FIXTURE_ENDPOINTS = {
    "fixture_statistics": "fixtures/statistics",
    "fixture_players": "fixtures/players",
}
FINISHED_STATUSES = frozenset({"FT", "AET", "PEN"})


def _af_target_params(target: dict) -> dict:
    return {"league": target["league"], "season": target["season"]}


def _af_season_full(
    client: ApiFootballClient, config: ConfigRow, watermark: str | None, _today: date
) -> HandlerResult:
    completed = parse_completed(watermark)
    result = HandlerResult(watermark_type="completed_targets")
    done: list[dict] = []
    for target in pending_targets(config.params["targets"], completed):
        try:
            payload = client.get_payload(config.entity, _af_target_params(target))
        except BudgetExceededError:
            result.stopped_by_budget = True
            break
        name = f"{target['league']}_{target['season']}"
        result.raw_files.append(RawFile(config.entity, name, payload, dict(target)))
        done.append(target)
    result.watermark_after = mark_completed(completed, done)
    return result


def _af_players_pages(
    client: ApiFootballClient, config: ConfigRow, watermark: str | None, _today: date
) -> HandlerResult:
    """Recorre /players página a página. El watermark guarda, por objetivo, la siguiente
    página y el total: {"league=4|season=2024": {"next_page": 3, "total_pages": 32}}."""
    progress = json.loads(watermark) if watermark else {}
    result = HandlerResult(watermark_type="page_progress")
    for target in config.params["targets"]:
        key = target_key(target)
        state = progress.get(key, {"next_page": 1, "total_pages": None})
        while state["total_pages"] is None or state["next_page"] <= state["total_pages"]:
            page = state["next_page"]
            try:
                payload = client.get_payload("players", {**_af_target_params(target), "page": page})
            except BudgetExceededError:
                result.stopped_by_budget = True
                break
            name = f"{target['league']}_{target['season']}_p{page}"
            context = {**target, "page": page}
            result.raw_files.append(RawFile("players", name, payload, context))
            state = {"next_page": page + 1, "total_pages": int(payload["paging"]["total"])}
        progress[key] = state
        if result.stopped_by_budget:
            break
    result.watermark_after = json.dumps(progress, sort_keys=True)
    return result


def plan_fixture_backfill(
    config: ConfigRow, fixture_records: list[dict], done_keys: set[str]
) -> list[dict]:
    """Partidos terminados de los objetivos que aún no tienen esta entidad en Bronze.

    `fixture_records` son las últimas versiones de api_football_fixtures (record_key,
    record_context, payload). Orden: el de `targets` (Euro → PL → La Liga) y luego la fecha.
    """
    order = {target_key(t): i for i, t in enumerate(config.params["targets"])}
    pending = []
    for record in fixture_records:
        context = json.loads(record["record_context"])
        position = order.get(target_key(_af_target_params(context)))
        if position is None or record["record_key"] in done_keys:
            continue
        fixture = json.loads(record["payload"])["fixture"]
        if fixture["status"]["short"] not in FINISHED_STATUSES:
            continue
        pending.append(
            {
                "fixture_id": int(record["record_key"]),
                "league": context["league"],
                "season": context["season"],
                "date": fixture["date"],
                "_position": position,
            }
        )
    pending.sort(key=lambda p: (p["_position"], p["date"]))
    return pending


def fetch_fixture_backfill(
    client: ApiFootballClient, config: ConfigRow, pending: list[dict]
) -> HandlerResult:
    endpoint = FIXTURE_ENDPOINTS[config.entity]
    result = HandlerResult(watermark_type="backfill_progress")
    for item in pending:
        try:
            payload = client.get_payload(endpoint, {"fixture": item["fixture_id"]})
        except BudgetExceededError:
            result.stopped_by_budget = True
            break
        context = {k: item[k] for k in ("fixture_id", "league", "season")}
        result.raw_files.append(RawFile(config.entity, str(item["fixture_id"]), payload, context))
    return result


Handler = Callable[[Any, ConfigRow, str | None, date], HandlerResult]

HANDLERS: dict[tuple[str, str], Handler] = {
    ("api_football", "season_full"): _af_season_full,
    ("football_data", "full"): _fd_full,
    ("football_data", "window"): _fd_window,
    ("football_data", "season_full"): _fd_season_full,
    ("football_data", "snapshot"): _fd_snapshot,
    ("statsbomb", "full"): _sb_full,
}


# Rellenos por páginas cuyo progreso vive en el watermark. El relleno por partido
# (FIXTURE_ENDPOINTS) necesita el estado de Bronze y lo orquesta runner.py.
PAGED_BACKFILL_HANDLERS: dict[tuple[str, str], Handler] = {
    ("api_football", "players"): _af_players_pages,
}


def run_handler(
    client: Any, config: ConfigRow, watermark: str | None, today: date
) -> HandlerResult:
    if config.load_type == "budgeted_backfill":
        handler = PAGED_BACKFILL_HANDLERS.get((config.source, config.entity))
    else:
        handler = HANDLERS.get((config.source, config.load_type))
    if handler is None:
        raise NotImplementedError(
            f"Sin handler para {config.source}/{config.load_type} ({config.config_id})"
        )
    return handler(client, config, watermark, today)
