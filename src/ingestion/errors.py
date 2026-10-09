"""Clasificación de errores de ingesta: ¿sirve reintentar?

- Permanente: reintentar repite el mismo error y gasta cuota (errores de plan de API-Football
  que llegan con HTTP 200, 4xx salvo 429, configuración sin handler). El notebook lo registra
  como `failed` y termina sin excepción; la pipeline lo marca con una actividad Fail, que no
  reintenta.
- Transitorio: red, 5xx, 429 tras agotar los reintentos del cliente. El notebook lanza la
  excepción para que actúe el `retry` de la actividad (ADR-010).
"""

from __future__ import annotations

from src.clients.api_football import ApiFootballError
from src.clients.base_client import ApiError


def is_permanent_error(exc: BaseException) -> bool:
    if isinstance(exc, ApiFootballError | NotImplementedError | ValueError | KeyError):
        return True
    if isinstance(exc, ApiError) and exc.status_code is not None:
        return 400 <= exc.status_code < 500 and exc.status_code != 429
    return False
