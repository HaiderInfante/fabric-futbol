"""Presupuesto de llamadas a APIs con límite diario.

`CallBudget` es la interfaz que usan los clientes HTTP. Hay dos implementaciones:
- `InMemoryBudget`: tope por ejecución (y para tests).
- `LocalFileBudget`: contador diario persistido en un JSON local (exploración, Fase 1).

En la Fase 2 se añadirá una implementación sobre la tabla Delta `ctl_api_budget` sin cambiar
los clientes.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Protocol


class BudgetExceededError(RuntimeError):
    """Se lanza antes de hacer una llamada que excedería el presupuesto."""


class CallBudget(Protocol):
    def remaining(self) -> int: ...

    def consume(self, calls: int = 1) -> None: ...


class InMemoryBudget:
    """Tope de llamadas que vive solo durante la ejecución."""

    def __init__(self, limit: int, name: str = "run") -> None:
        self.limit = limit
        self.name = name
        self.used = 0

    def remaining(self) -> int:
        return max(self.limit - self.used, 0)

    def consume(self, calls: int = 1) -> None:
        if calls > self.remaining():
            raise BudgetExceededError(
                f"Presupuesto '{self.name}' agotado: {self.used}/{self.limit} llamadas usadas"
            )
        self.used += calls


def _utc_today() -> date:
    return datetime.now(UTC).date()


class LocalFileBudget:
    """Contador diario persistido en un JSON, con una clave por fuente.

    El día se calcula en UTC. `reserve` deja llamadas sin tocar (margen de seguridad).
    Formato del archivo: {"<fuente>": {"date": "YYYY-MM-DD", "used": 12}}
    """

    def __init__(
        self,
        path: Path,
        source: str,
        daily_limit: int,
        reserve: int = 0,
        today: Callable[[], date] = _utc_today,
    ) -> None:
        self.path = Path(path)
        self.source = source
        self.daily_limit = daily_limit
        self.reserve = reserve
        self._today = today

    def _read_all(self) -> dict:
        if not self.path.exists():
            return {}
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _write_used(self, used: int) -> None:
        data = self._read_all()
        data[self.source] = {"date": self._today().isoformat(), "used": used}
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def used(self) -> int:
        entry = self._read_all().get(self.source)
        if not entry or entry.get("date") != self._today().isoformat():
            return 0  # día nuevo: el contador se reinicia
        return int(entry["used"])

    def remaining(self) -> int:
        return max(self.daily_limit - self.reserve - self.used(), 0)

    def consume(self, calls: int = 1) -> None:
        used = self.used()
        if calls > self.remaining():
            raise BudgetExceededError(
                f"Presupuesto diario de '{self.source}' agotado: {used}/{self.daily_limit} "
                f"llamadas usadas (reserva {self.reserve})"
            )
        self._write_used(used + calls)

    def sync_used(self, used_by_provider: int) -> None:
        """Alinea el contador con el uso que reporta el proveedor.

        Se queda con el mayor de los dos valores: la API es la fuente de verdad, pero si el
        contador local va por delante (llamadas en vuelo) no se retrocede.
        """
        self._write_used(max(self.used(), used_by_provider))
