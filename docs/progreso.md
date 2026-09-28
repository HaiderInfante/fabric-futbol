# Progreso del proyecto

Estado por fase. Una fase se marca como terminada solo cuando se confirma su criterio de "terminado"
(ver [CLAUDE.md](../CLAUDE.md), sección 8).

| Fase | Nombre | Estado |
|---|---|---|
| 0 | Setup | ✅ Terminada (2026-09-28) |
| 1 | Exploración de fuentes | ⚪ Pendiente |
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

- Confirmar que `ws_futbol_test` y `ws_futbol_prod` están asignados a la capacidad Trial
  (necesario en la Fase 8).
- football-data.org muestra 13 competiciones y no las 12 documentadas del plan gratuito: en la
  Fase 1 hay que comprobar a cuáles hay acceso real a partidos.
- Azure CLI, `ms-fabric-cli` y `fabric-cicd` se instalarán cuando una fase los necesite.
