# Progreso del proyecto

Estado por fase. Una fase se marca como terminada solo cuando se confirma su criterio de "terminado"
(ver [CLAUDE.md](../CLAUDE.md), sección 8).

| Fase | Nombre | Estado |
|---|---|---|
| 0 | Setup | ✅ Terminada (2026-09-28) |
| 1 | Exploración de fuentes | ✅ Terminada (2026-09-29) |
| 2 | Bronze | 🟡 En curso (2.1 y 2.2 ✅) |
| 3 | Silver | ⚪ Pendiente |
| 4 | Gold | ⚪ Pendiente |
| 5 | Consumo | ⚪ Pendiente |
| 6 | Tiempo real | ⚪ Pendiente |
| 7 | Orquestación y monitoreo | ⚪ Pendiente |
| 8 | Deployment pipelines (CD etapa A) | ⚪ Pendiente |
| 9 | GitHub Actions + fabric-cicd (CD etapa B) | ⚪ Pendiente |
| 10 | Optimización y seguridad | ⚪ Pendiente |
| 11 | Repaso DP-700 | ⚪ Pendiente |

---

## Fase 0 — Setup ✅

**Criterio de terminado:** el repo existe, DEV está sincronizado y las 3 fuentes responden.
Confirmado el 2026-09-28.

### Construido

- Estructura de carpetas del repositorio (sección 6 de CLAUDE.md).
- `.gitignore` ampliado (variantes de `.env`, binarios de Power BI, muestras locales) y
  `.gitattributes` con normalización a LF.
- `.env.example` con keys y URLs base de las 3 fuentes.
- `requirements.txt`, `requirements-dev.txt` y `pyproject.toml` (ruff + pytest).
- `scripts/check_access.py`, probado con keys ausentes, keys inválidas y keys válidas.
- README, `docs/decisiones.md` (ADR-001 a ADR-004) y esqueletos de `diccionario_datos.md` y
  `dp700_mapa.md`.

### Configurado en el portal

- Tenant settings de Git integration (Git y GitHub) habilitados.
- PAT fine-grained `fabric-git-dev`: solo sobre `fabric-futbol`, Contents read/write, **vence en
  90 días (~2026-12-27)**. Al renovarlo hay que actualizar la cuenta en Fabric.
- `ws_futbol_dev` conectado a `HaiderInfante/fabric-futbol`, rama `main`, carpeta `fabric`.
  Source control en 0.
- Ruleset `protect-main`: bloquea borrado y force push, exige PR con 0 aprobaciones, sin bypass.

### Evidencia

```
[OK     ] football-data.org    HTTP 200, 13 competiciones visibles, llamadas disponibles este minuto: 9
[OK     ] API-Football         HTTP 200, plan Free, uso hoy: 0/100
[OK     ] StatsBomb Open Data  HTTP 200, 24 competiciones y 80 temporadas disponibles
```

### Pendientes y notas para fases siguientes

- ~~Confirmar que `ws_futbol_test` y `ws_futbol_prod` están asignados a la capacidad Trial~~
  Confirmado el 2026-09-28: los tres workspaces están en la Trial.
- ~~football-data.org muestra 13 competiciones y no las 12 documentadas~~ Resuelto en la Fase 1:
  son las 12 `TIER_ONE` más la Copa Libertadores (`TIER_FOUR`).
- Azure CLI, `ms-fabric-cli` y `fabric-cicd` se instalarán cuando una fase los necesite.

---

## Fase 1 — Exploración de fuentes ✅

**Criterio de terminado:** diccionario completo y decisión documentada de qué competiciones y
temporadas usar. Confirmado el 2026-09-29.

### Configurado

- Ruleset `protect-main`: se añadió el check obligatorio `lint-test` (CI).
- Capacidad Trial revisada: su vigencia cubre el relleno de API-Football.
- Sección 3 de `CLAUDE.md` actualizada con los límites y patrones verificados.

### Construido

- Clientes HTTP reutilizables en `src/clients/`: base con rate limiting, reintentos y
  presupuesto; uno por fuente (ADR-006).
- CI mínima en GitHub Actions (`ruff` + `pytest` en cada PR).
- `scripts/explore/discover_coverage.py` genera la matriz de cobertura real de los planes
  gratuitos ([perfiles/cobertura.md](perfiles/cobertura.md)).
- `scripts/explore/download_samples.py` descarga muestras crudas del alcance elegido.
- `src/exploration/json_profiler.py` y `scripts/explore/profile_samples.py` generan los perfiles
  por fuente en `docs/perfiles/`.
- [diccionario_datos.md](diccionario_datos.md): entidades, claves, semántica del marcador,
  mapeo entre fuentes, presupuesto de llamadas y volumen.
- ADR-005 (competiciones y temporadas) y ADR-006 (clientes HTTP).
- 38 tests en verde.

### Hallazgos clave

- API-Football gratis: solo temporadas 2022–2024, 100/día y 10/min, **sin el parámetro `ids`**.
- football-data: temporadas desde 2023. `lastUpdated` no sirve como watermark por partido.
- `fullTime` de football-data suma la tanda de penaltis, y `fulltime` de API-Football es solo el
  tiempo reglamentario.
- StatsBomb no trae fecha de nacimiento de los jugadores.
- Coincidencia de equipos con normalización simple: 65 % en clubes y 96 % en selecciones.

### Consumo de la exploración

- API-Football: 29 llamadas según el contador local (conservador); unas 20 según la API.
- football-data: ~40 llamadas. StatsBomb: ~22 descargas.

### Pendientes y notas para fases siguientes

- Fase 2: decidir cómo llega `src/` a los notebooks de Fabric (wheel en un Environment, `%run` o
  código embebido).
- Fase 2: sincronizar `ctl_api_budget` con el header `x-ratelimit-requests-remaining`.
- ~~Revisar en el portal cuándo vence la capacidad Trial~~ Revisado el 2026-09-29: cubre los ~20
  días de relleno de API-Football.

---

## Fase 2 — Bronze 🟡

**Criterio de terminado:** dos ejecuciones seguidas; la segunda solo trae datos nuevos (evidencia
en `ctl_run_log`).

Se trabaja en `ws_futbol_feat_bronze`, conectado a `feature/fase-2-bronze` (ver ADR-004).
Decisiones: ADR-007 a ADR-010.

| Subetapa | Contenido | Estado |
|---|---|---|
| 2.1 | Key Vault, `env_futbol`, `vl_futbol`, `lh_bronze`, tablas `ctl_*`, `nb_bronze_setup` | ✅ 2026-10-05 |
| 2.2 | football-data (`full`, `window`, `season_full`, `snapshot`) y `pl_bronze_ingest` | ✅ 2026-10-08 |
| 2.3 | StatsBomb (`file_incremental` con `ctl_file_manifest`) | ⚪ |
| 2.4 | API-Football (`budgeted_backfill` con cuota por configuración) | ⚪ |
| 2.5 | Copy job (HTTP completo e incremental desde tabla), documentación y cierre | ⚪ |

### Evidencia de la subetapa 2.2 (`ctl_run_log`, UTC)

| Configuración | Ejecución 1 (llamadas / leídos / insertados) | Ejecución 2 (llamadas / leídos / insertados) |
|---|---|---|
| `fd_matches_current` | 4 / 158 / 158 | 4 / 43 / 2 |
| `fd_matches_history` | 3 / 811 / 811 | **0 / 0 / 0** |
| `fd_teams` | 5 / 104 / 104 | 2 / 40 / 0 |
| `fd_standings` | 2 / 2 / 2 | 2 / 2 / 0 |
| `fd_scorers` | 2 / 2 / 2 | 2 / 2 / 0 |
| `fd_competitions` | 1 / 13 / 0 (ya cargadas en la prueba manual) | 1 / 13 / 0 |

- La primera ejecución de la pipeline duró 8 min 08 s, con 6 iteraciones.
- Los 2 registros insertados en `fd_matches_current` en la segunda ejecución están pendientes de
  revisar: pueden ser cambios reales o un campo volátil no detectado.

### Hallazgos

- *Branch out* se bloquea si la rama de origen no tiene ítems (ADR-004).
- El wheel en modo Quick no viaja por Git y en modo Full sí (ADR-008).
- El Lookup en modo *Table* no ordena, y *T-SQL Query* está deshabilitado → diseño
  independiente del orden (ADR-010).
- HTTP 430 `TooManyRequestsForCapacity` con una sesión interactiva abierta → cerrar las sesiones
  antes de lanzar la pipeline. Se añadió `retry` = 2 a la actividad Notebook (ADR-010).
- Los roles de Azure aparecen traducidos en el portal en español (ADR-009).

### Hallazgos de la subetapa 2.4 (primera prueba, 2026-10-09, `max_api_calls = 5`)

- **El plan gratuito de API-Football rechaza `page > 3`** ("Free plans are limited to a maximum
  value of 3 for the Page parameter"). `/players?league&season` tiene 57 páginas en PL, así que
  ese diseño no sirve. Nuevo diseño: `/players?team&season`, páginas 1 a 3 por equipo (equipos
  tomados de `api_football_teams`). Si un equipo tiene más páginas queda marcado `truncated`;
  el Manchester United tiene 4, y la cuarta serían sobre todo juveniles. `/players/squads`
  descartado: devuelve la plantilla actual y sin fecha de nacimiento. Coste estimado: unas 168
  llamadas.
- Los **reintentos de la pipeline repetían un error permanente** (3 intentos × 5 llamadas) y
  **no se guardaban las páginas ya descargadas**. Ahora el handler guarda lo descargado antes de
  registrar el error. El notebook clasifica el error (`src/ingestion/errors.py`): si es
  permanente termina sin excepción con `status = failed`, y la actividad Fail de la pipeline lo
  marca como fallido sin reintentar.
- **`api_calls` incluía la llamada gratuita a `/status`** (4 llamadas con 3 archivos). Ahora
  cuenta solo las llamadas que consumen cuota (`billable_calls`).
- **Contadores:** las llamadas que consumen cuota fueron 21. El proveedor no cobra los 3
  errores de plan, así que registró 18, que es lo que marcaba `/status` después. `calls_used`
  (22) es conservador: toma el máximo entre nuestro contador y el del proveedor.
- `af_fixture_statistics` y `af_fixture_players` corrieron antes que `af_fixtures` y no tenían
  pendientes. Es lo esperado según el diseño independiente del orden (ADR-010).
