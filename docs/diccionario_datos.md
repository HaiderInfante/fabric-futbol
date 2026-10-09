# Diccionario de datos

> Estado: **fuentes documentadas (Fase 1)**. Las secciones de Bronze, Silver, Gold y control se
> completan en sus fases. Cada tabla Gold debe tener aquí su descripción.
>
> Evidencia técnica (tipos, nulos, cardinalidad de cada campo) en los perfiles generados:
> [cobertura](perfiles/cobertura.md) · [football-data](perfiles/football_data.md) ·
> [API-Football](perfiles/api_football.md) · [StatsBomb](perfiles/statsbomb.md).
> Muestras analizadas el 2026-09-29.

## 1. Alcance

Decidido en [ADR-005](decisiones.md#adr-005--competiciones-y-temporadas):

| Competición | football-data.org | API-Football | StatsBomb |
|---|---|---|---|
| Premier League | `PL`: 2024/25 + temporada en curso | liga `39`, temporada `2024` | competición `2`, temporada `27` (2015/16) |
| La Liga | `PD`: 2024/25 + temporada en curso | liga `140`, temporada `2024` | competición `11`, temporada `90` (2020/21, solo partidos del Barça) |
| Euro 2024 | `EC`: 2024 | liga `4`, temporada `2024` | competición `55`, temporada `282` |

Convención de temporada: las tres fuentes identifican la temporada por su **año de inicio**
(`2024` = 2024/25). En StatsBomb se usa un `season_id` propio, cuyo nombre es `"2024/2025"` o
`"2024"`.

---

## 2. football-data.org (API v4)

**Acceso:** header `X-Auth-Token`. Plan gratuito: 12 competiciones `TIER_ONE` (la 13.ª visible,
Copa Libertadores, es `TIER_FOUR`), temporadas **2023 en adelante** (2015 y 2020 → HTTP 403),
**10 llamadas/min** (headers `X-Requests-Available-Minute` y `X-RequestCounter-Reset`).
No incluye cuotas de apuestas (`odds.msg`) ni estadio del partido (`venue` siempre nulo).

| Entidad (endpoint) | Granularidad | Clave natural | Campos relevantes | Notas |
|---|---|---|---|---|
| Competición (`/competitions`) | 1 fila por competición | `id` (también `code`: `PL`, `PD`, `EC`) | `name`, `type` (`LEAGUE`/`CUP`), `plan`, `currentSeason.{startDate,endDate,currentMatchday}` | Carga full |
| Partido (`/competitions/{code}/matches`) | 1 fila por partido | `id` | `utcDate` (UTC), `status`, `matchday`, `stage`, `group`, `homeTeam.id`, `awayTeam.id`, `score.*`, `referees[]`, `lastUpdated` | Ver estados y marcador abajo |
| Equipo y plantilla (`/competitions/{code}/teams`) | 1 fila por equipo y temporada | `teams[].id` | `name`, `shortName`, `tla`, `venue`, `founded`, `coach.*`, `squad[].{id,name,position,dateOfBirth,nationality}` | `coach` nulo en el 58 % de los equipos. `tla` **no es única** (71 valores para 73 equipos) |
| Tabla de posiciones (`/competitions/{code}/standings`) | 1 fila por equipo, tipo de tabla y fecha de consulta | (`season.id`, `standings[].type`, `team.id`) | `position`, `playedGames`, `won/draw/lost`, `points`, `goalsFor/Against`, `form` | `type` ∈ `TOTAL`/`HOME`/`AWAY`. La Euro no tiene tabla (HTTP 404). Base del snapshot diario |
| Goleadores (`/competitions/{code}/scorers`) | 1 fila por jugador y temporada | (`season.id`, `player.id`) | `goals`, `assists`, `penalties`, `playedMatches`, `player.dateOfBirth` | `assists` y `penalties` pueden ser nulos |
| Detalle de partido (`/matches/{id}`) | 1 partido | `id` | Igual que la lista | En el plan gratuito no añade alineaciones ni goles detallados |
| Persona (`/persons/{id}`) | 1 jugador | `id` | `name`, `firstName`, `lastName`, `dateOfBirth`, `nationality`, `position`, `currentTeam` | `currentTeam` puede ser la **selección**, no el club (caso Mbappé → France) |

**Estados de partido** (`status`): observados `FINISHED`, `TIMED` (fecha y hora confirmadas) y
`SCHEDULED` (fecha sin confirmar). Según la documentación también existen `IN_PLAY`, `PAUSED`,
`POSTPONED`, `SUSPENDED`, `CANCELLED` y `AWARDED` (no observados, pendiente de verificar). Un
partido reprogramado cambia `utcDate` y `status`: es el caso de "datos tardíos" que el MERGE de
Silver debe absorber.

**`lastUpdated` no sirve como watermark por partido:** en PL 2026 los 380 partidos tienen el
mismo valor (la marca de refresco de la competición), y en PL 2024 solo hay 2 valores distintos.
→ El incremental debe ser una **ventana de fechas (`dateFrom`/`dateTo`) con margen hacia atrás**,
más un `MERGE` por `id` (se decide en la Fase 2).

---

## 3. API-Football (api-sports.io, v3)

**Acceso:** header `x-apisports-key`. Plan gratuito: **temporadas 2022–2024** ("Free plans do not
have access to this season, try from 2022 to 2024"), **100 llamadas/día y 10/min** (headers
`x-ratelimit-requests-limit/remaining` para el día y `x-ratelimit-limit/remaining` para el
minuto). **No permite el parámetro `ids`** (varios partidos por llamada).

**Sobre común** a todos los endpoints: `{get, parameters, errors, results, paging{current,total},
response}`.
- Los errores de plan o de parámetros llegan con **HTTP 200** y `errors` no vacío (objeto o lista).
- Una key inválida responde HTTP 403.
- Las respuestas con error de plan parecen no descontar cuota.

| Entidad (endpoint) | Granularidad | Clave natural | Campos relevantes | Notas |
|---|---|---|---|---|
| Liga (`/leagues`) | 1 fila por liga, con sus temporadas | `league.id` | `seasons[].{year,current,coverage}` | 1 llamada devuelve todas las ligas (3,3 MB) |
| Partido (`/fixtures?league&season`) | 1 fila por partido | `fixture.id` | `fixture.{date,timestamp,referee,venue.{id,name,city},status.{short,elapsed}}`, `league.round`, `teams.{home,away}.{id,winner}`, `goals`, `score.*` | 1 llamada = temporada completa (380 partidos). **Única fuente con estadio por partido** |
| Estadísticas de equipo (`/fixtures/statistics?fixture`) | 1 fila por partido, equipo y tipo de estadística | (`fixture`, `team.id`, `statistics[].type`) | 18 tipos (`Shots on Goal`, `Ball Possession`…) | Formato largo (tipo/valor). `value` mezcla int, null y texto (`"55%"`) → pivotar y convertir tipos en Silver |
| Estadísticas de jugador por partido (`/fixtures/players?fixture`) | 1 fila por partido y jugador | (`fixture`, `player.id`) | `games.{minutes,position,rating,substitute}`, `goals.*`, `shots.*`, `passes.*`, `cards.*` | `rating` y `passes.accuracy` llegan como **texto**. La API tiene la errata `penalty.commited` |
| Alineaciones (`/fixtures/lineups?fixture`) | 1 fila por partido y equipo | (`fixture`, `team.id`) | `formation`, `coach.{id,name}`, `startXI[]`, `substitutes[]` | Fuente del entrenador por partido (SCD2 de `dim_team`) |
| Eventos (`/fixtures/events?fixture`) | 1 fila por evento | Sin clave propia → (`fixture`, `time.elapsed`, `time.extra`, `team.id`, `player.id`, `type`, `detail`) | `type` (`Goal`/`Card`/`subst`/`Var`), `detail`, `assist` | Sin id de evento: la deduplicación exige clave compuesta |
| Jugadores de la temporada (`/players?league&season&page`) | 1 fila por jugador, con estadísticas por equipo | `player.id` (global entre competiciones) | `firstname`, `lastname`, `birth.{date,country}`, `nationality`, `height`, `weight`, `statistics[].team` | Paginado: **57 páginas en PL, 53 en La Liga, 32 en la Euro**. Varias entradas en `statistics[]` si el jugador cambió de equipo. `age` es la edad actual: no guardarla, derivarla de `birth.date`. La API tiene la errata `appearences` |
| Lesiones (`/injuries?league&season`) | 1 fila por jugador y partido perdido | (`player.id`, `fixture.id`) | `player.type` (`Missing Fixture`/`Questionable`), `player.reason` | 3.168 filas en PL 2024 en 1 llamada |
| Equipos (`/teams?league&season`) | 1 fila por equipo | `team.id` | `name`, `code`, `country`, `national`, `venue.{id,name,city,capacity}` | `code` no es único |
| Tabla (`/standings?league&season`) | 1 fila por equipo y grupo | (`league.id`, `season`, `team.id`) | `rank`, `points`, `all/home/away.*`, `form`, `description` | Lista anidada `standings[][]` (un nivel por grupo) |

**Estados** (`fixture.status.short`): observados `FT`, `AET` (con prórroga) y `PEN` (con tanda).
Según la documentación existen también `NS`, `TBD`, `PST`, `CANC`, `ABD`, `AWD`, `WO` y los de
partido en juego (no observados en temporadas cerradas).

---

## 4. StatsBomb Open Data

**Acceso:** archivos JSON públicos en `github.com/statsbomb/open-data` (rama `master`), sin key y
sin límite publicado. **Atribución obligatoria** en cualquier publicación.

| Entidad (archivo) | Granularidad | Clave natural | Campos relevantes | Notas |
|---|---|---|---|---|
| Competición-temporada (`competitions.json`) | 1 fila por competición y temporada | (`competition_id`, `season_id`) | `match_available`, `match_available_360`, `match_updated` | Detecta temporadas nuevas o actualizadas |
| Partido (`matches/{comp}/{season}.json`) | 1 fila por partido | `match_id` | `match_date`, `kick_off`, `home/away_team.*`, `managers[].{id,name,dob}`, `home_score`, `away_score`, `stadium`, `referee`, `last_updated`, `last_updated_360`, `metadata.data_version` | **`last_updated` varía por partido** (436 valores en 466 partidos): es el watermark de la carga por archivos y detecta correcciones |
| Evento (`events/{match_id}.json`) | 1 fila por evento | `id` (UUID) | `index`, `period`, `minute`, `second`, `type.name` (30 tipos), `team`, `player`, `position`, `location` [x, y], `possession`, `play_pattern` y un objeto por tipo (`pass`, `shot`, `carry`, `duel`…) | ~3.800 eventos por partido. Campos muy dispersos por tipo. Tiros: `shot.statsbomb_xg`, `shot.outcome`, `shot.freeze_frame[]`. Campo de 120 × 80 |
| Alineación (`lineups/{match_id}.json`) | 1 fila por partido y equipo, con jugadores anidados | (`match_id`, `team_id`, `player_id`) | `player_name`, `player_nickname`, `jersey_number`, `country`, `positions[].{from,to,start_reason,end_reason}`, `cards[]` | **Sin fecha de nacimiento** |
| 360 (`three-sixty/{match_id}.json`) | 1 fila por evento con captura | `event_uuid` (→ `events.id`) | `visible_area[]`, `freeze_frame[].{teammate,actor,keeper,location}` | ~3.400 por partido, ~6,5 MB por archivo. Solo en La Liga 2020/21 y Euro 2024 dentro del alcance |

---

## 5. Semántica del marcador (importante para validar goles)

Las fuentes usan los mismos nombres de campo con **significados distintos**. Casos verificados en
la Euro 2024:

| Partido | football-data `fullTime` | API-Football `goals` / `score.fulltime` | StatsBomb `home_score`–`away_score` |
|---|---|---|---|
| POR–SVN (0–0, penaltis 3–0) | **3–0** (suma la tanda) | `goals` 0–0 · `fulltime` 0–0 | 0–0 |
| ESP–GER (1–1, prórroga 2–1) | 2–1 | `goals` 2–1 · `fulltime` **1–1** (solo 90 min) | 2–1 |

Reglas para Silver:
- **Goles del partido** = `regularTime + extraTime` en football-data, cuando hay `duration` ≠
  `REGULAR`; si no, `fullTime`. En API-Football, `goals`.
- La tanda de penaltis se guarda aparte (`penalty_home`, `penalty_away`) y **nunca** suma goles.
- Tipo de desenlace: `score.duration` (`REGULAR`/`EXTRA_TIME`/`PENALTY_SHOOTOUT`) en
  football-data; `status.short` (`FT`/`AET`/`PEN`) en API-Football.
- StatsBomb (`home_score`/`away_score`) coincide con el criterio anterior: incluye la prórroga y
  excluye la tanda.

---

## 6. Identificadores y mapeo entre fuentes

Cada fuente tiene sus propios IDs de competición, equipo, jugador y partido. No existe ningún ID
común. Medición con una normalización simple (minúsculas, sin tildes, sin "FC/CF/Club…"):

| Comparación | Coincidencias | Casos que fallan |
|---|---|---|
| Equipos PL 2024: football-data ↔ API-Football | 13/20 (65 %) | "Wolverhampton Wanderers FC" ↔ "Wolves", "Brighton & Hove Albion FC" ↔ "Brighton", "Tottenham Hotspur FC" ↔ "Tottenham" |
| Equipos La Liga 2024: football-data ↔ API-Football | 13/20 (65 %) | "RC Celta de Vigo" ↔ "Celta Vigo", "Real Betis Balompié" ↔ "Real Betis" |
| Selecciones Euro 2024: football-data ↔ API-Football | 23/24 | "Turkey" ↔ "Türkiye" |
| Selecciones Euro 2024: football-data ↔ StatsBomb | 23/24 | "Czechia" ↔ "Czech Republic" |
| Jugadores PL 2024: API-Football (40) ↔ plantillas de football-data, por fecha de nacimiento + apellido | 20 únicos, 2 ambiguos, 18 sin pareja | Apodos ("Rodri"), jugadores cedidos o que salieron a mitad de temporada, fechas sospechosas (`1996-01-01`) |

**Atributos disponibles para las reglas de coincidencia:**

| Atributo | football-data | API-Football | StatsBomb |
|---|---|---|---|
| Nombre de equipo | `name`, `shortName`, `tla` | `name`, `code` | `team_name` |
| País del equipo | `area.name` | `country` | `country.name` |
| Nombre de jugador | `name` (completo) | `firstname`, `lastname`, `name` (abreviado) | `player_name`, `player_nickname` |
| Fecha de nacimiento | ✅ `dateOfBirth` | ✅ `birth.date` | ❌ |
| Nacionalidad | ✅ | ✅ | ✅ `country` |
| Partido | fecha UTC + equipos | fecha UTC + equipos | fecha + hora local + equipos |

**Implicaciones para la Fase 3:**
- `map_team`: reglas en cascada:
  1. Nombre normalizado igual.
  2. `shortName` o alias conocidos.
  3. Similitud de tokens dentro del mismo país.
  4. El resto va a la cola de revisión manual.
- `map_player`: football-data ↔ API-Football por fecha de nacimiento más similitud de nombre.
  Con StatsBomb, sin fecha de nacimiento, por nombre + nacionalidad + equipo y temporada, **con
  más casos a revisión manual**.
- `map_match`: fecha (en UTC) + equipo local + equipo visitante, una vez mapeados los equipos.
  Es posible en PL/La Liga 2024 (football-data ↔ API-Football) y en la Euro 2024 (las 3 fuentes).

---

## 7. Presupuesto diario de llamadas

### API-Football (100/día; 10 de reserva → **90 útiles/día**; 10/min)

Sin el parámetro `ids`, cada partido cuesta 1 llamada por endpoint. Propuesta base: por partido
`fixtures/statistics` + `fixtures/players` (2 llamadas). Las alineaciones y los eventos quedan
como opcionales.

| Bloque | Cálculo | Llamadas | Días (90/día) |
|---|---|---|---|
| Euro 2024 | 4 (fixtures, teams, standings, injuries) + 32 págs. players + 51 × 2 | 138 | ~1,5 |
| Premier League 2024 | 4 + 57 págs. + 380 × 2 | 821 | ~9 |
| La Liga 2024 | 4 + 53 págs. + 380 × 2 | 817 | ~9 |
| **Total base** | | **~1.776** | **~20** |
| Opcional: alineaciones + eventos | 811 partidos × 2 | +1.622 | +18 |

→ La carga de API-Football es un **relleno histórico limitado por presupuesto**: cada ejecución
diaria toma los `fixture_id` pendientes (orden Euro → PL → La Liga) hasta agotar las 90 llamadas.
Por eso `ctl_api_budget` es obligatoria.

### football-data.org (10/min, sin límite diario observado)

| Carga | Llamadas |
|---|---|
| Histórica 2024/25, una sola vez (partidos, equipos, tablas y goleadores de PL, PD y EC) | ~11 |
| Diaria de la temporada en curso (PL + PD): partidos por ventana de fechas + tabla (snapshot) + goleadores | ~6/día |
| Semanal: plantillas y entrenador (SCD2) | ~2/semana |

La restricción real es el **límite por minuto**: el notebook o pipeline debe espaciar las llamadas
(el `RateLimiter` del cliente ya lo hace).

### StatsBomb (sin límite; la restricción es el volumen)

| Bloque | Archivos | Volumen JSON aprox. |
|---|---|---|
| PL 2015/16: 380 partidos × (eventos + alineaciones) | ~760 | ~0,9 GB |
| La Liga 2020/21: 35 × (eventos + alineaciones + 360) | ~105 | ~0,3 GB |
| Euro 2024: 51 × (eventos + alineaciones + 360) | ~153 | ~0,45 GB |
| **Total** | **~1.020** | **~1,7 GB** |

Tamaños medios medidos: eventos 2,4 MB, 360 6,5 MB, alineaciones 17 KB por partido.

---

## 8. Bronze (`lh_bronze`)

Formato y escritura según [ADR-007](decisiones.md#adr-007--formato-de-bronze-e-idempotencia).

**Archivos crudos:** `Files/raw/<fuente>/<entidad>/ingest_date=YYYY-MM-DD/<batch_id>/<nombre>.json`.
Cada archivo es la respuesta tal cual; en API-Football incluye el sobre `get/parameters/errors/paging`.

**Esquema común de las tablas Delta** (una tabla por fuente y entidad, nombre `<fuente>_<entidad>`):

| Columna | Tipo | Descripción |
|---|---|---|
| `record_key` | string | Clave natural del registro (ver tabla siguiente) |
| `record_hash` | string | SHA-256 del registro sin campos volátiles. Si no cambia, no se inserta una versión nueva |
| `record_context` | string (JSON) | Contexto de la petición que el registro no trae dentro (competición, temporada, equipo, partido…) |
| `payload` | string (JSON) | El registro tal cual lo devolvió la fuente |
| `_source` | string | `football_data`, `api_football` o `statsbomb` |
| `_config_id` | string | Configuración de `ctl_source_config` que lo cargó |
| `_batch_id` | string | Lote de ingesta (`YYYYMMDDTHHMMSSZ_xxxxxxxx`) |
| `_file_name` | string | Ruta del archivo crudo de origen |
| `_ingested_at` | timestamp | Momento en que se insertó esta versión |

Una clave puede tener **varias versiones**: la vigente es la de mayor `_ingested_at`.

| Tabla | Registro | `record_key` | Configuración | Volumen (feature, 2026-10-09) |
|---|---|---|---|---|
| `football_data_competitions` | Competición | `id` | `fd_competitions` (full) | 13 |
| `football_data_matches` | Partido | `id` | `fd_matches_current` (window), `fd_matches_history` (season_full) | ~970 |
| `football_data_teams` | Equipo con plantilla y entrenador en una temporada | `<season.id>\|<team.id>` | `fd_teams` (season_full) | 104 |
| `football_data_standings` | Tabla completa de una competición y temporada | `<code>\|<season.id>` | `fd_standings` (snapshot) | 1 versión por cambio |
| `football_data_scorers` | Goleadores de una competición y temporada | `<code>\|<season.id>` | `fd_scorers` (snapshot) | 1 versión por cambio |
| `api_football_fixtures` | Partido | `fixture.id` | `af_fixtures` (season_full) | 811 |
| `api_football_teams` | Equipo y estadio en una liga y temporada | `<league>\|<season>\|<team.id>` | `af_teams` (season_full) | 64 |
| `api_football_injuries` | Baja de un jugador en un partido | `<player.id>\|<fixture.id>` | `af_injuries` (season_full) | 5.592 |
| `api_football_players` | Jugador en un equipo y temporada (con estadísticas) | `<league>\|<season>\|<team>\|<player.id>` | `af_players` (budgeted_backfill) | relleno en curso |
| `api_football_fixture_statistics` | Estadísticas de los dos equipos en un partido | `fixture_id` | `af_fixture_statistics` (budgeted_backfill) | relleno en curso |
| `api_football_fixture_players` | Estadísticas de los jugadores en un partido | `fixture_id` | `af_fixture_players` (budgeted_backfill) | relleno en curso |
| `statsbomb_competitions` | Competición y temporada disponibles | `<competition_id>\|<season_id>` | `sb_competitions` (full) | 80 |
| `statsbomb_matches` | Partido (con `last_updated`) | `match_id` | `sb_matches` (full) | 466 |
| `statsbomb_events` | Evento | `id` (UUID) | `sb_match_files` (file_incremental) | 1.640.727 |
| `statsbomb_lineups` | Alineación de un equipo en un partido | `<match_id>\|<team_id>` | `sb_match_files` | 932 |
| `statsbomb_three_sixty` | Captura 360 de un evento | `event_uuid` | `sb_match_files` | 293.370 |

Notas:
- `api_football_players` se carga **por equipo**, páginas 1 a 3 (tope del plan gratuito). Los
  equipos con más páginas quedan marcados como `truncated` en el watermark de `af_players`.
- `statsbomb_*` de eventos: `record_context` incluye `match_id` y `version`
  (`last_updated|last_updated_360`). Si StatsBomb corrige un partido, se vuelve a descargar y
  solo se insertan los eventos que cambiaron.

## 9. Silver (`lh_silver`)

_Pendiente (Fase 3)._

## 10. Gold (`wh_gold` / `lh_gold`)

_Pendiente (Fase 4)._

## 11. Control y metadatos

Tablas Delta en `lh_bronze`, creadas por `nb_bronze_setup` (DDL en `src/ingestion/control.py`).

**`ctl_source_config`**: qué se ingiere y cómo. Se sincroniza desde `src/ingestion/source_config.py`.

| Columna | Descripción |
|---|---|
| `config_id` | Identificador (p. ej. `fd_matches_current`) |
| `source`, `entity` | Fuente y entidad |
| `load_type` | `full`, `window`, `season_full`, `snapshot`, `budgeted_backfill`, `file_incremental` |
| `params` | JSON: `targets`, `lookback_days`, `daily_quota`, `max_page`, `max_matches_per_run`… |
| `watermark_column` | Columna de referencia del incremental (documental) |
| `priority` | Orden lógico (documental; la pipeline no lo garantiza, ADR-010) |
| `is_active` | Si la pipeline la ejecuta |
| `description`, `updated_at` | Descripción y última modificación |

**`ctl_watermark`**: último estado procesado por configuración.

| `watermark_type` | Valor | Usado por |
|---|---|---|
| `date` | Fecha de la última ejecución (`YYYY-MM-DD`) | `window`, `snapshot` |
| `completed_targets` | Lista JSON de objetivos cerrados ya cargados | `season_full` |
| `team_page_progress` | JSON por equipo: `next_page`, `total_pages`, `truncated` | `af_players` |
| `backfill_progress` | JSON `{"done": n, "pending": m}` | `af_fixture_*` |
| `max_last_updated` | Mayor `last_updated` procesado | `sb_match_files` |

**`ctl_run_log`**: una fila por ejecución de una configuración. Se escribe también si falla.

| Columna | Descripción |
|---|---|
| `run_id`, `batch_id`, `pipeline_run_id` | Identificadores de la ejecución, el lote y la ejecución de la pipeline |
| `config_id`, `source`, `entity`, `load_type` | Qué se ejecutó |
| `started_at`, `finished_at` | Duración (UTC) |
| `status` | `succeeded`, `budget_exhausted`, `failed`, `skipped` |
| `api_calls` | Llamadas que consumen cuota (no incluye `/status`) |
| `files_written`, `records_read`, `records_inserted` | Volumen: leídos frente a versiones nuevas insertadas |
| `watermark_before`, `watermark_after` | Evidencia del incremental |
| `error_message` | Error, si lo hubo |
| `code_version` | Versión del wheel `fabric_futbol` que corrió (ADR-008) |

**`ctl_api_budget`**: uso diario (UTC) de las APIs con límite.

| Columna | Descripción |
|---|---|
| `source`, `budget_date` | API y día |
| `daily_limit`, `reserve` | 100 y 10 en API-Football |
| `calls_used` | Contador propio, conservador: máximo entre nuestras llamadas y las del proveedor |
| `provider_used` | Uso según los headers del proveedor (no cuenta los errores de plan) |

**`ctl_file_manifest`**: archivos ya procesados en la carga por archivos.

| Columna | Descripción |
|---|---|
| `source`, `file_key` | Fuente y archivo lógico (p. ej. `match/3943043`) |
| `source_last_updated` | Versión procesada (`last_updated\|last_updated_360`) |
| `batch_id`, `processed_at` | Lote y momento del último procesamiento |
