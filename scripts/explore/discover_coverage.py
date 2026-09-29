"""Fase 1, paso A: cobertura de competiciones y temporadas en cada fuente.

Uso (desde la raíz del repo):
    python -m scripts.explore.discover_coverage
    python -m scripts.explore.discover_coverage --af-probe 39:2015 --fd-probe PD:2020

Una prueba (probe) es COMPETICIÓN:TEMPORADA, donde la temporada es un año de inicio,
`current` o `previous`. En football-data la competición es el código (PL); en API-Football
es el id de liga (39).

Llamadas:
- football-data.org: 1 + pruebas (6 por defecto). Sin límite diario; 10/min.
- API-Football: /status (no consume cuota) + /leagues (1) + pruebas (3 por defecto),
  limitado por --max-af-calls.
- StatsBomb: 1 descarga.

Salida: docs/perfiles/cobertura.md y respuestas crudas en data/samples/<fuente>/discovery/.
"""

from __future__ import annotations

import argparse
import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from scripts.explore._common import (
    CANDIDATES,
    PROFILES_DIR,
    api_football_client,
    football_data_client,
    save_raw,
    setup,
    statsbomb_client,
)
from src.clients.base_client import ApiError
from src.clients.budget import BudgetExceededError

logger = logging.getLogger("discover_coverage")

# Temporadas probadas: actual, anterior, la ventana 2022-2024 (donde puede haber solapamiento
# con API-Football) y temporadas en las que StatsBomb tiene datos.
DEFAULT_FD_PROBES = [
    "PL:current",
    "PL:previous",
    "PL:2024",
    "PL:2023",
    "PL:2015",
    "PD:current",
    "PD:previous",
    "PD:2024",
    "PD:2020",
]
DEFAULT_AF_PROBES = ["39:current", "39:2024", "39:2015", "140:2024", "140:2020"]
AF_MIN_YEAR_SHOWN = 2015


@dataclass
class ProbeResult:
    source: str
    competition: str
    season: int
    ok: bool
    detail: str


def resolve_season(token: str, current: int | None) -> int:
    if token == "current":
        if current is None:
            raise ValueError("No se conoce la temporada actual")
        return current
    if token == "previous":
        if current is None:
            raise ValueError("No se conoce la temporada actual")
        return current - 1
    return int(token)


def short_error(exc: Exception) -> str:
    return str(exc).replace("\n", " ").replace("|", "/")[:160]


# --- football-data.org -------------------------------------------------------------------------


def discover_football_data(probes: list[str]) -> dict[str, Any]:
    client = football_data_client()
    payload = client.competitions()
    save_raw("football_data", "discovery", "competitions", payload)
    competitions = {c["code"]: c for c in payload["competitions"]}

    results: list[ProbeResult] = []
    for probe in probes:
        code, token = probe.split(":")
        current_start = (competitions.get(code, {}).get("currentSeason") or {}).get("startDate")
        current = int(current_start[:4]) if current_start else None
        season = resolve_season(token, current)
        try:
            data = client.standings(code, season=season)
            save_raw("football_data", "discovery", f"standings_{code}_{season}", data)
            table = (data.get("standings") or [{}])[0].get("table", [])
            results.append(
                ProbeResult("football-data", code, season, True, f"{len(table)} equipos")
            )
        except ApiError as exc:
            results.append(ProbeResult("football-data", code, season, False, short_error(exc)))

    headers = client.last_response.headers if client.last_response is not None else {}
    quota_headers = {k: v for k, v in headers.items() if "request" in k.lower()}
    return {"competitions": payload["competitions"], "probes": results, "headers": quota_headers}


# --- API-Football ------------------------------------------------------------------------------


def coverage_code(coverage: dict) -> str:
    fixtures = coverage.get("fixtures") or {}
    flags = [
        ("E", fixtures.get("events")),
        ("L", fixtures.get("lineups")),
        ("S", fixtures.get("statistics_fixtures")),
        ("P", fixtures.get("statistics_players")),
        ("I", coverage.get("injuries")),
    ]
    return "".join(letter if value else "·" for letter, value in flags)


def discover_api_football(probes: list[str], max_calls: int) -> dict[str, Any]:
    client, daily, run_cap = api_football_client(max_calls)
    status_before = client.sync_budget(daily)
    logger.info("API-Football: uso de hoy antes de empezar %s", status_before["requests"])

    leagues = client.get_payload("leagues")
    save_raw("api_football", "discovery", "leagues", leagues)
    by_id = {item["league"]["id"]: item for item in leagues["response"]}
    quota_headers = _ratelimit_headers(client.last_response)

    results: list[ProbeResult] = []
    for probe in probes:
        league_token, season_token = probe.split(":")
        league_id = int(league_token)
        seasons = (by_id.get(league_id) or {}).get("seasons", [])
        current = next((s["year"] for s in seasons if s.get("current")), None)
        season = resolve_season(season_token, current)
        try:
            data = client.get_payload("standings", {"league": league_id, "season": season})
            save_raw("api_football", "discovery", f"standings_{league_id}_{season}", data)
            results.append(
                ProbeResult(
                    "API-Football", str(league_id), season, True, f"{data['results']} tabla(s)"
                )
            )
        except ApiError as exc:
            results.append(
                ProbeResult("API-Football", str(league_id), season, False, short_error(exc))
            )
        except BudgetExceededError as exc:
            logger.warning("Se detienen las pruebas de API-Football: %s", exc)
            break
        quota_headers.update(_ratelimit_headers(client.last_response))

    status_after = client.sync_budget(daily)
    return {
        "leagues": by_id,
        "probes": results,
        "headers": quota_headers,
        "status": status_after,
        "calls": run_cap.used,
        "local_used": daily.used(),
    }


def _ratelimit_headers(response: Any) -> dict[str, str]:
    if response is None:
        return {}
    return {k: v for k, v in response.headers.items() if "ratelimit" in k.lower()}


# --- StatsBomb ---------------------------------------------------------------------------------


def discover_statsbomb() -> list[dict]:
    rows = statsbomb_client().competitions()
    save_raw("statsbomb", "discovery", "competitions", rows)
    return rows


# --- Informe -----------------------------------------------------------------------------------


def statsbomb_seasons(rows: list[dict], competition_id: int) -> list[str]:
    seasons = [r for r in rows if r["competition_id"] == competition_id]
    seasons.sort(key=lambda r: r["season_name"])
    return [r["season_name"] + (" (360)" if r.get("match_available_360") else "") for r in seasons]


def af_seasons_compact(league: dict | None) -> str:
    if not league:
        return "no encontrada"
    parts = []
    for season in sorted(league["seasons"], key=lambda s: s["year"]):
        if season["year"] < AF_MIN_YEAR_SHOWN:
            continue
        mark = "*" if season.get("current") else ""
        parts.append(f"{season['year']}{mark} `{coverage_code(season.get('coverage') or {})}`")
    return ", ".join(parts)


def render_report(fd: dict, af: dict, sb_rows: list[dict]) -> str:
    fd_by_code = {c["code"]: c for c in fd["competitions"]}
    now = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Cobertura de fuentes (Fase 1, paso A)",
        "",
        f"> Generado por `scripts/explore/discover_coverage.py` el {now}. "
        "Se regenera en cada ejecución: no editar a mano.",
        "",
        "## Resumen por competición candidata",
        "",
        "| Competición | football-data: plan · temporada actual | StatsBomb: temporadas |",
        "|---|---|---|",
    ]
    for cand in CANDIDATES:
        comp = fd_by_code.get(cand.fd_code)
        if comp:
            season = comp.get("currentSeason") or {}
            fd_text = f"{comp.get('plan')} · {season.get('startDate')} → {season.get('endDate')}"
        else:
            fd_text = "no visible"
        sb_text = ", ".join(statsbomb_seasons(sb_rows, cand.sb_competition_id)) or "—"
        lines.append(f"| {cand.name} | {fd_text} | {sb_text} |")

    lines += [
        "",
        "## API-Football: temporadas y cobertura por liga",
        "",
        f"Temporadas desde {AF_MIN_YEAR_SHOWN}; `*` = temporada actual. Cobertura: "
        "`E` eventos, `L` alineaciones, `S` estadísticas de partido, `P` estadísticas de "
        "jugador, `I` lesiones (`·` = no disponible).",
        "",
        "| Competición | Liga (id) | Temporadas |",
        "|---|---|---|",
    ]
    for cand in CANDIDATES:
        league = af["leagues"].get(cand.af_league_id)
        name = f"{league['league']['name']} ({cand.af_league_id})" if league else "—"
        lines.append(f"| {cand.name} | {name} | {af_seasons_compact(league)} |")

    lines += [
        "",
        "## Pruebas de acceso por temporada",
        "",
        "Consulta de la tabla de posiciones de una temporada concreta: muestra si el plan "
        "gratuito da acceso a ella.",
        "",
        "| Fuente | Competición | Temporada | Acceso | Detalle |",
        "|---|---|---|---|---|",
    ]
    for probe in fd["probes"] + af["probes"]:
        mark = "✅" if probe.ok else "❌"
        lines.append(
            f"| {probe.source} | {probe.competition} | {probe.season} | {mark} | {probe.detail} |"
        )

    lines += [
        "",
        f"## football-data.org: competiciones visibles ({len(fd['competitions'])})",
        "",
        "| Código | Nombre | Tipo | Plan | Temporada actual | Temporadas disponibles |",
        "|---|---|---|---|---|---|",
    ]
    for comp in sorted(fd["competitions"], key=lambda c: (c.get("plan") or "", c["code"])):
        season = comp.get("currentSeason") or {}
        lines.append(
            f"| {comp['code']} | {comp['name']} | {comp.get('type')} | {comp.get('plan')} | "
            f"{season.get('startDate')} → {season.get('endDate')} | "
            f"{comp.get('numberOfAvailableSeasons')} |"
        )

    requests_info = af["status"]["requests"]
    lines += [
        "",
        "## Cuotas observadas",
        "",
        f"- API-Football: {af['calls']} llamadas con cuota en esta ejecución (sin contar "
        f"`/status`). Uso del día según el contador local: {af['local_used']}; según la "
        f"API: {requests_info['current']}/{requests_info['limit_day']}.",
        f"- Headers de cuota de API-Football: `{af['headers']}`",
        f"- Headers de cuota de football-data.org: `{fd['headers']}`",
        "",
        "## StatsBomb: todas las competiciones disponibles",
        "",
        "| Id | Competición | País | Género | Temporadas |",
        "|---|---|---|---|---|",
    ]
    grouped: dict[int, dict] = {}
    for row in sb_rows:
        grouped.setdefault(row["competition_id"], row)
    for comp_id, row in sorted(grouped.items()):
        seasons = ", ".join(statsbomb_seasons(sb_rows, comp_id))
        lines.append(
            f"| {comp_id} | {row['competition_name']} | {row['country_name']} | "
            f"{row['competition_gender']} | {seasons} |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--fd-probe", action="append", help="p. ej. PL:2015 (repetible)")
    parser.add_argument("--af-probe", action="append", help="p. ej. 39:2015 (repetible)")
    parser.add_argument(
        "--max-af-calls", type=int, default=8, help="tope de llamadas a API-Football"
    )
    args = parser.parse_args()

    setup()
    fd = discover_football_data(args.fd_probe or DEFAULT_FD_PROBES)
    af = discover_api_football(args.af_probe or DEFAULT_AF_PROBES, args.max_af_calls)
    sb_rows = discover_statsbomb()

    PROFILES_DIR.mkdir(parents=True, exist_ok=True)
    report_path = PROFILES_DIR / "cobertura.md"
    report_path.write_text(render_report(fd, af, sb_rows), encoding="utf-8")
    logger.info("Informe generado en %s", report_path)


if __name__ == "__main__":
    main()
