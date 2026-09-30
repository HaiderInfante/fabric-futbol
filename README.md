# fabric-futbol

Plataforma analítica de fútbol construida en **Microsoft Fabric** como proyecto de práctica
para la certificación **DP-700 (Fabric Data Engineer)**.

Integra tres fuentes batch y un simulador en streaming en una arquitectura medallion
(Bronze → Silver → Gold). Sobre ella se construyen un modelo semántico Direct Lake, un reporte
Power BI y un dashboard en tiempo real con alertas.

## Arquitectura

```
Fuentes ─► lh_bronze ─► lh_silver ─► wh_gold / lh_gold ─► sm_futbol (Direct Lake) ─► rpt_futbol
                                                              ▲
Simulador ─► es_live_match ─► eh_futbol_live (KQL) ─► dashboard tiempo real + Activator
```

| Capa | Contenido |
|---|---|
| Bronze (`lh_bronze`) | JSON crudo por fuente/entidad/fecha de ingesta y tablas Delta con columnas de auditoría |
| Silver (`lh_silver`) | Datos tipados, deduplicados, con `MERGE`, Change Data Feed y tabla de rechazos |
| Gold (`wh_gold` / `lh_gold`) | Modelo estrella con dimensiones SCD1/SCD2, hechos y snapshot diario de posiciones |
| Tiempo real | Eventstream → Eventhouse (KQL) → dashboard y alertas con Activator |

El detalle del plan y las fases está en [CLAUDE.md](CLAUDE.md) y el avance en
[docs/progreso.md](docs/progreso.md).

## Fuentes de datos

| Fuente | Tipo | Límite del plan gratuito |
|---|---|---|
| [football-data.org](https://www.football-data.org) | API REST con key | 10 llamadas/min, temporada actual, 12 competiciones |
| [API-Football (api-sports.io)](https://api-sports.io) | API REST con key | 100 llamadas/día |
| [StatsBomb Open Data](https://github.com/statsbomb/open-data) | JSON en GitHub | Sin key; atribución obligatoria |
| Simulador propio | Script Python | — |

## Setup local (Windows / PowerShell)

Requisitos: Python 3.11+ y Git.

```powershell
# 1. Entorno virtual e instalación de dependencias
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt

# 2. Variables de entorno: copia la plantilla y completa tus keys en .env
Copy-Item .env.example .env

# 3. Verifica el acceso a las tres fuentes
python scripts/check_access.py
```

`check_access.py` hace una sola llamada mínima por fuente y termina con código 0 solo si las tres
responden. La llamada a API-Football usa `/status`, que según la documentación de api-sports no
consume la cuota diaria.

Exploración de fuentes (Fase 1). Los scripts se ejecutan como módulos desde la raíz del repo:

```powershell
python -m scripts.explore.discover_coverage          # cobertura real de los planes gratuitos
python -m scripts.explore.download_samples --dry-run # plan y coste estimado de la descarga
python -m scripts.explore.download_samples           # muestras crudas en data/samples/
python -m scripts.explore.profile_samples            # perfiles en docs/perfiles/
```

El presupuesto diario de API-Football se lleva en `.state/api_budget.json` (ignorado por Git) y
los scripts nunca tocan las 10 últimas llamadas del día.

Calidad de código:

```powershell
ruff check .
ruff format --check .
pytest
```

## Estructura del repositorio

```
fabric/          ítems de Fabric sincronizados con ws_futbol_dev (no editar a mano)
src/clients/     clientes HTTP de cada API
src/transformations/  lógica PySpark reutilizable y testeable
src/simulator/   simulador de eventos en tiempo real
src/exploration/ perfilado de JSON (exploración de fuentes)
sql/             scripts T-SQL del Warehouse
kql/             consultas KQL
tests/           pytest
scripts/         utilidades (verificación de acceso, exploración, despliegue)
docs/            progreso, diccionario de datos, decisiones (ADR) y mapa DP-700
```

## Seguridad

- Las keys viven solo en `.env`, que está en `.gitignore`. `.env.example` es la plantilla sin valores.
- En CI/CD se usan GitHub Secrets y service principals por entorno.
- Este repositorio es **público**: no se versionan datos descargados de las APIs
  (`data/samples/` está ignorado), solo código y definiciones.

## Atribución y términos de uso

**Datos de eventos: [StatsBomb Open Data](https://github.com/statsbomb/open-data).**
StatsBomb exige que cualquier investigación, análisis o insight publicado a partir de sus datos
indique a StatsBomb como fuente y use su logo (disponible en su Media Pack). Todo reporte o
dashboard de este proyecto que use estos datos incluye esa atribución.

Los datos de football-data.org y API-Football se usan según los términos de uso de cada
proveedor, dentro de los límites de su plan gratuito y sin redistribuir los datos crudos.
