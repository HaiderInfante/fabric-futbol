"""Utilidades compartidas por los scripts de exploración (Fase 1)."""

from __future__ import annotations

import json
import logging
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from src.clients.api_football import ApiFootballClient
from src.clients.budget import InMemoryBudget, LocalFileBudget
from src.clients.football_data import FootballDataClient
from src.clients.statsbomb import StatsBombClient

REPO_ROOT = Path(__file__).resolve().parents[2]
SAMPLES_DIR = REPO_ROOT / "data" / "samples"
PROFILES_DIR = REPO_ROOT / "docs" / "perfiles"
BUDGET_FILE = REPO_ROOT / ".state" / "api_budget.json"

API_FOOTBALL_DAILY_LIMIT = 100
API_FOOTBALL_RESERVE = 10  # margen que ningún script de exploración puede tocar


@dataclass(frozen=True)
class Candidate:
    """Competición candidata con su identificador en cada fuente."""

    name: str
    fd_code: str  # football-data.org
    af_league_id: int  # API-Football
    sb_competition_id: int  # StatsBomb


CANDIDATES = [
    Candidate("Premier League", "PL", 39, 2),
    Candidate("La Liga", "PD", 140, 11),
    Candidate("Bundesliga", "BL1", 78, 9),
    Candidate("Serie A", "SA", 135, 12),
    Candidate("Ligue 1", "FL1", 61, 7),
    Candidate("Champions League", "CL", 2, 16),
    Candidate("FIFA World Cup", "WC", 1, 43),
    Candidate("UEFA Euro", "EC", 4, 55),
]


@dataclass(frozen=True)
class ScopeEntry:
    """Competición y temporadas elegidas por fuente (ADR-005)."""

    name: str
    fd_code: str
    fd_seasons: tuple[int | str, ...]  # año de inicio o "current"
    af_league_id: int
    af_season: int
    sb_competition_id: int
    sb_season_id: int


SELECTED_SCOPE = [
    ScopeEntry("Premier League", "PL", (2024, "current"), 39, 2024, 2, 27),
    ScopeEntry("La Liga", "PD", (2024, "current"), 140, 2024, 11, 90),
    ScopeEntry("UEFA Euro 2024", "EC", (2024,), 4, 2024, 55, 282),
]


def setup() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")  # logging escribe en stderr
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )
    load_dotenv(REPO_ROOT / ".env")


def require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise SystemExit(f"Falta {name} en .env")
    return value


def football_data_client() -> FootballDataClient:
    return FootballDataClient(require_env("FOOTBALL_DATA_API_KEY"))


def api_football_client(
    max_calls: int,
) -> tuple[ApiFootballClient, LocalFileBudget, InMemoryBudget]:
    """Cliente con dos presupuestos: el diario (persistido) y un tope para esta ejecución."""
    daily = LocalFileBudget(
        BUDGET_FILE,
        "api_football",
        daily_limit=API_FOOTBALL_DAILY_LIMIT,
        reserve=API_FOOTBALL_RESERVE,
    )
    run_cap = InMemoryBudget(limit=max_calls, name="ejecución")
    client = ApiFootballClient(
        require_env("API_FOOTBALL_API_KEY"), daily_budget=daily, budgets=[run_cap]
    )
    return client, daily, run_cap


def statsbomb_client() -> StatsBombClient:
    return StatsBombClient()


def save_raw(source: str, entity: str, name: str, payload: Any) -> Path:
    """Guarda la respuesta cruda tal cual en data/samples/<fuente>/<entidad>/<name>.json."""
    path = SAMPLES_DIR / source / entity / f"{name}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return path
