"""De respuesta cruda a registros Bronze: qué es un registro, su clave y su hash.

Cada registro Bronze guarda el JSON tal cual (`payload`) más:
- record_key: clave natural de la entidad (ver docs/diccionario_datos.md).
- record_hash: SHA-256 del registro SIN los campos volátiles, que cambian en cada refresco
  aunque el dato no cambie (p. ej. `lastUpdated` de football-data). Así el hash solo cambia
  cuando cambia el contenido.
- record_context: JSON con el contexto de la petición (competición, temporada…) que el
  registro no trae dentro.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

VOLATILE_KEYS: dict[str, frozenset[str]] = {
    "football_data": frozenset({"lastUpdated", "currentMatchday"}),
    "api_football": frozenset({"update"}),
    "statsbomb": frozenset(),
}


@dataclass(frozen=True)
class BronzeRecord:
    record_key: str
    record_hash: str
    record_context: str
    payload: str


def _strip(value: Any, volatile: frozenset[str]) -> Any:
    if isinstance(value, dict):
        return {k: _strip(v, volatile) for k, v in value.items() if k not in volatile}
    if isinstance(value, list):
        return [_strip(v, volatile) for v in value]
    return value


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def stable_hash(record: Any, volatile: frozenset[str] = frozenset()) -> str:
    return hashlib.sha256(canonical_json(_strip(record, volatile)).encode("utf-8")).hexdigest()


# --- Reglas por fuente y entidad: payload + contexto → [(clave, registro)] ------------------

Rule = Callable[[Any, dict], list[tuple[str, Any]]]


def _season_doc_key(payload: dict, _: dict) -> list[tuple[str, Any]]:
    """Documento completo (tabla de posiciones, goleadores): una versión por competición y
    temporada."""
    key = f"{payload['competition']['code']}|{payload['season']['id']}"
    return [(key, payload)]


RULES: dict[tuple[str, str], Rule] = {
    ("football_data", "competitions"): lambda p, _: [(str(c["id"]), c) for c in p["competitions"]],
    ("football_data", "matches"): lambda p, _: [(str(m["id"]), m) for m in p["matches"]],
    ("football_data", "teams"): lambda p, _: [
        (f"{p['season']['id']}|{t['id']}", t) for t in p["teams"]
    ],
    ("football_data", "standings"): _season_doc_key,
    ("football_data", "scorers"): _season_doc_key,
    # API-Football: el sobre (get/parameters/errors/paging) queda en el archivo crudo; los
    # registros son los elementos de `response`.
    ("api_football", "fixtures"): lambda p, _: [
        (str(r["fixture"]["id"]), r) for r in p["response"]
    ],
    ("api_football", "teams"): lambda p, ctx: [
        (f"{ctx['league']}|{ctx['season']}|{r['team']['id']}", r) for r in p["response"]
    ],
    ("api_football", "injuries"): lambda p, _: [
        (f"{r['player']['id']}|{r['fixture']['id']}", r) for r in p["response"]
    ],
    ("api_football", "players"): lambda p, ctx: [
        (f"{ctx['league']}|{ctx['season']}|{r['player']['id']}", r) for r in p["response"]
    ],
    # Por partido: un documento con los dos equipos (estadísticas o jugadores)
    ("api_football", "fixture_statistics"): lambda p, ctx: [
        (str(ctx["fixture_id"]), p["response"])
    ],
    ("api_football", "fixture_players"): lambda p, ctx: [(str(ctx["fixture_id"]), p["response"])],
    ("statsbomb", "competitions"): lambda p, _: [
        (f"{c['competition_id']}|{c['season_id']}", c) for c in p
    ],
    ("statsbomb", "matches"): lambda p, _: [(str(m["match_id"]), m) for m in p],
    ("statsbomb", "events"): lambda p, _: [(e["id"], e) for e in p],
    ("statsbomb", "lineups"): lambda p, ctx: [(f"{ctx['match_id']}|{t['team_id']}", t) for t in p],
    ("statsbomb", "three_sixty"): lambda p, _: [(f["event_uuid"], f) for f in p],
}


def extract_records(source: str, entity: str, payload: Any, context: dict) -> list[BronzeRecord]:
    try:
        rule = RULES[(source, entity)]
    except KeyError as exc:
        raise ValueError(f"No hay regla de registros para {source}/{entity}") from exc
    volatile = VOLATILE_KEYS.get(source, frozenset())
    context_json = canonical_json(context)
    return [
        BronzeRecord(
            record_key=key,
            record_hash=stable_hash(record, volatile),
            record_context=context_json,
            payload=json.dumps(record, ensure_ascii=False),
        )
        for key, record in rule(payload, context)
    ]
