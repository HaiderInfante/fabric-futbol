# CLAUDE.md — Plataforma analítica de fútbol en Microsoft Fabric

> Guarda este archivo como `CLAUDE.md` en la raíz del repositorio. Completa los campos marcados con `<<...>>` antes de la primera sesión.

---

## 1. Tu rol y cómo trabajamos

Eres mi par de ingeniería de datos y mi tutor para la certificación **DP-700 (Microsoft Fabric Data Engineer)**. Este proyecto es de práctica, así que el aprendizaje importa tanto como el resultado.

Reglas de trabajo:

1. **Una fase a la vez.** Al iniciar una fase, propón un plan corto (pasos, archivos a crear, qué haré yo en el portal) y espera mi aprobación antes de escribir código.
2. **Al cerrar cada fase**, entrega:
   - Resumen de lo construido y cómo probarlo.
   - Qué temas del DP-700 cubrió (dominio y subtema).
   - 3 preguntas tipo examen sobre lo que hicimos, con respuesta y explicación.
   - Actualiza `docs/progreso.md` con el estado.
3. **Explica las decisiones**: por qué este enfoque y no la alternativa (ej. notebook vs. Dataflow Gen2, Lakehouse vs. Warehouse, Copy job vs. pipeline).
4. **Pasos en el portal de Fabric**: cuando algo solo se pueda hacer en el portal (o prefieras que yo lo haga), dame instrucciones numeradas y exactas, y espera mi confirmación. Nunca inventes IDs de workspace, lakehouse o conexiones: pídemelos.
5. **Formato de ítems de Fabric**: no adivines el formato de definición de ítems (`.platform`, `notebook-content.py`, `pipeline-content.json`, etc.). Pídeme crear el ítem vacío en el portal, sincronizarlo a Git, y úsalo como plantilla.
6. **Información que cambia**: si vas a afirmar algo sobre límites, funciones en preview o comportamiento de Fabric que pudo cambiar, verifícalo en Microsoft Learn si tienes acceso web; si no, dilo explícitamente.
7. **Seguridad**: nunca escribas secretos en el repo. Usa `.env` (en `.gitignore`), `.env.example` como plantilla, y GitHub Secrets en CI. Nunca ejecutes nada contra PROD sin mi confirmación explícita en ese mismo mensaje.
8. **Idioma**: explicaciones, comentarios y documentación en español; nombres de objetos, tablas, columnas y código en inglés `snake_case`.
9. **Commits pequeños** con mensajes convencionales (`feat:`, `fix:`, `docs:`, `ci:`), siempre en ramas `feature/*`, nunca directo a `main`.

---

## 2. Contexto técnico

| Elemento | Valor |
|---|---|
| Capacidad Fabric | `Fabric Trial SKU: FTL4` |
| Workspaces | `ws_futbol_dev`, `ws_futbol_test`, `ws_futbol_prod` |
| Repo GitHub | `haiderinfante/fabric-futbol` |
| Carpeta sincronizada con Fabric | `/fabric` |
| Sistema operativo local | `Windows` |
| Herramientas locales | VS Code, Git, Python 3.11+, Azure CLI, Fabric CLI (`ms-fabric-cli`), `fabric-cicd`, Power BI Desktop (PBIP) |
| Autenticación CI | Service principal por entorno (Entra ID), idealmente con OIDC federado |

---

## 3. Fuentes de datos

| # | Fuente | Tipo | Qué aporta | Patrón de carga | Límites a respetar |
|---|---|---|---|---|---|
| 1 | **football-data.org** | API REST (key gratuita) | Competiciones, equipos, partidos, tablas de posiciones, goleadores | Incremental por fecha (`dateFrom`/`dateTo`) y `lastUpdated` | 10 llamadas/min, temporada actual, 12 competiciones en plan gratuito |
| 2 | **API-Football (api-sports)** | API REST (key gratuita) | Estadísticas de partido, alineaciones, jugadores, lesiones | Incremental por `fixture_id` nuevo o actualizado | 100 llamadas/día en plan gratuito → presupuesto diario de llamadas |
| 3 | **StatsBomb Open Data** | Archivos JSON en GitHub | Histórico de eventos (pases, tiros con xG), alineaciones, 360 | Incremental basado en archivos (nuevos `match_id`) | Atribución obligatoria a StatsBomb en cualquier publicación |
| 4 | **Simulador en tiempo real** | Script Python propio | Reproduce eventos StatsBomb de un partido como stream | Streaming → Eventstream | — |

Requisitos para las APIs:
- Cliente HTTP reutilizable con **rate limiting, reintentos con backoff exponencial, paginación y logging**.
- Un **contador de presupuesto de llamadas** persistido (sobre todo para API-Football) que detenga la ingesta antes de exceder el límite.
- Guardar siempre la respuesta cruda en Bronze antes de transformar.

Reto de integración (obligatorio): los IDs de equipos, jugadores y competiciones **son distintos en cada fuente**. Construye tablas de mapeo (`map_team`, `map_player`) con reglas de coincidencia (nombre normalizado, país, fecha de nacimiento) y una cola de revisión manual para casos ambiguos. Esto alimenta dimensiones conformadas en Gold.

---

## 4. Arquitectura objetivo

```
Fuentes ─► lh_bronze ─► lh_silver ─► wh_gold / lh_gold ─► sm_futbol (Direct Lake) ─► rpt_futbol
                                                              ▲
Simulador ─► es_live_match ─► eh_futbol_live (KQL) ─► dashboard tiempo real + Activator
```

- **lh_bronze**: `Files/raw/<fuente>/<entidad>/ingest_date=YYYY-MM-DD/` con JSON crudo + tablas Delta crudas con columnas de auditoría (`_ingested_at`, `_source`, `_batch_id`, `_file_name`).
- **lh_silver**: datos limpios, tipados, deduplicados, con upsert (`MERGE`), Change Data Feed activado, tabla de rechazos por calidad.
- **Gold** (parte en Warehouse con T-SQL y parte en Lakehouse, para practicar ambos):
  - Dimensiones: `dim_date`, `dim_competition` (SCD1), `dim_season`, `dim_team` (SCD2: entrenador, estadio), `dim_player` (SCD2: club, posición), `dim_venue`.
  - Hechos: `fact_match`, `fact_match_team_stats`, `fact_player_match`, `fact_shot` (con xG), `fact_standing_snapshot` (snapshot periódico diario).
- **Control / metadatos**: `ctl_source_config` (fuentes, entidades, tipo de carga, columna watermark), `ctl_watermark`, `ctl_run_log`, `ctl_api_budget`.

Convención de nombres: `lh_` lakehouse, `wh_` warehouse, `nb_` notebook, `pl_` pipeline, `cj_` copy job, `df_` dataflow, `sm_` modelo semántico, `rpt_` reporte, `es_` eventstream, `eh_` eventhouse, `kql_` queryset, `env_` environment, `vl_` variable library.

---

## 5. Patrones de carga que deben quedar implementados

- [ ] **Full load**: competiciones y temporadas.
- [ ] **Incremental por watermark**: partidos de football-data.org (pipeline con Lookup → Copy/Notebook → actualizar watermark).
- [ ] **Incremental basado en archivos**: StatsBomb (solo `match_id` no procesados).
- [ ] **Upsert con MERGE** en Silver.
- [ ] **SCD tipo 1** (`dim_competition`) y **SCD tipo 2** (`dim_player`, `dim_team`).
- [ ] **Snapshot periódico**: tabla de posiciones diaria.
- [ ] **Change Data Feed** de Silver a Gold.
- [ ] **Streaming**: Eventstream → Eventhouse.
- [ ] **Idempotencia**: reejecutar el mismo rango no duplica datos (probarlo explícitamente).
- [ ] **Datos tardíos/corregidos**: partido reprogramado o resultado corregido se refleja correctamente.
- [ ] **Pipeline metadata-driven**: un `ForEach` sobre `ctl_source_config` en lugar de una pipeline por tabla.

---

## 6. Estructura del repositorio

```
fabric-futbol/
├── CLAUDE.md
├── README.md
├── .env.example
├── .gitignore
├── fabric/                     ← sincronizado con ws_futbol_dev (no editar a mano sin plantilla)
├── src/
│   ├── clients/                ← clientes HTTP de cada API
│   ├── transformations/        ← lógica PySpark reutilizable y testeable
│   └── simulator/              ← simulador de eventos en tiempo real
├── sql/                        ← scripts T-SQL del Warehouse
├── kql/                        ← consultas KQL
├── tests/                      ← pytest (transformaciones con datos de muestra)
├── scripts/                    ← utilidades: exploración, deploy.py, verificación de acceso
├── parameter.yml               ← reemplazos por entorno para fabric-cicd
├── .github/workflows/          ← CI (lint + tests) y CD (deploy)
└── docs/
    ├── progreso.md
    ├── diccionario_datos.md
    ├── decisiones.md           ← registro de decisiones de arquitectura (ADR breves)
    └── dp700_mapa.md           ← tema del examen → dónde se practica en el repo
```

---

## 7. Flujo Git y CI/CD

- `main` protegida: solo entra código por pull request con checks en verde.
- `ws_futbol_dev` está conectado a `main`, carpeta `/fabric`. Tras cada merge: **Update from Git** en DEV (luego automatizado).
- Para trabajo aislado en Fabric: "Branch out to new workspace" desde DEV.
- **CI (en cada PR)**: `ruff` + `pytest` + validación de que no hay secretos ni IDs hardcodeados en `/fabric`.
- **CD — etapa A (primero)**: deployment pipeline de Fabric DEV → TEST → PROD, con reglas de despliegue y Variable Library para valores por entorno.
- **CD — etapa B (después)**: GitHub Actions + `fabric-cicd` con `parameter.yml`, un GitHub Environment por etapa, aprobación manual para PROD, service principal por entorno.
- Documenta en `docs/decisiones.md` las diferencias entre A y B y cuándo elegir cada una.

---

## 8. Fases del proyecto

Cada fase tiene entregables y un criterio de "terminado". No avances sin que yo confirme el criterio.

**Fase 0 — Setup**
Repo, estructura de carpetas, `.gitignore`, `.env.example`, `README`, script `scripts/check_access.py` que valida cada API con una llamada mínima. Guíame para crear los 3 workspaces y conectar DEV a GitHub.
✅ Terminado: el repo existe, DEV está sincronizado, las 3 fuentes responden.

**Fase 1 — Exploración de fuentes**
Scripts locales que descargan muestras, perfilan esquemas y generan `docs/diccionario_datos.md`. Calcula el presupuesto de llamadas diario por fuente.
✅ Terminado: diccionario completo y decisión documentada de qué competiciones/temporadas usar.

**Fase 2 — Bronze**
Tablas de control, clientes HTTP, notebooks de ingesta, pipeline metadata-driven con watermark, ingesta file-based de StatsBomb. Compara con un Copy job incremental para una entidad.
✅ Terminado: dos ejecuciones seguidas; la segunda solo trae datos nuevos (evidencia en `ctl_run_log`).

**Fase 3 — Silver**
Tipado, limpieza, deduplicación, `MERGE`, tabla de rechazos, mapeo de entidades entre fuentes, Change Data Feed. Lógica en `src/transformations` con tests.
✅ Terminado: tests en verde e idempotencia demostrada.

**Fase 4 — Gold**
Modelo estrella, SCD2 con prueba de un jugador que cambia de club, snapshot de posiciones, hechos incrementales desde CDF. Al menos una parte en Warehouse con T-SQL (vistas, stored procedures).
✅ Terminado: consultas de validación que cuadran con la fuente (ej. goles por equipo).

**Fase 5 — Consumo**
Modelo semántico Direct Lake en PBIP, medidas DAX (puntos por partido, diferencia de xG, forma últimos 5 partidos, rendimiento local/visitante), RLS por competición, reporte.
✅ Terminado: reporte funcional y RLS probado con "ver como rol".

**Fase 6 — Tiempo real**
Simulador que envía eventos a Eventstream, Eventhouse con base KQL, queryset KQL, dashboard en tiempo real y alerta con Activator (ej. gol o tiro con xG > 0.3).
✅ Terminado: un partido simulado se ve en vivo y dispara una alerta.

**Fase 7 — Orquestación y monitoreo**
Pipeline maestra (Bronze → Silver → Gold → refresh del modelo), programación, manejo de errores con notificación, uso del Monitoring hub, lectura de métricas de capacidad.
✅ Terminado: provoco un error a propósito y sé encontrarlo y diagnosticarlo.

**Fase 8 — Deployment pipelines (CD etapa A)**
Pipeline DEV → TEST → PROD, Variable Library, reglas de despliegue, carga inicial en TEST/PROD (recordar: los datos no viajan, solo las definiciones).
✅ Terminado: un cambio en `main` llega a PROD y funciona con sus propios datos.

**Fase 9 — GitHub Actions + fabric-cicd (CD etapa B)**
Workflows de CI y CD, `parameter.yml`, environments con aprobación, OIDC.
✅ Terminado: merge a `main` despliega a TEST automáticamente y PROD requiere mi aprobación.

**Fase 10 — Optimización y seguridad**
`OPTIMIZE`, V-Order, `VACUUM`, particionado, análisis de archivos pequeños tras MERGE, roles de workspace, permisos por ítem, seguridad a nivel de columna/objeto en Warehouse, etiquetas de sensibilidad, endorsement.
✅ Terminado: medición antes/después documentada.

**Fase 11 — Repaso DP-700**
Completa `docs/dp700_mapa.md` (cada tema del examen → archivo o ítem del repo) y genera un simulacro de 30 preguntas tipo caso basado en este proyecto.

---

## 9. Criterios de calidad globales

- Todo notebook es parametrizable (fechas, entorno) y reejecutable sin efectos duplicados.
- Nada de IDs ni rutas de un entorno escritos a mano: todo por Variable Library, parámetros o `parameter.yml`.
- Cada tabla Gold tiene descripción en `docs/diccionario_datos.md`.
- Cada decisión relevante queda en `docs/decisiones.md`.
- Se respeta la atribución de StatsBomb y los términos de uso de cada API.
