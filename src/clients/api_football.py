"""Cliente de API-Football (api-sports.io, v3), con registro directo, no RapidAPI.

Particularidades:
- Plan gratuito: 100 llamadas por día. Cada llamada (incluidos los reintentos) consume
  presupuesto, excepto `/status`, que según la documentación no cuenta en la cuota.
- La API puede responder HTTP 200 con errores en el campo `errors` (key inválida, temporada
  no incluida en el plan, parámetros incorrectos...). Se convierten en `ApiFootballError`.
- Paginación con `page` y el bloque `paging: {current, total}`.
- `/status` se actualiza con retraso; los headers `x-ratelimit-requests-limit/remaining` de
  cada respuesta son la señal más fiable del uso diario, y con ellos se sincroniza el
  presupuesto diario (`daily_budget`).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import requests

from src.clients.base_client import ApiClient, ApiError, RateLimiter
from src.clients.budget import CallBudget, SyncableBudget

DEFAULT_BASE_URL = "https://v3.football.api-sports.io"
DAILY_LIMIT_HEADER = "x-ratelimit-requests-limit"
DAILY_REMAINING_HEADER = "x-ratelimit-requests-remaining"


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
        daily_budget: SyncableBudget | None = None,
        budgets: Sequence[CallBudget] = (),
        **kwargs: Any,
    ) -> None:
        """`daily_budget` refleja la cuota del proveedor y se sincroniza con los headers;
        `budgets` son topes adicionales (p. ej. por ejecución) que no se sincronizan."""
        all_budgets = ([daily_budget] if daily_budget is not None else []) + list(budgets)
        super().__init__(
            base_url,
            headers={"x-apisports-key": api_key},
            rate_limiter=RateLimiter(max_calls=calls_per_minute, period_seconds=60),
            budgets=all_budgets,
            **kwargs,
        )
        self.daily_budget = daily_budget
        self.provider_used: int | None = None  # último uso diario leído de los headers

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
        self._sync_from_headers(response)
        payload = response.json()
        if payload.get("errors"):
            raise ApiFootballError(payload["errors"], url=response.url, status_code=200)
        return payload

    def _sync_from_headers(self, response: requests.Response) -> None:
        try:
            limit = int(response.headers[DAILY_LIMIT_HEADER])
            remaining = int(response.headers[DAILY_REMAINING_HEADER])
        except (KeyError, ValueError):
            return  # sin headers de cuota (p. ej. /status o respuestas de error)
        self.provider_used = limit - remaining
        if self.daily_budget is not None:
            self.daily_budget.sync_used(self.provider_used)

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

    def sync_budget(self, budget: SyncableBudget | None = None) -> dict:
        """Alinea el presupuesto (por defecto, `daily_budget`) con el uso que reporta /status."""
        status = self.status()
        target = budget if budget is not None else self.daily_budget
        if target is not None:
            target.sync_used(int(status["requests"]["current"]))
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
