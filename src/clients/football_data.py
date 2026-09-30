"""Cliente de football-data.org (API v4).

Plan gratuito: 10 llamadas por minuto. Si la API responde 429, el header
`X-RequestCounter-Reset` indica los segundos hasta que se reinicia el contador.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from src.clients.base_client import ApiClient, RateLimiter
from src.clients.budget import CallBudget

DEFAULT_BASE_URL = "https://api.football-data.org/v4"


class FootballDataClient(ApiClient):
    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        calls_per_minute: int = 10,
        budgets: Sequence[CallBudget] = (),
        **kwargs: Any,
    ) -> None:
        super().__init__(
            base_url,
            headers={"X-Auth-Token": api_key},
            rate_limiter=RateLimiter(max_calls=calls_per_minute, period_seconds=60),
            budgets=budgets,
            retry_after_headers=("Retry-After", "X-RequestCounter-Reset"),
            **kwargs,
        )

    def competitions(self) -> dict:
        return self.get_json("competitions")

    def competition(self, code: str) -> dict:
        return self.get_json(f"competitions/{code}")

    def teams(self, code: str, season: int | None = None) -> dict:
        return self.get_json(f"competitions/{code}/teams", _clean({"season": season}))

    def matches(
        self,
        code: str,
        *,
        season: int | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        status: str | None = None,
        matchday: int | None = None,
    ) -> dict:
        params = {
            "season": season,
            "dateFrom": date_from,
            "dateTo": date_to,
            "status": status,
            "matchday": matchday,
        }
        return self.get_json(f"competitions/{code}/matches", _clean(params))

    def standings(self, code: str, season: int | None = None) -> dict:
        return self.get_json(f"competitions/{code}/standings", _clean({"season": season}))

    def scorers(self, code: str, season: int | None = None, limit: int | None = None) -> dict:
        params = {"season": season, "limit": limit}
        return self.get_json(f"competitions/{code}/scorers", _clean(params))

    def match(self, match_id: int) -> dict:
        return self.get_json(f"matches/{match_id}")

    def team(self, team_id: int) -> dict:
        return self.get_json(f"teams/{team_id}")

    def person(self, person_id: int) -> dict:
        return self.get_json(f"persons/{person_id}")


def _clean(params: dict[str, Any]) -> dict[str, Any]:
    """Quita los parámetros sin valor para no enviarlos vacíos."""
    return {key: value for key, value in params.items() if value is not None}
