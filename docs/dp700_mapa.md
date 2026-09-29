# Mapa DP-700 → proyecto

Relaciona cada tema del examen con el archivo o ítem del repo donde se practica. Se completa fase a
fase y se revisa entero en la Fase 11.

> Referencia: *study guide* de DP-700, "Skills measured as of October 19, 2026" (consultado el
> 2026-09-28). Los tres dominios pesan 30–35 % cada uno. Hay que volver a revisarlo antes de la
> Fase 11.

## 1. Implement and manage an analytics solution (30–35 %)

| Subtema del examen | Dónde se practica | Fase |
|---|---|---|
| Implement lifecycle management → *Configure version control* | `ws_futbol_dev` ↔ GitHub (`main`, `fabric/`), ADR-001 y ADR-004 | 0 |
| Implement lifecycle management → *Create and configure deployment pipelines* | _Pendiente_ | 8 |
| Implement lifecycle management → *Implement database projects* | _Pendiente_ | 4 |
| Configure security and governance | _Pendiente_ | 5 / 10 |
| Orchestrate processes | _Pendiente_ | 2 / 7 |
| Configure Microsoft Fabric workspace settings | _Pendiente_ | 2 / 10 |

## 2. Ingest and transform data (30–35 %)

| Subtema del examen | Dónde se practica | Fase |
|---|---|---|
| Design and implement loading patterns → *Design and implement full and incremental data loads* (análisis de candidatos a watermark: `lastUpdated` descartado, `last_updated` de StatsBomb válido; presupuesto como restricción del incremental) | `docs/diccionario_datos.md` §2, §4 y §7; ADR-005 | 1 (diseño) / 2 (implementación) |
| Design and implement loading patterns → *Prepare data for loading into a dimensional model* (claves naturales, mapeo entre fuentes) | `docs/diccionario_datos.md` §6 | 1 / 3 |
| Ingest and transform batch data → *Handle duplicate, missing, and late-arriving data* (estados de partido, reprogramaciones, eventos sin id propio) | `docs/diccionario_datos.md` §2 y §3 | 1 / 3 |
| Ingest and transform batch data → *Choose an appropriate data store* (volúmenes medidos por fuente) | `docs/diccionario_datos.md` §7 | 1 / 2 |
| Ingest and transform streaming data | _Pendiente_ | 6 |

## 3. Monitor and optimize an analytics solution (30–35 %)

| Subtema del examen | Dónde se practica | Fase |
|---|---|---|
| Monitor Fabric items | _Pendiente_ | 7 |
| Identify and resolve errors | _Pendiente_ | 7 |
| Optimize performance | _Pendiente_ | 10 |
