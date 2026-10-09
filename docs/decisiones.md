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
- **Evidencia (2026-10-05):** *Branch out* falló porque la rama de origen (`main/fabric`) no tenía
  ningún ítem. Alternativa aplicada: crear `ws_futbol_feat_bronze` a mano y conectarlo a una rama
  nueva `feature/fase-2-bronze` creada desde `main`. El efecto es el mismo, salvo que no queda
  registrada la relación entre el workspace de feature y DEV. Cuando DEV tenga ítems, *Branch
  out* debería funcionar.

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

## ADR-007 — Formato de Bronze e idempotencia

- **Fecha:** 2026-10-08
- **Contexto:** Bronze debe guardar el dato crudo, permitir reejecutar sin duplicar y conservar
  el historial de cambios (partidos reprogramados, resultados corregidos). Las APIs cambian el
  tipo de algunos campos (p. ej. `statistics.value` llega como int o como texto).
- **Decisión:**
  - Respuesta cruda tal cual en `Files/raw/<fuente>/<entidad>/ingest_date=…/<batch_id>/`.
  - Una tabla Delta por entidad (`<fuente>_<entidad>`) con una fila por registro. Columnas:
    - `payload`: el registro como **texto JSON**.
    - `record_key`: clave natural.
    - `record_hash`: SHA-256 **sin los campos volátiles** (`lastUpdated`, `currentMatchday`
      en football-data; `update` en API-Football).
    - `record_context`: JSON con competición, temporada… que el registro no trae dentro.
    - Columnas de auditoría `_source`, `_config_id`, `_batch_id`, `_file_name`, `_ingested_at`.
  - Escritura: se **añaden solo las versiones nuevas**, comparando cada registro con la
    **última** versión de su clave.
- **Por qué:**
  - El texto JSON no se rompe ante cambios de tipo; Silver lo parsea con un esquema explícito.
  - Comparar con la última versión, y no con cualquiera anterior, registra el caso A → B → A.
    Con un MERGE por (`record_key`, `record_hash`) ese segundo A no se guardaría.
  - Sin excluir los campos volátiles, cada refresco de football-data parecería un cambio: los
    380 partidos tienen el mismo `lastUpdated`, que es la hora de refresco de la competición.
- **Alternativas:**
  - Structs inferidos con `mergeSchema`: fallan ante cambios de tipo.
  - Sobrescritura por lote: pierde el historial.
  - MERGE por (clave, hash): pierde el caso A → B → A.
- **Evidencia:** segunda ejecución de la pipeline en la subetapa 2.2. `fd_competitions` leyó 13
  registros e insertó 0; `fd_teams` leyó 40 e insertó 0; `fd_matches_history` hizo 0 llamadas.

## ADR-008 — Distribución del código: wheel en el Environment `env_futbol`

- **Fecha:** 2026-10-08
- **Decisión:** `src/` se empaqueta como wheel `fabric_futbol` (versión en `pyproject.toml`) y
  se instala como librería propia del Environment `env_futbol`, en **modo Full**.
- **Evidencia que fija el modo:**
  - El wheel en **modo Quick no se serializa en Git**: la carpeta del Environment solo traía
    `Setting/Sparkcompute.yml`.
  - En **modo Full sí**: aparece en `Libraries/CustomLibraries/` y viaja por Git y por las
    deployment pipelines. Lo necesitan DEV, TEST y PROD (fases 8 y 9).
  - Problema observado en modo Quick: una versión subida en Quick quedó tapada por una ruta
    `/nfs4/pyenv-…` antigua; se resolvió subiéndola de nuevo y reiniciando la sesión.
- **Flujo para actualizar el wheel:**
  1. Subir la versión en `pyproject.toml`.
  2. `python -m build --wheel`.
  3. Reemplazar el `.whl` en `fabric/env_futbol.Environment/Libraries/CustomLibraries/`.
  4. Commit.
  5. *Update from Git* en el workspace.
  6. **Publish** del Environment: Git solo actualiza el estado *staging*.
- **Coste:** publicar en modo Full tarda entre 3 y 6 minutos. El modo Quick queda solo para
  pruebas rápidas que no se commitean.
- **Alternativas:**
  - Notebook utilitario con `%run`: duplica el código fuera de `src/` y sin tests.
  - `.py` en `Files/` del lakehouse: el código no viaja por Git.

## ADR-009 — Secretos: Azure Key Vault y Variable Library

- **Fecha:** 2026-10-08
- **Decisión:**
  - Las API keys viven en el Key Vault `kv-futbol-dev-hi01` (modelo RBAC). Los notebooks las
    leen con `notebookutils.credentials.getSecret(url, nombre)` y nunca las imprimen ni las
    pasan como parámetro.
  - La URL del vault no es secreta y está en la Variable Library `vl_futbol/key_vault_url`, que
    tendrá un conjunto de valores por entorno en la Fase 8.
- **Permisos:** rol RBAC *Key Vault Secrets Officer* (en el portal en español, **"Agente de
  secretos de Key Vault"**) para el usuario que ejecuta. Para solo leer bastaría *Key Vault
  Secrets User* ("Usuario de secretos de Key Vault").
- **Pendiente (Fase 9):** con service principals, `notebookutils.variableLibrary` no está
  soportado (según Learn), y la identidad que lee el vault cambia. Hay que revisarlo al
  automatizar.

## ADR-010 — Orquestación guiada por metadatos, independiente del orden

- **Fecha:** 2026-10-08
- **Decisión:** `pl_bronze_ingest` encadena Lookup (`ctl_source_config`, modo *Table*) → Filter
  (`is_active` y `source_filter`) → ForEach **secuencial** → Notebook `nb_bronze_ingest`, con la
  etiqueta de sesión `bronze_ingest` para que los notebooks compartan sesión (alta
  concurrencia).
- **Restricción encontrada:** el modo *T-SQL Query (Preview)* del Lookup, que permitiría
  `ORDER BY priority`, está deshabilitado en el workspace. En modo *Table*, el orden de las filas
  es el orden físico de la tabla, que no está garantizado.
- **Consecuencia de diseño:** ninguna configuración depende del orden.
  - Cada configuración con presupuesto (`budgeted_backfill`) tiene su **cuota diaria** propia,
    de modo que ninguna agota el presupuesto de las otras.
  - Una dependencia (p. ej. las estadísticas por partido necesitan `fixtures`) se resuelve en la
    ejecución siguiente: si aún no hay partidos cargados, esa configuración tiene 0 pendientes.
  - `priority` queda como documentación y para ordenar consultas, no como mecanismo.
- **Reintentos:** como el notebook es idempotente, la actividad Notebook se reintenta sin
  riesgo (`retry` = 2).
- **Lección de capacidad:** con una sesión interactiva de Spark abierta, la primera ejecución
  falló en las 6 iteraciones con `TooManyRequestsForCapacity` (HTTP 430), antes de escribir en
  `ctl_run_log`. Regla: cerrar las sesiones interactivas antes de lanzar la pipeline. El
  diagnóstico de este tipo de errores se practica en la Fase 7.
- **Alternativas:**
  - Un notebook que planifique y devuelva la lista ordenada: añade una actividad y un notebook
    más.
  - Reescribir la tabla ordenada: depende de un detalle de implementación.
