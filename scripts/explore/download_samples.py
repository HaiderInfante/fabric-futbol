"""Fase 1, paso B: descarga muestras crudas de las competiciones elegidas (ADR-005).

Uso (desde la raíz del repo):
    python -m scripts.explore.download_samples --dry-run
    python -m scripts.explore.download_samples --source all --max-af-calls 25

Guarda cada respuesta tal cual en data/samples/<fuente>/<entidad>/<nombre>.json (ignorado por
Git: el repo es público y no redistribuimos datos).

Incluye una prueba de `/fixtures?ids=` de API-Football: un lote de partidos en una sola llamada,
comparado con las llamadas por partido (estadísticas, alineaciones, eventos, jugadores).
"""

from __future__ import annotations

import argparse
import logging

from scripts.explore._common import (
    SELECTED_SCOPE,
    ScopeEntry,
    api_football_client,
    football_data_client,
    save_raw,
    setup,
    statsbomb_client,
)
from src.clients.api_football import ApiFootballClient
from src.clients.base_client import ApiError
from src.clients.budget import BudgetExceededError
from src.clients.football_data import FootballDataClient
from src.clients.statsbomb import StatsBombClient

logger = logging.getLogger("download_samples")

SB_MATCHES_PER_COMPETITION = 2
AF_BATCH_SIZE = 3  # partidos en la prueba de /fixtures?ids=

# Estimación de llamadas para --dry-run (API-Football es la única con límite diario).
# Nota: el plan gratuito rechaza el parámetro `ids` ("Free plans do not have access to the Ids
# parameter"); la prueba queda para documentar el hallazgo y la llamada no consume cuota.
AF_CALLS_PRINCIPAL = 11  # fixtures, lote ids, 4 por partido, teams, 2 págs. players, etc.
AF_CALLS_SECONDARY = 4  # fixtures, lote ids, teams, 1 pág. players


# --- football-data.org -------------------------------------------------------------------------


def download_football_data(client: FootballDataClient, entry: ScopeEntry) -> None:
    code = entry.fd_code
    current_start = (client.competition(code).get("currentSeason") or {}).get("startDate", "")
    seasons = sorted(
        {int(current_start[:4]) if s == "current" else int(s) for s in entry.fd_seasons}
    )
    last_matches: dict = {}
    for season in seasons:
        last_matches = client.matches(code, season=season)
        save_raw("football_data", "matches", f"{code}_{season}", last_matches)
        save_raw("football_data", "teams", f"{code}_{season}", client.teams(code, season=season))

    historical = seasons[0]
    try:
        standings = client.standings(code, historical)
        save_raw("football_data", "standings", f"{code}_{historical}", standings)
    except ApiError as exc:
        # Los torneos como la Euro no tienen tabla en football-data (HTTP 404).
        logger.warning("Sin standings para %s %s: %s", code, historical, exc)
    scorers = client.scorers(code, season=historical, limit=20)
    save_raw("football_data", "scorers", f"{code}_{historical}", scorers)

    finished = [m for m in last_matches.get("matches", []) if m.get("status") == "FINISHED"]
    if finished:
        match_id = finished[0]["id"]
        save_raw("football_data", "match_detail", str(match_id), client.match(match_id))
    if scorers.get("scorers"):
        person_id = scorers["scorers"][0]["player"]["id"]
        save_raw("football_data", "person", str(person_id), client.person(person_id))
        team_id = scorers["scorers"][0]["team"]["id"]
        save_raw("football_data", "team", str(team_id), client.team(team_id))


# --- API-Football ------------------------------------------------------------------------------


def download_api_football(client: ApiFootballClient, entry: ScopeEntry, principal: bool) -> None:
    league, season = entry.af_league_id, entry.af_season
    name = f"{league}_{season}"

    fixtures = client.get_payload("fixtures", {"league": league, "season": season})
    save_raw("api_football", "fixtures", name, fixtures)
    finished = sorted(
        (f for f in fixtures["response"] if f["fixture"]["status"]["short"] == "FT"),
        key=lambda f: f["fixture"]["date"],
    )
    ids = [f["fixture"]["id"] for f in finished[:AF_BATCH_SIZE]]

    if ids:
        try:
            batch = client.get_payload("fixtures", {"ids": "-".join(map(str, ids))})
            save_raw("api_football", "fixtures_by_ids", name, batch)
        except ApiError as exc:
            logger.error("La prueba de /fixtures?ids= falló: %s", exc)

    save_raw(
        "api_football",
        "teams",
        name,
        client.get_payload("teams", {"league": league, "season": season}),
    )

    pages = 2 if principal else 1
    for page in range(1, pages + 1):
        players = client.get_payload("players", {"league": league, "season": season, "page": page})
        save_raw("api_football", "players", f"{name}_p{page}", players)

    if not principal or not ids:
        return
    fixture_id = ids[0]
    for endpoint in ("statistics", "lineups", "events", "players"):
        payload = client.get_payload(f"fixtures/{endpoint}", {"fixture": fixture_id})
        save_raw("api_football", f"fixture_{endpoint}", str(fixture_id), payload)
    save_raw(
        "api_football",
        "injuries",
        name,
        client.get_payload("injuries", {"league": league, "season": season}),
    )
    save_raw(
        "api_football",
        "standings",
        name,
        client.get_payload("standings", {"league": league, "season": season}),
    )


# --- StatsBomb ---------------------------------------------------------------------------------


def download_statsbomb(client: StatsBombClient, entry: ScopeEntry) -> None:
    matches = client.matches(entry.sb_competition_id, entry.sb_season_id)
    save_raw("statsbomb", "matches", f"{entry.sb_competition_id}_{entry.sb_season_id}", matches)

    ordered = sorted(matches, key=lambda m: m["match_date"])
    # Primer y último partido de la temporada (en la Euro 2024, el último es la final).
    sample = [ordered[0], ordered[-1]][:SB_MATCHES_PER_COMPETITION]
    for match in sample:
        match_id = match["match_id"]
        save_raw("statsbomb", "events", str(match_id), client.events(match_id))
        save_raw("statsbomb", "lineups", str(match_id), client.lineups(match_id))
        three_sixty = client.three_sixty(match_id)
        if three_sixty is not None:
            save_raw("statsbomb", "three_sixty", str(match_id), three_sixty)


# --- Orquestación ------------------------------------------------------------------------------


def print_plan(max_af_calls: int) -> None:
    af_calls = AF_CALLS_PRINCIPAL + AF_CALLS_SECONDARY * (len(SELECTED_SCOPE) - 1)
    print("Plan de descarga (estimado):")
    for entry in SELECTED_SCOPE:
        print(
            f"- {entry.name}: football-data {entry.fd_code} {entry.fd_seasons}; "
            f"API-Football liga {entry.af_league_id} temporada {entry.af_season}; "
            f"StatsBomb {entry.sb_competition_id}/{entry.sb_season_id}"
        )
    print(f"API-Football: ~{af_calls} llamadas con cuota (tope --max-af-calls={max_af_calls})")
    print("football-data.org: ~10 llamadas por competición (10/min, sin límite diario)")
    print(
        f"StatsBomb: {SB_MATCHES_PER_COMPETITION} partidos por competición "
        "(eventos, alineaciones, 360)"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--source", choices=["football_data", "api_football", "statsbomb", "all"], default="all"
    )
    parser.add_argument("--max-af-calls", type=int, default=25)
    parser.add_argument("--dry-run", action="store_true", help="solo muestra el plan")
    args = parser.parse_args()

    setup()
    print_plan(args.max_af_calls)
    if args.dry_run:
        return

    if args.source in ("football_data", "all"):
        fd = football_data_client()
        for entry in SELECTED_SCOPE:
            logger.info("football-data: %s", entry.name)
            try:
                download_football_data(fd, entry)
            except ApiError as exc:
                logger.error("football-data, %s: %s", entry.name, exc)
        logger.info("football-data: %d llamadas", fd.calls_made)

    if args.source in ("api_football", "all"):
        af, daily, run_cap = api_football_client(args.max_af_calls)
        af.sync_budget(daily)
        for index, entry in enumerate(SELECTED_SCOPE):
            logger.info("API-Football: %s", entry.name)
            try:
                download_api_football(af, entry, principal=index == 0)
            except BudgetExceededError as exc:
                logger.warning("Descarga de API-Football detenida: %s", exc)
                break
            except ApiError as exc:
                logger.error("API-Football, %s: %s", entry.name, exc)
        status = af.sync_budget(daily)
        logger.info(
            "API-Football: %d llamadas con cuota; uso del día (local/API): %d/%s",
            run_cap.used,
            daily.used(),
            status["requests"]["current"],
        )

    if args.source in ("statsbomb", "all"):
        sb = statsbomb_client()
        for entry in SELECTED_SCOPE:
            logger.info("StatsBomb: %s", entry.name)
            download_statsbomb(sb, entry)
        logger.info("StatsBomb: %d descargas", sb.calls_made)


if __name__ == "__main__":
    main()
