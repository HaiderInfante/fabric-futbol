"""Cliente de StatsBomb Open Data (archivos JSON en GitHub, sin key).

Estructura del repositorio `statsbomb/open-data` (rama master, carpeta data/):
competitions.json, matches/<competition_id>/<season_id>.json, events/<match_id>.json,
lineups/<match_id>.json y three-sixty/<match_id>.json (solo en algunos partidos).

Atribución obligatoria: cualquier análisis publicado con estos datos debe citar a StatsBomb.
"""

from __future__ import annotations

from typing import Any

from src.clients.base_client import ApiClient, ApiError, RateLimiter

DEFAULT_BASE_URL = "https://raw.githubusercontent.com/statsbomb/open-data/master/data"


class StatsBombClient(ApiClient):
    def __init__(
        self,
        *,
        base_url: str = DEFAULT_BASE_URL,
        calls_per_minute: int = 60,
        **kwargs: Any,
    ) -> None:
        # Sin límite publicado: 60/min es una cortesía con GitHub, no una restricción.
        super().__init__(
            base_url,
            rate_limiter=RateLimiter(max_calls=calls_per_minute, period_seconds=60),
            **kwargs,
        )

    def competitions(self) -> list[dict]:
        return self.get_json("competitions.json")

    def matches(self, competition_id: int, season_id: int) -> list[dict]:
        return self.get_json(f"matches/{competition_id}/{season_id}.json")

    def events(self, match_id: int) -> list[dict]:
        return self.get_json(f"events/{match_id}.json")

    def lineups(self, match_id: int) -> list[dict]:
        return self.get_json(f"lineups/{match_id}.json")

    def three_sixty(self, match_id: int) -> list[dict] | None:
        """Datos 360 del partido; None si el partido no los tiene."""
        try:
            return self.get_json(f"three-sixty/{match_id}.json")
        except ApiError as exc:
            if exc.status_code == 404:
                return None
            raise
