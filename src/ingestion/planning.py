"""Planificación de cargas incrementales: ventanas de fechas y objetivos pendientes."""

from __future__ import annotations

import json
from datetime import date, timedelta


def compute_window(
    *,
    watermark: date | None,
    today: date,
    season_start: date,
    season_end: date,
    lookback_days: int,
    lookahead_days: int,
) -> tuple[date, date]:
    """Ventana [desde, hasta] para la carga por fechas.

    - Primera ejecución (sin watermark): desde el inicio de la temporada.
    - Siguientes: desde el watermark menos `lookback_days`, para recoger partidos reprogramados
      o resultados corregidos (datos tardíos). El MERGE de Bronze descarta lo que no cambió.
    - Hasta hoy más `lookahead_days`, para tener los próximos partidos programados.
    Siempre acotada a la temporada.
    """
    start = season_start if watermark is None else watermark - timedelta(days=lookback_days)
    start = max(start, season_start)
    end = min(today + timedelta(days=lookahead_days), season_end)
    return start, max(end, start)


def target_key(target: dict) -> str:
    """Clave estable de un objetivo, p. ej. 'competition=PL|season=2024'."""
    return "|".join(f"{k}={target[k]}" for k in sorted(target))


def parse_completed(watermark: str | None) -> set[str]:
    """El watermark de season_full es la lista JSON de objetivos ya completados."""
    return set(json.loads(watermark)) if watermark else set()


def pending_targets(targets: list[dict], completed: set[str]) -> list[dict]:
    """Objetivos por cargar: los no completados y siempre los de la temporada en curso."""
    return [t for t in targets if t.get("season") == "current" or target_key(t) not in completed]


def mark_completed(completed: set[str], targets: list[dict]) -> str:
    """Añade las temporadas cerradas (no 'current') al watermark y lo serializa."""
    closed = {target_key(t) for t in targets if t.get("season") != "current"}
    return json.dumps(sorted(completed | closed))
