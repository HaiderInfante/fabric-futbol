# Progreso del proyecto

Estado por fase. Una fase se marca como terminada solo cuando se confirma su criterio de "terminado"
(ver [CLAUDE.md](../CLAUDE.md), sección 8).

| Fase | Nombre | Estado |
|---|---|---|
| 0 | Setup | ✅ Terminada (2026-09-28) |
| 1 | Exploración de fuentes | ✅ Terminada (2026-09-29) |
| 2 | Bronze | ⚪ Pendiente |
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
