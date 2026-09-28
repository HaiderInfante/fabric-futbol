# Progreso del proyecto

Estado por fase. Una fase se marca como terminada solo cuando se confirma su criterio de "terminado"
(ver [CLAUDE.md](../CLAUDE.md), sección 8).

| Fase | Nombre | Estado |
|---|---|---|
| 0 | Setup | 🟡 En curso |
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

## Fase 0 — Setup

**Criterio de terminado:** el repo existe, DEV está sincronizado y las 3 fuentes responden.

### Hecho

- [x] Estructura de carpetas del repositorio (sección 6 de CLAUDE.md).
- [x] `.gitignore` ampliado (variantes de `.env`, binarios de Power BI, muestras locales).
- [x] `.env.example` con keys y URLs base de las 3 fuentes.
- [x] `requirements.txt`, `requirements-dev.txt` y `pyproject.toml` (ruff + pytest).
- [x] `scripts/check_access.py`, probado con keys ausentes y con keys inválidas.
- [x] StatsBomb Open Data responde (24 competiciones, 80 temporadas).
- [x] README, `docs/decisiones.md` (ADR-001 a ADR-004) y esqueletos de `diccionario_datos.md`
      y `dp700_mapa.md`.

### Pendiente

- [ ] Obtener las keys de football-data.org y API-Football y cargarlas en `.env`.
- [ ] `check_access.py` devuelve OK en las 3 fuentes.
- [ ] Verificar los tenant settings de Git integration en el Admin portal.
- [ ] Conectar `ws_futbol_dev` a GitHub (`main`, carpeta `fabric`).
- [ ] Proteger `main` con un ruleset en GitHub.
- [ ] Mergear el PR de la Fase 0.

### Notas

- Azure CLI, `ms-fabric-cli` y `fabric-cicd` se instalarán cuando una fase los necesite.
