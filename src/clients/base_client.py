"""Cliente HTTP base: rate limiting, reintentos con backoff exponencial y presupuesto.

Los clientes de cada fuente heredan de `ApiClient` y solo definen URL base, headers y
endpoints. Nunca se registran headers en el log (contienen las API keys).
"""

from __future__ import annotations

import logging
import random
import time
from collections import deque
from collections.abc import Callable, Mapping, Sequence
from typing import Any

import requests

from src.clients.budget import CallBudget

logger = logging.getLogger(__name__)

RETRYABLE_STATUS_CODES = frozenset({429, 500, 502, 503, 504})


class ApiError(RuntimeError):
    """Respuesta no exitosa después de agotar los reintentos."""

    def __init__(self, message: str, status_code: int | None = None, url: str | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.url = url


class RateLimiter:
    """Ventana deslizante: como máximo `max_calls` llamadas en `period_seconds`."""

    def __init__(
        self,
        max_calls: int,
        period_seconds: float = 60.0,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self.max_calls = max_calls
        self.period_seconds = period_seconds
        self._clock = clock
        self._sleep = sleep
        self._calls: deque[float] = deque()

    def acquire(self) -> None:
        now = self._clock()
        while self._calls and now - self._calls[0] >= self.period_seconds:
            self._calls.popleft()
        if len(self._calls) >= self.max_calls:
            wait = self.period_seconds - (now - self._calls[0])
            logger.info("Rate limit local: esperando %.1f s", wait)
            self._sleep(wait)
            self._calls.popleft()
            now = self._clock()
        self._calls.append(now)


class ApiClient:
    def __init__(
        self,
        base_url: str,
        *,
        headers: Mapping[str, str] | None = None,
        rate_limiter: RateLimiter | None = None,
        budgets: Sequence[CallBudget] = (),
        max_retries: int = 4,
        backoff_base_seconds: float = 2.0,
        backoff_max_seconds: float = 60.0,
        timeout_seconds: float = 30.0,
        retry_after_headers: Sequence[str] = ("Retry-After",),
        session: requests.Session | None = None,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.rate_limiter = rate_limiter
        self.budgets = list(budgets)
        self.max_retries = max_retries
        self.backoff_base_seconds = backoff_base_seconds
        self.backoff_max_seconds = backoff_max_seconds
        self.timeout_seconds = timeout_seconds
        self.retry_after_headers = retry_after_headers
        self._sleep = sleep
        self.session = session or requests.Session()
        if headers:
            self.session.headers.update(headers)
        self.calls_made = 0  # todas las peticiones HTTP
        self.billable_calls = 0  # solo las que consumen presupuesto (p. ej. sin /status)
        # Última respuesta recibida: permite leer headers de cuota (p. ej. llamadas restantes).
        self.last_response: requests.Response | None = None

    def _consume_budgets(self) -> None:
        # Se verifica todo antes de consumir, para no descontar de un presupuesto si otro está
        # agotado.
        for budget in self.budgets:
            if budget.remaining() < 1:
                budget.consume(1)  # lanza BudgetExceededError con el detalle
        for budget in self.budgets:
            budget.consume(1)

    def _backoff_seconds(self, attempt: int, response: requests.Response | None) -> float:
        if response is not None:
            for header in self.retry_after_headers:
                value = response.headers.get(header)
                if value is not None:
                    try:
                        return min(float(value), self.backoff_max_seconds)
                    except ValueError:
                        pass
        delay = self.backoff_base_seconds * (2**attempt)
        jitter = random.uniform(0, self.backoff_base_seconds)
        return min(delay + jitter, self.backoff_max_seconds)

    def get(
        self,
        path: str,
        params: Mapping[str, Any] | None = None,
        *,
        consume_budget: bool = True,
    ) -> requests.Response:
        """GET con reintentos. Cada intento cuenta contra el presupuesto."""
        url = f"{self.base_url}/{path.lstrip('/')}"
        for attempt in range(self.max_retries + 1):
            if consume_budget:
                self._consume_budgets()
                self.billable_calls += 1
            if self.rate_limiter:
                self.rate_limiter.acquire()

            response: requests.Response | None = None
            try:
                logger.debug("GET %s params=%s (intento %d)", url, params, attempt + 1)
                response = self.session.get(url, params=params, timeout=self.timeout_seconds)
                self.calls_made += 1
                self.last_response = response
            except (requests.ConnectionError, requests.Timeout) as exc:
                self.calls_made += 1
                reason = type(exc).__name__
            else:
                if response.ok:
                    return response
                if response.status_code not in RETRYABLE_STATUS_CODES:
                    raise ApiError(
                        f"HTTP {response.status_code} en {url}: {response.text[:300]}",
                        status_code=response.status_code,
                        url=url,
                    )
                reason = f"HTTP {response.status_code}"

            if attempt == self.max_retries:
                raise ApiError(
                    f"{reason} en {url} tras {self.max_retries + 1} intentos",
                    status_code=response.status_code if response is not None else None,
                    url=url,
                )
            wait = self._backoff_seconds(attempt, response)
            logger.warning("%s en %s; reintento en %.1f s", reason, url, wait)
            self._sleep(wait)

        raise AssertionError("inalcanzable")  # pragma: no cover

    def get_json(
        self,
        path: str,
        params: Mapping[str, Any] | None = None,
        *,
        consume_budget: bool = True,
    ) -> Any:
        return self.get(path, params, consume_budget=consume_budget).json()
