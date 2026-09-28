"""Verifica el acceso a las fuentes de datos con una llamada mínima por fuente.

Uso:
    python scripts/check_access.py

Lee las keys desde .env (nunca las imprime). Llamadas que hace:
- football-data.org: GET /competitions (1 llamada del límite de 10/min).
- API-Football:      GET /status (según la documentación de api-sports, no consume
                     la cuota diaria; devuelve el uso actual de la cuenta).
- StatsBomb:         descarga data/competitions.json del repositorio open-data.

Código de salida: 0 si todas las fuentes responden; 1 si alguna falla o no tiene key.
"""

from __future__ import annotations

import os
import sys
from collections.abc import Callable
from dataclasses import dataclass

import requests
from dotenv import load_dotenv

TIMEOUT_SECONDS = 15

DEFAULT_FOOTBALL_DATA_BASE_URL = "https://api.football-data.org/v4"
DEFAULT_API_FOOTBALL_BASE_URL = "https://v3.football.api-sports.io"
DEFAULT_STATSBOMB_BASE_URL = "https://raw.githubusercontent.com/statsbomb/open-data/master/data"


@dataclass
class CheckResult:
    source: str
    status: str  # OK | FALLO | SIN KEY
    detail: str


def _get_env(name: str, default: str | None = None) -> str | None:
    """Devuelve la variable de entorno sin espacios; None si está vacía."""
    value = os.getenv(name, default)
    if value is None:
        return None
    value = value.strip()
    return value or None


def check_football_data() -> CheckResult:
    source = "football-data.org"
    api_key = _get_env("FOOTBALL_DATA_API_KEY")
    if not api_key:
        return CheckResult(source, "SIN KEY", "Completa FOOTBALL_DATA_API_KEY en .env")

    base_url = _get_env("FOOTBALL_DATA_BASE_URL", DEFAULT_FOOTBALL_DATA_BASE_URL)
    response = requests.get(
        f"{base_url}/competitions",
        headers={"X-Auth-Token": api_key},
        timeout=TIMEOUT_SECONDS,
    )
    if response.status_code != 200:
        return CheckResult(source, "FALLO", f"HTTP {response.status_code}: {response.text[:200]}")

    competitions = response.json().get("competitions", [])
    available = response.headers.get("X-Requests-Available-Minute", "?")
    return CheckResult(
        source,
        "OK",
        f"HTTP 200, {len(competitions)} competiciones visibles, "
        f"llamadas disponibles este minuto: {available}",
    )


def check_api_football() -> CheckResult:
    source = "API-Football"
    api_key = _get_env("API_FOOTBALL_API_KEY")
    if not api_key:
        return CheckResult(source, "SIN KEY", "Completa API_FOOTBALL_API_KEY en .env")

    base_url = _get_env("API_FOOTBALL_BASE_URL", DEFAULT_API_FOOTBALL_BASE_URL)
    response = requests.get(
        f"{base_url}/status",
        headers={"x-apisports-key": api_key},
        timeout=TIMEOUT_SECONDS,
    )
    if response.status_code != 200:
        return CheckResult(source, "FALLO", f"HTTP {response.status_code}: {response.text[:200]}")

    payload = response.json()
    # api-sports responde HTTP 200 incluso con key inválida: el error viene en "errors".
    errors = payload.get("errors")
    if errors:
        return CheckResult(source, "FALLO", f"HTTP 200 con errores: {errors}")

    status = payload.get("response") or {}
    requests_info = status.get("requests", {})
    plan = status.get("subscription", {}).get("plan", "?")
    return CheckResult(
        source,
        "OK",
        f"HTTP 200, plan {plan}, uso hoy: "
        f"{requests_info.get('current', '?')}/{requests_info.get('limit_day', '?')}",
    )


def check_statsbomb() -> CheckResult:
    source = "StatsBomb Open Data"
    base_url = _get_env("STATSBOMB_BASE_URL", DEFAULT_STATSBOMB_BASE_URL)
    response = requests.get(f"{base_url}/competitions.json", timeout=TIMEOUT_SECONDS)
    if response.status_code != 200:
        return CheckResult(source, "FALLO", f"HTTP {response.status_code}")

    rows = response.json()
    competitions = {row["competition_id"] for row in rows}
    return CheckResult(
        source,
        "OK",
        f"HTTP 200, {len(competitions)} competiciones y {len(rows)} temporadas disponibles",
    )


def run_check(check: Callable[[], CheckResult], source: str) -> CheckResult:
    """Ejecuta un chequeo sin dejar que un error de red detenga los demás."""
    try:
        return check()
    except requests.RequestException as exc:
        return CheckResult(source, "FALLO", f"Error de red: {type(exc).__name__}")
    except ValueError:
        return CheckResult(source, "FALLO", "La respuesta no es JSON válido")


def main() -> int:
    # Evita caracteres corruptos (tildes) al redirigir la salida en Windows.
    sys.stdout.reconfigure(encoding="utf-8")
    load_dotenv()
    checks = [
        (check_football_data, "football-data.org"),
        (check_api_football, "API-Football"),
        (check_statsbomb, "StatsBomb Open Data"),
    ]
    results = [run_check(check, source) for check, source in checks]

    print("Verificación de acceso a fuentes\n")
    for result in results:
        print(f"[{result.status:<7}] {result.source:<20} {result.detail}")

    all_ok = all(result.status == "OK" for result in results)
    print("\nResultado:", "todas las fuentes responden" if all_ok else "hay fuentes pendientes")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
