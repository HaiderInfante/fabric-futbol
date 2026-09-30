"""Fase 1, paso B: perfila las muestras crudas y genera docs/perfiles/<fuente>.md.

Uso (desde la raíz del repo):
    python -m scripts.explore.profile_samples

Lee data/samples/<fuente>/<entidad>/*.json (excepto la carpeta discovery). Cada archivo se
convierte en registros así:
- API-Football: los elementos de `response` (el sobre get/parameters/errors/paging es común a
  todos los endpoints y se documenta aparte en el diccionario).
- Si la raíz es una lista (StatsBomb): cada elemento es un registro.
- En otro caso (football-data.org): el documento completo es un registro.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from scripts.explore._common import PROFILES_DIR, SAMPLES_DIR, setup
from src.exploration.json_profiler import JsonProfiler, render_markdown_table

logger = logging.getLogger("profile_samples")

SOURCE_TITLES = {
    "football_data": "football-data.org",
    "api_football": "API-Football",
    "statsbomb": "StatsBomb Open Data",
}


def extract_records(source: str, payload: Any) -> list[Any]:
    if source == "api_football" and isinstance(payload, dict) and "response" in payload:
        response = payload["response"]
        return response if isinstance(response, list) else [response]
    if isinstance(payload, list):
        return payload
    return [payload]


def profile_entity(source: str, folder: Path) -> str:
    profiler = JsonProfiler()
    files = sorted(folder.glob("*.json"))
    total_bytes = 0
    for file in files:
        total_bytes += file.stat().st_size
        payload = json.loads(file.read_text(encoding="utf-8"))
        profiler.add_many(extract_records(source, payload))

    names = ", ".join(f.stem for f in files[:6]) + (" …" if len(files) > 6 else "")
    header = [
        f"## `{folder.name}`",
        "",
        f"- Archivos: {len(files)} ({names}) · {total_bytes / 1_048_576:.1f} MB",
        f"- Registros perfilados: {profiler.records}",
        "",
        "",
    ]
    return "\n".join(header) + render_markdown_table(profiler.profiles()) + "\n"


def profile_source(source: str) -> Path:
    source_dir = SAMPLES_DIR / source
    entities = sorted(p for p in source_dir.iterdir() if p.is_dir() and p.name != "discovery")
    sections = [
        f"# Perfil de muestras: {SOURCE_TITLES.get(source, source)}",
        "",
        "> Generado por `scripts/explore/profile_samples.py` a partir de `data/samples/`. "
        "Se regenera en cada ejecución: no editar a mano. La interpretación de negocio está "
        "en `docs/diccionario_datos.md`.",
        "",
        "Leyenda: *Presencia* = % de objetos padre que tienen el campo (— en elementos de "
        "lista); *Distintos* = valores no nulos distintos; *¿Clave?* = único, sin nulos y "
        "presente en el 100 % de los casos dentro de la muestra.",
        "",
    ]
    for entity in entities:
        logger.info("Perfilando %s/%s", source, entity.name)
        sections.append(profile_entity(source, entity))

    PROFILES_DIR.mkdir(parents=True, exist_ok=True)
    output = PROFILES_DIR / f"{source}.md"
    output.write_text("\n".join(sections), encoding="utf-8", newline="\n")
    return output


def main() -> None:
    setup()
    for source in SOURCE_TITLES:
        if (SAMPLES_DIR / source).exists():
            logger.info("Perfil generado en %s", profile_source(source))
        else:
            logger.warning("No hay muestras de %s", source)


if __name__ == "__main__":
    main()
