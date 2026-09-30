"""Cliente de API-Football (api-sports.io, v3), con registro directo, no RapidAPI.

Particularidades:
- Plan gratuito: 100 llamadas por día. Cada llamada (incluidos los reintentos) consume
  presupuesto, excepto `/status`, que según la documentación no cuenta en la cuota.
- La API puede responder HTTP 200 con errores en el campo `errors` (key inválida, temporada
  no incluida en el plan, parámetros incorrectos...). Se convierten en `ApiFootballError`.
- Paginación con `page` y el bloque `paging: {current, total}`.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from src.clients.base_client import ApiClient, ApiError, RateLimiter
from src.clients.budget import CallBudget, LocalFileBudget

DEFAULT_BASE_URL = "https://v3.football.api-sports.io"


class ApiFootballError(ApiError):
    """La API respondió con errores en el cuerpo."""

    def __init__(self, errors: Any, url: str | None = None, status_code: int | None = None):
        super().__init__(f"API-Football devolvió errores: {errors}", status_code, url)
        self.errors = errors


class ApiFootballClient(ApiClient):
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
            headers={"x-apisports-key": api_key},
            rate_limiter=RateLimiter(max_calls=calls_per_minute, period_seconds=60),
            budgets=budgets,
            **kwargs,
        )

    def get_payload(
        self,
        path: str,
        params: Mapping[str, Any] | None = None,
        *,
        consume_budget: bool = True,
    ) -> dict:
        """Devuelve el cuerpo completo (con `response`, `paging`, etc.) validando `errors`.

        Los 4xx (p. ej. key inválida) los lanza `ApiClient.get` como `ApiError`, con el cuerpo
        en el mensaje.
        """
        response = self.get(path, params, consume_budget=consume_budget)
        payload = response.json()
        if payload.get("errors"):
            raise ApiFootballError(payload["errors"], url=response.url, status_code=200)
        return payload

    def get_response(self, path: str, params: Mapping[str, Any] | None = None) -> list:
        return self.get_payload(path, params)["response"]

    def get_all_pages(
        self,
        path: str,
        params: Mapping[str, Any] | None = None,
        max_pages: int | None = None,
    ) -> list:
        """Recorre todas las páginas; `max_pages` acota el gasto de presupuesto."""
        results: list = []
        page = 1
        while True:
            payload = self.get_payload(path, {**(params or {}), "page": page})
            results.extend(payload["response"])
            paging = payload.get("paging") or {}
            if page >= int(paging.get("total", 1)):
                return results
            if max_pages is not None and page >= max_pages:
                return results
            page += 1

    # --- Endpoints -------------------------------------------------------------------------

    def status(self) -> dict:
        """Estado de la cuenta y uso del día. No consume presupuesto."""
        return self.get_payload("status", consume_budget=False)["response"]

    def sync_budget(self, budget: LocalFileBudget) -> dict:
        """Alinea el contador local con el uso diario que reporta la API."""
        status = self.status()
        budget.sync_used(int(status["requests"]["current"]))
        return status

    def leagues(self, **params: Any) -> list:
        return self.get_response("leagues", params)

    def teams(self, league: int, season: int) -> list:
        return self.get_response("teams", {"league": league, "season": season})

    def standings(self, league: int, season: int) -> list:
        return self.get_response("standings", {"league": league, "season": season})

    def fixtures(self, **params: Any) -> list:
        return self.get_response("fixtures", params)

    def fixture_statistics(self, fixture_id: int) -> list:
        return self.get_response("fixtures/statistics", {"fixture": fixture_id})

    def fixture_lineups(self, fixture_id: int) -> list:
        return self.get_response("fixtures/lineups", {"fixture": fixture_id})

    def fixture_events(self, fixture_id: int) -> list:
        return self.get_response("fixtures/events", {"fixture": fixture_id})

    def fixture_players(self, fixture_id: int) -> list:
        return self.get_response("fixtures/players", {"fixture": fixture_id})

    def injuries(self, **params: Any) -> list:
        return self.get_response("injuries", params)
