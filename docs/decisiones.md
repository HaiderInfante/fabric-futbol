# Registro de decisiones de arquitectura (ADR)

Formato breve: contexto → decisión → alternativas descartadas → consecuencias.

---

## ADR-001 — Monorepo con carpeta `fabric/` sincronizada

- **Fecha:** 2026-09-28
- **Contexto:** hay artefactos de dos tipos: ítems de Fabric (notebooks, pipelines, lakehouses,
  modelo semántico) y código local (clientes HTTP, transformaciones testeables, scripts, CI).
- **Decisión:** un solo repositorio. La integración Git de `ws_futbol_dev` se limita a la carpeta
  `fabric/` y el resto del repo queda fuera de su alcance.
- **Alternativas:** conectar Fabric a la raíz del repo (mezclaría ítems con código local y Fabric
  intentaría interpretar carpetas ajenas); usar dos repositorios (duplicaría CI y complicaría los
  PR que tocan código y notebooks a la vez).
- **Consecuencias:** los PR pueden cambiar a la vez la lógica en `src/` y el notebook que la usa.
  La carpeta `fabric/` solo se edita a través de Fabric o partiendo de una plantilla generada por
  Fabric.

## ADR-002 — Secretos en `.env` local y GitHub Secrets en CI

- **Fecha:** 2026-09-28
- **Contexto:** dos APIs requieren key y el repositorio es público.
- **Decisión:** las keys viven solo en `.env` (ignorado por Git). `.env.example` documenta las
  variables sin valores. En CI se usarán GitHub Secrets. Dentro de Fabric las keys se leerán desde
  Azure Key Vault o una conexión, a definir en la Fase 2.
- **Alternativas:** keys en un notebook o en `parameter.yml` (quedarían expuestas en Git).
- **Consecuencias:** cada desarrollador crea su propio `.env`. `check_access.py` nunca imprime
  valores de keys.

## ADR-003 — API-Football mediante registro directo en api-sports.io

- **Fecha:** 2026-09-28
- **Contexto:** API-Football se ofrece directamente (api-sports.io) y a través de RapidAPI, con
  distinta URL base y distinto header de autenticación.
- **Decisión:** registro directo. URL base `https://v3.football.api-sports.io` y header
  `x-apisports-key`.
- **Consecuencias:** el endpoint `/status` permite consultar el uso diario sin consumir cuota; lo
  usaremos para sincronizar `ctl_api_budget` en la Fase 2. Detalle importante: api-sports puede
  responder HTTP 200 con errores en el campo `errors`, así que el cliente debe revisar ese campo
  además del código HTTP.

## ADR-004 — `main` protegida y flujo de commits desde Fabric

- **Fecha:** 2026-09-28
- **Contexto:** `ws_futbol_dev` está conectado a `main`, que se protegerá con un ruleset que exige
  PR. Según Microsoft Learn, para hacer commit desde un workspace hacia su rama conectada, la
  política de la rama debe permitir commits directos. Por tanto, con `main` protegida, DEV **no
  podrá** hacer commit directo.
- **Decisión:** DEV solo recibe cambios con **Update from Git**. Los ítems nuevos o modificados en
  Fabric llegan a `main` por una de estas dos vías:
  1. **Branch out to another workspace**: se crea un workspace de feature conectado a una rama
     `feature/*`, se trabaja y se hace commit allí, y luego se abre un PR a `main`.
  2. **Commit to new branch** desde el panel Source control de DEV, para cambios puntuales. Crea
     una rama nueva con los cambios sin cambiar la conexión de DEV. Luego se abre un PR.
- **Alternativas:** dejar `main` sin protección (contradice el flujo definido en CLAUDE.md) o
  añadir al administrador al bypass list (anula el propósito de la protección).
- **Consecuencias:** se practica el flujo de ramas de Fabric que evalúa el DP-700. Los ítems que
  sirvan de plantilla (regla 5 de CLAUDE.md) se crearán con alguna de estas dos vías.
- **Evidencia (2026-09-28):** al conectar `ws_futbol_dev` con la carpeta `fabric` (que no existía),
  Fabric hizo un commit directo a `main` (`4481ba6 Creating directory fabric`, crea
  `fabric/Readme.md`). Por eso el ruleset `protect-main` se activó **después** de conectar. Si hay
  que reconectar un workspace a una carpeta nueva con `main` ya protegida, conviene crear antes la
  carpeta mediante un PR.

## ADR-005 — Competiciones y temporadas

- **Fecha:** 2026-09-29
- **Contexto:** los planes gratuitos, verificados contra las APIs
  ([cobertura](perfiles/cobertura.md)), no se solapan del todo:
  - football-data.org da acceso a la temporada 2023 en adelante.
  - API-Football solo a 2022–2024 (no a la temporada en curso).
  - StatsBomb solo tiene temporadas históricas escogidas (PL 2015/16; La Liga hasta 2020/21 y
    solo partidos del Barça; Euro 2024 completa).

  El usuario prefería la Premier League o La Liga.
- **Decisión (opción A):**

  | Competición | football-data | API-Football | StatsBomb |
  |---|---|---|---|
  | Premier League (principal) | 2024/25 + temporada en curso | 2024 | 2015/16 |
  | La Liga | 2024/25 + temporada en curso | 2024 | 2020/21 |
  | Euro 2024 | 2024 | 2024 | 2024 |

- **Por qué:**
  - 2024/25 es la temporada más reciente que comparten football-data y API-Football, lo que
    permite mapear partido a partido.
  - La temporada en curso de football-data aporta la carga en vivo: ventana de fechas,
    reprogramaciones, resultados corregidos y snapshot diario de la tabla.
  - StatsBomb aporta eventos con xG (`fact_shot`) y el material del simulador.
  - La Euro 2024 es el único caso con el mismo partido en las tres fuentes: sirve para validar el
    mapeo y cuadrar goles.
  - Dos ligas permiten el RLS por competición de la Fase 5.
- **Alternativas:**
  - Opción B, solo PL + La Liga: sin un caso de validación con las tres fuentes.
  - Bundesliga 2023/24: las tres fuentes a nivel de club, pero en StatsBomb solo están los
    partidos del Leverkusen y contradice la preferencia del usuario.
  - Temporada 2023/24: duplicaría el presupuesto de API-Football sin aportar nada nuevo.
- **Consecuencias:**
  - API-Football se carga como **relleno histórico limitado por presupuesto**: ~1.776 llamadas,
    ~20 días a 90/día (ver diccionario, sección 7), en orden Euro → PL → La Liga.
  - Ninguna temporada de PL o La Liga está en las tres fuentes: el mapeo con StatsBomb es a nivel
    de equipo y de jugador, no de partido.
  - Si los proveedores cambian sus planes gratuitos, hay que repetir
    `scripts/explore/discover_coverage.py`.

## ADR-006 — Clientes HTTP reutilizables con presupuesto de llamadas

- **Fecha:** 2026-09-29
- **Contexto:** CLAUDE.md exige rate limiting, reintentos, paginación, logging y un contador de
  presupuesto persistido. La exploración ya necesitaba proteger las 100 llamadas diarias de
  API-Football.
- **Decisión:** construir los clientes en `src/clients/` desde la Fase 1 (y no en la 2):
  - `ApiClient` base con `RateLimiter` de ventana deslizante, reintentos con backoff exponencial
    y jitter (429/5xx/errores de red, respetando `Retry-After`) y logging sin headers.
  - `CallBudget` como **interfaz**. Implementaciones:
    - `InMemoryBudget`: tope por ejecución.
    - `LocalFileBudget`: contador diario en `.state/`, en UTC.
    - En la Fase 2, una implementación sobre `ctl_api_budget`, sin tocar los clientes.
  - Cada intento consume presupuesto, incluidos reintentos y respuestas con error: el contador
    es **conservador** a propósito. `/status` no consume.
- **Alternativas:**
  - Scripts con `requests` sueltos: código de usar y tirar y riesgo de agotar la cuota.
  - Un cliente por fuente sin base común: duplicaría los reintentos y el rate limit.
- **Hallazgos que afectan a la Fase 2:**
  - El `/status` de API-Football se actualiza con retraso (llegó a reportar 1 uso cuando el header
    decía 5). El header `x-ratelimit-requests-remaining` de cada respuesta es la señal más fiable:
    conviene sincronizar el presupuesto con él después de cada llamada.
  - Falta decidir cómo llega `src/` a los notebooks de Fabric: wheel en un Environment, notebook
    utilitario con `%run` o código embebido.
