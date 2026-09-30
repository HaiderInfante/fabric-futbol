"""Perfilado de documentos JSON anidados.

Recorre cada registro y, por cada ruta de campo (p. ej. `matches[].homeTeam.id`), acumula:
tipos observados, apariciones, nulos, valores distintos y un ejemplo. La presencia se mide
contra el número de objetos padre, así se detectan campos que solo aparecen a veces.

Notación de rutas: `a.b` para objetos anidados y `a[]` para los elementos de una lista.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any

SCALAR_TYPES = ("null", "bool", "int", "float", "str")


def json_type(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):  # antes que int: bool es subclase de int
        return "bool"
    if isinstance(value, int):
        return "int"
    if isinstance(value, float):
        return "float"
    if isinstance(value, str):
        return "str"
    if isinstance(value, dict):
        return "object"
    if isinstance(value, list):
        return "array"
    return type(value).__name__


@dataclass
class _FieldStats:
    parent: str | None  # ruta del objeto que contiene el campo; None si es elemento de lista
    types: Counter = field(default_factory=Counter)
    occurrences: int = 0
    nulls: int = 0
    distinct: set = field(default_factory=set)
    distinct_capped: bool = False
    example: Any = None


@dataclass(frozen=True)
class FieldProfile:
    path: str
    types: tuple[str, ...]
    occurrences: int
    presence_pct: float | None  # None para elementos de lista
    null_pct: float
    distinct_count: int | None  # None para objetos y listas
    distinct_capped: bool
    example: Any
    is_candidate_key: bool


class JsonProfiler:
    def __init__(self, max_distinct: int = 10_000, min_key_samples: int = 10) -> None:
        self.max_distinct = max_distinct
        # Con pocos valores, "todos distintos" es casualidad: no se marca como clave candidata.
        self.min_key_samples = min_key_samples
        self.records = 0
        self._containers: Counter = Counter()
        self._fields: dict[str, _FieldStats] = {}

    def add(self, record: Any) -> None:
        self.records += 1
        self._walk("", record)

    def add_many(self, records: Iterable[Any]) -> None:
        for record in records:
            self.add(record)

    def _walk(self, path: str, value: Any) -> None:
        if isinstance(value, dict):
            self._containers[path] += 1
            for key, child in value.items():
                child_path = f"{path}.{key}" if path else key
                self._observe(child_path, child, parent=path)
                self._walk(child_path, child)
        elif isinstance(value, list):
            item_path = f"{path}[]"
            for item in value:
                self._observe(item_path, item, parent=None)
                self._walk(item_path, item)

    def _observe(self, path: str, value: Any, parent: str | None) -> None:
        stats = self._fields.get(path)
        if stats is None:
            stats = self._fields[path] = _FieldStats(parent=parent)
        kind = json_type(value)
        stats.types[kind] += 1
        stats.occurrences += 1
        if value is None:
            stats.nulls += 1
            return
        if kind in SCALAR_TYPES:
            if stats.example is None:
                stats.example = value
            if not stats.distinct_capped:
                stats.distinct.add(value)
                if len(stats.distinct) > self.max_distinct:
                    stats.distinct_capped = True
                    stats.distinct.clear()

    def profiles(self) -> list[FieldProfile]:
        result = []
        for path, stats in self._fields.items():
            scalar = all(kind in SCALAR_TYPES for kind in stats.types)
            presence = None
            if stats.parent is not None and self._containers[stats.parent]:
                presence = 100.0 * stats.occurrences / self._containers[stats.parent]
            non_null = stats.occurrences - stats.nulls
            distinct = len(stats.distinct) if scalar and not stats.distinct_capped else None
            is_key = (
                scalar
                and not stats.distinct_capped
                and stats.nulls == 0
                and non_null >= max(self.min_key_samples, 2)
                and presence == 100.0
                and distinct == non_null
            )
            result.append(
                FieldProfile(
                    path=path,
                    types=tuple(sorted(stats.types)),
                    occurrences=stats.occurrences,
                    presence_pct=presence,
                    null_pct=100.0 * stats.nulls / stats.occurrences,
                    distinct_count=distinct,
                    distinct_capped=stats.distinct_capped and scalar,
                    example=stats.example,
                    is_candidate_key=is_key,
                )
            )
        return result


def _cell(value: Any, width: int = 40) -> str:
    if value == "":
        return '""'
    text = str(value).replace("|", "\\|").replace("\n", " ")
    return text if len(text) <= width else text[: width - 1] + "…"


def format_pct(value: float) -> str:
    """Porcentaje sin decimales, sin ocultar extremos: 0.3 → '<1 %', 99.8 → '>99 %'."""
    if 0 < value < 1:
        return "<1 %"
    if 99 < value < 100:
        return ">99 %"
    return f"{value:.0f} %"


def render_markdown_table(profiles: list[FieldProfile]) -> str:
    lines = [
        "| Campo | Tipos | Presencia | Nulos | Distintos | Ejemplo | ¿Clave? |",
        "|---|---|---|---|---|---|---|",
    ]
    for p in profiles:
        presence = "—" if p.presence_pct is None else format_pct(p.presence_pct)
        if p.distinct_capped:
            distinct = "muchos"
        elif p.distinct_count is None:
            distinct = "—"
        else:
            distinct = str(p.distinct_count)
        example = "" if p.example is None else f"`{_cell(p.example)}`"
        lines.append(
            f"| `{p.path}` | {', '.join(p.types)} | {presence} | {format_pct(p.null_pct)} | "
            f"{distinct} | {example} | {'✔' if p.is_candidate_key else ''} |"
        )
    return "\n".join(lines)
