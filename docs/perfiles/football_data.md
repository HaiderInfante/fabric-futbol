# Perfil de muestras: football-data.org

> Generado por `scripts/explore/profile_samples.py` a partir de `data/samples/`. Se regenera en cada ejecución: no editar a mano. La interpretación de negocio está en `docs/diccionario_datos.md`.

Leyenda: *Presencia* = % de objetos padre que tienen el campo (— en elementos de lista); *Distintos* = valores no nulos distintos; *¿Clave?* = único, sin nulos y presente en el 100 % de los casos dentro de la muestra.

## `match_detail`

- Archivos: 2 (560542, 564634) · 0.0 MB
- Registros perfilados: 2

| Campo | Tipos | Presencia | Nulos | Distintos | Ejemplo | ¿Clave? |
|---|---|---|---|---|---|---|
| `area` | object | 100 % | 0 % | — |  |  |
| `area.id` | int | 100 % | 0 % | 2 | `2072` |  |
| `area.name` | str | 100 % | 0 % | 2 | `England` |  |
| `area.code` | str | 100 % | 0 % | 2 | `ENG` |  |
| `area.flag` | str | 100 % | 0 % | 2 | `https://crests.football-data.org/770.svg` |  |
| `competition` | object | 100 % | 0 % | — |  |  |
| `competition.id` | int | 100 % | 0 % | 2 | `2021` |  |
| `competition.name` | str | 100 % | 0 % | 2 | `Premier League` |  |
| `competition.code` | str | 100 % | 0 % | 2 | `PL` |  |
| `competition.type` | str | 100 % | 0 % | 1 | `LEAGUE` |  |
| `competition.emblem` | str | 100 % | 0 % | 2 | `https://crests.football-data.org/PL.png` |  |
| `season` | object | 100 % | 0 % | — |  |  |
| `season.id` | int | 100 % | 0 % | 2 | `2502` |  |
| `season.startDate` | str | 100 % | 0 % | 2 | `2026-08-21` |  |
| `season.endDate` | str | 100 % | 0 % | 1 | `2027-05-30` |  |
| `season.currentMatchday` | int | 100 % | 0 % | 2 | `6` |  |
| `season.winner` | null | 100 % | 100 % | 0 |  |  |
| `id` | int | 100 % | 0 % | 2 | `560542` |  |
| `utcDate` | str | 100 % | 0 % | 2 | `2026-08-21T19:00:00Z` |  |
| `status` | str | 100 % | 0 % | 1 | `FINISHED` |  |
| `venue` | null | 100 % | 100 % | 0 |  |  |
| `matchday` | int | 100 % | 0 % | 1 | `1` |  |
| `stage` | str | 100 % | 0 % | 1 | `REGULAR_SEASON` |  |
| `group` | null | 100 % | 100 % | 0 |  |  |
| `lastUpdated` | str | 100 % | 0 % | 2 | `2026-09-29T00:20:39Z` |  |
| `homeTeam` | object | 100 % | 0 % | — |  |  |
| `homeTeam.id` | int | 100 % | 0 % | 2 | `57` |  |
| `homeTeam.name` | str | 100 % | 0 % | 2 | `Arsenal FC` |  |
| `homeTeam.shortName` | str | 100 % | 0 % | 2 | `Arsenal` |  |
| `homeTeam.tla` | str | 100 % | 0 % | 2 | `ARS` |  |
| `homeTeam.crest` | str | 100 % | 0 % | 2 | `https://crests.football-data.org/57.png` |  |
| `awayTeam` | object | 100 % | 0 % | — |  |  |
| `awayTeam.id` | int | 100 % | 0 % | 2 | `1076` |  |
| `awayTeam.name` | str | 100 % | 0 % | 2 | `Coventry City FC` |  |
| `awayTeam.shortName` | str | 100 % | 0 % | 2 | `Coventry City` |  |
| `awayTeam.tla` | str | 100 % | 0 % | 2 | `COV` |  |
| `awayTeam.crest` | str | 100 % | 0 % | 2 | `https://crests.football-data.org/1076.p…` |  |
| `score` | object | 100 % | 0 % | — |  |  |
| `score.winner` | str | 100 % | 0 % | 1 | `HOME_TEAM` |  |
| `score.duration` | str | 100 % | 0 % | 1 | `REGULAR` |  |
| `score.fullTime` | object | 100 % | 0 % | — |  |  |
| `score.fullTime.home` | int | 100 % | 0 % | 1 | `3` |  |
| `score.fullTime.away` | int | 100 % | 0 % | 1 | `0` |  |
| `score.halfTime` | object | 100 % | 0 % | — |  |  |
| `score.halfTime.home` | int | 100 % | 0 % | 2 | `2` |  |
| `score.halfTime.away` | int | 100 % | 0 % | 1 | `0` |  |
| `odds` | object | 100 % | 0 % | — |  |  |
| `odds.msg` | str | 100 % | 0 % | 1 | `Activate Odds-Package in User-Panel to …` |  |
| `referees` | array | 100 % | 0 % | — |  |  |
| `referees[]` | object | — | 0 % | — |  |  |
| `referees[].id` | int | 100 % | 0 % | 2 | `11620` |  |
| `referees[].name` | str | 100 % | 0 % | 2 | `Thomas Bramall` |  |
| `referees[].type` | str | 100 % | 0 % | 1 | `REFEREE` |  |
| `referees[].nationality` | str | 100 % | 0 % | 2 | `England` |  |

## `matches`

- Archivos: 5 (EC_2024, PD_2024, PD_2026, PL_2024, PL_2026) · 1.7 MB
- Registros perfilados: 5

| Campo | Tipos | Presencia | Nulos | Distintos | Ejemplo | ¿Clave? |
|---|---|---|---|---|---|---|
| `filters` | object | 100 % | 0 % | — |  |  |
| `filters.season` | int | 100 % | 0 % | 2 | `2024` |  |
| `resultSet` | object | 100 % | 0 % | — |  |  |
| `resultSet.count` | int | 100 % | 0 % | 2 | `51` |  |
| `resultSet.first` | str | 100 % | 0 % | 5 | `2024-06-14` |  |
| `resultSet.last` | str | 100 % | 0 % | 3 | `2024-07-14` |  |
| `resultSet.played` | int | 100 % | 0 % | 4 | `51` |  |
| `competition` | object | 100 % | 0 % | — |  |  |
| `competition.id` | int | 100 % | 0 % | 3 | `2018` |  |
| `competition.name` | str | 100 % | 0 % | 3 | `European Championship` |  |
| `competition.code` | str | 100 % | 0 % | 3 | `EC` |  |
| `competition.type` | str | 100 % | 0 % | 2 | `CUP` |  |
| `competition.emblem` | str | 100 % | 0 % | 3 | `https://crests.football-data.org/ec.png` |  |
| `matches` | array | 100 % | 0 % | — |  |  |
| `matches[]` | object | — | 0 % | — |  |  |
| `matches[].area` | object | 100 % | 0 % | — |  |  |
| `matches[].area.id` | int | 100 % | 0 % | 3 | `2077` |  |
| `matches[].area.name` | str | 100 % | 0 % | 3 | `Europe` |  |
| `matches[].area.code` | str | 100 % | 0 % | 3 | `EUR` |  |
| `matches[].area.flag` | str | 100 % | 0 % | 3 | `https://crests.football-data.org/EUR.svg` |  |
| `matches[].competition` | object | 100 % | 0 % | — |  |  |
| `matches[].competition.id` | int | 100 % | 0 % | 3 | `2018` |  |
| `matches[].competition.name` | str | 100 % | 0 % | 3 | `European Championship` |  |
| `matches[].competition.code` | str | 100 % | 0 % | 3 | `EC` |  |
| `matches[].competition.type` | str | 100 % | 0 % | 2 | `CUP` |  |
| `matches[].competition.emblem` | str | 100 % | 0 % | 3 | `https://crests.football-data.org/ec.png` |  |
| `matches[].season` | object | 100 % | 0 % | — |  |  |
| `matches[].season.id` | int | 100 % | 0 % | 5 | `1537` |  |
| `matches[].season.startDate` | str | 100 % | 0 % | 5 | `2024-06-14` |  |
| `matches[].season.endDate` | str | 100 % | 0 % | 3 | `2024-07-14` |  |
| `matches[].season.currentMatchday` | int | 100 % | 0 % | 4 | `7` |  |
| `matches[].season.winner` | null, object | 100 % | 97 % | — |  |  |
| `matches[].season.winner.id` | int | 100 % | 0 % | 1 | `760` |  |
| `matches[].season.winner.name` | str | 100 % | 0 % | 1 | `Spain` |  |
| `matches[].season.winner.shortName` | str | 100 % | 0 % | 1 | `Spain` |  |
| `matches[].season.winner.tla` | str | 100 % | 0 % | 1 | `ESP` |  |
| `matches[].season.winner.crest` | str | 100 % | 0 % | 1 | `https://crests.football-data.org/760.svg` |  |
| `matches[].season.winner.address` | str | 100 % | 0 % | 1 | `Ramón y Cajal, s/n Las Rozas 28230` |  |
| `matches[].season.winner.website` | str | 100 % | 0 % | 1 | `http://www.rfef.es` |  |
| `matches[].season.winner.founded` | int | 100 % | 0 % | 1 | `1909` |  |
| `matches[].season.winner.clubColors` | str | 100 % | 0 % | 1 | `Red / Blue / Yellow` |  |
| `matches[].season.winner.venue` | null | 100 % | 100 % | 0 |  |  |
| `matches[].season.winner.lastUpdated` | str | 100 % | 0 % | 1 | `2026-06-01T09:41:19Z` |  |
| `matches[].id` | int | 100 % | 0 % | 1571 | `428747` | ✔ |
| `matches[].utcDate` | str | 100 % | 0 % | 792 | `2024-06-14T19:00:00Z` |  |
| `matches[].status` | str | 100 % | 0 % | 3 | `FINISHED` |  |
| `matches[].matchday` | int | 100 % | 0 % | 38 | `1` |  |
| `matches[].stage` | str | 100 % | 0 % | 6 | `GROUP_STAGE` |  |
| `matches[].group` | null, str | 100 % | 98 % | 6 | `GROUP_A` |  |
| `matches[].lastUpdated` | str | 100 % | 0 % | 10 | `2024-07-23T10:21:24Z` |  |
| `matches[].homeTeam` | object | 100 % | 0 % | — |  |  |
| `matches[].homeTeam.id` | int | 100 % | 0 % | 73 | `759` |  |
| `matches[].homeTeam.name` | str | 100 % | 0 % | 73 | `Germany` |  |
| `matches[].homeTeam.shortName` | str | 100 % | 0 % | 73 | `Germany` |  |
| `matches[].homeTeam.tla` | str | 100 % | 0 % | 71 | `GER` |  |
| `matches[].homeTeam.crest` | str | 100 % | 0 % | 73 | `https://crests.football-data.org/759.svg` |  |
| `matches[].awayTeam` | object | 100 % | 0 % | — |  |  |
| `matches[].awayTeam.id` | int | 100 % | 0 % | 73 | `8873` |  |
| `matches[].awayTeam.name` | str | 100 % | 0 % | 73 | `Scotland` |  |
| `matches[].awayTeam.shortName` | str | 100 % | 0 % | 73 | `Scotland` |  |
| `matches[].awayTeam.tla` | str | 100 % | 0 % | 71 | `SCO` |  |
| `matches[].awayTeam.crest` | str | 100 % | 0 % | 73 | `https://crests.football-data.org/814.svg` |  |
| `matches[].score` | object | 100 % | 0 % | — |  |  |
| `matches[].score.winner` | null, str | 100 % | 41 % | 3 | `HOME_TEAM` |  |
| `matches[].score.duration` | str | 100 % | 0 % | 3 | `REGULAR` |  |
| `matches[].score.fullTime` | object | 100 % | 0 % | — |  |  |
| `matches[].score.fullTime.home` | int, null | 100 % | 41 % | 8 | `5` |  |
| `matches[].score.fullTime.away` | int, null | 100 % | 41 % | 7 | `1` |  |
| `matches[].score.halfTime` | object | 100 % | 0 % | — |  |  |
| `matches[].score.halfTime.home` | int, null | 100 % | 41 % | 6 | `3` |  |
| `matches[].score.halfTime.away` | int, null | 100 % | 41 % | 5 | `0` |  |
| `matches[].odds` | object | 100 % | 0 % | — |  |  |
| `matches[].odds.msg` | str | 100 % | 0 % | 1 | `Activate Odds-Package in User-Panel to …` |  |
| `matches[].referees` | array | 100 % | 0 % | — |  |  |
| `matches[].referees[]` | object | — | 0 % | — |  |  |
| `matches[].referees[].id` | int | 100 % | 0 % | 70 | `9374` |  |
| `matches[].referees[].name` | str | 100 % | 0 % | 70 | `Clément Turpin` |  |
| `matches[].referees[].type` | str | 100 % | 0 % | 1 | `REFEREE` |  |
| `matches[].referees[].nationality` | null, str | 100 % | 2 % | 17 | `France` |  |
| `matches[].score.regularTime` | object | <1 % | 0 % | — |  |  |
| `matches[].score.regularTime.home` | int | 100 % | 0 % | 2 | `1` |  |
| `matches[].score.regularTime.away` | int | 100 % | 0 % | 2 | `1` |  |
| `matches[].score.extraTime` | object | <1 % | 0 % | — |  |  |
| `matches[].score.extraTime.home` | int | 100 % | 0 % | 2 | `1` |  |
| `matches[].score.extraTime.away` | int | 100 % | 0 % | 1 | `0` |  |
| `matches[].score.penalties` | object | <1 % | 0 % | — |  |  |
| `matches[].score.penalties.home` | int | 100 % | 0 % | 2 | `3` |  |
| `matches[].score.penalties.away` | int | 100 % | 0 % | 3 | `0` |  |

## `person`

- Archivos: 2 (3374, 3754) · 0.0 MB
- Registros perfilados: 2

| Campo | Tipos | Presencia | Nulos | Distintos | Ejemplo | ¿Clave? |
|---|---|---|---|---|---|---|
| `id` | int | 100 % | 0 % | 2 | `3374` |  |
| `name` | str | 100 % | 0 % | 2 | `Kylian Mbappé` |  |
| `firstName` | str | 100 % | 0 % | 2 | `Kylian` |  |
| `lastName` | str | 100 % | 0 % | 2 | `Mbappé` |  |
| `dateOfBirth` | str | 100 % | 0 % | 2 | `1998-12-20` |  |
| `nationality` | str | 100 % | 0 % | 2 | `France` |  |
| `section` | str | 100 % | 0 % | 1 | `Offence` |  |
| `position` | str | 100 % | 0 % | 1 | `Offence` |  |
| `shirtNumber` | int | 100 % | 0 % | 1 | `10` |  |
| `lastUpdated` | str | 100 % | 0 % | 1 | `2026-06-01T11:16:30Z` |  |
| `currentTeam` | object | 100 % | 0 % | — |  |  |
| `currentTeam.area` | object | 100 % | 0 % | — |  |  |
| `currentTeam.area.id` | int | 100 % | 0 % | 2 | `2081` |  |
| `currentTeam.area.name` | str | 100 % | 0 % | 2 | `France` |  |
| `currentTeam.area.code` | str | 100 % | 0 % | 2 | `FRA` |  |
| `currentTeam.area.flag` | str | 100 % | 0 % | 2 | `https://crests.football-data.org/773.svg` |  |
| `currentTeam.id` | int | 100 % | 0 % | 2 | `773` |  |
| `currentTeam.name` | str | 100 % | 0 % | 2 | `France` |  |
| `currentTeam.shortName` | str | 100 % | 0 % | 2 | `France` |  |
| `currentTeam.tla` | str | 100 % | 0 % | 2 | `FRA` |  |
| `currentTeam.crest` | str | 100 % | 0 % | 2 | `https://crests.football-data.org/773.svg` |  |
| `currentTeam.address` | str | 100 % | 0 % | 2 | `87 Boulevard de Grenelle Paris 75738` |  |
| `currentTeam.website` | str | 100 % | 0 % | 2 | `http://www.fff.fr` |  |
| `currentTeam.founded` | int | 100 % | 0 % | 2 | `1919` |  |
| `currentTeam.clubColors` | str | 100 % | 0 % | 2 | `Blue / White / Red` |  |
| `currentTeam.venue` | null | 100 % | 100 % | 0 |  |  |
| `currentTeam.runningCompetitions` | array | 100 % | 0 % | — |  |  |
| `currentTeam.runningCompetitions[]` | object | — | 0 % | — |  |  |
| `currentTeam.runningCompetitions[].id` | int | 100 % | 0 % | 2 | `2182` |  |
| `currentTeam.runningCompetitions[].name` | str | 100 % | 0 % | 2 | `UEFA Nations League` |  |
| `currentTeam.runningCompetitions[].code` | str | 100 % | 0 % | 2 | `UNL` |  |
| `currentTeam.runningCompetitions[].type` | str | 100 % | 0 % | 1 | `CUP` |  |
| `currentTeam.runningCompetitions[].emblem` | null | 100 % | 100 % | 0 |  |  |
| `currentTeam.contract` | object | 100 % | 0 % | — |  |  |
| `currentTeam.contract.start` | null, str | 100 % | 50 % | 1 | `2017-03` |  |
| `currentTeam.contract.until` | null | 100 % | 100 % | 0 |  |  |

## `scorers`

- Archivos: 2 (PD_2024, PL_2024) · 0.0 MB
- Registros perfilados: 2

| Campo | Tipos | Presencia | Nulos | Distintos | Ejemplo | ¿Clave? |
|---|---|---|---|---|---|---|
| `count` | int | 100 % | 0 % | 1 | `20` |  |
| `filters` | object | 100 % | 0 % | — |  |  |
| `filters.season` | int | 100 % | 0 % | 1 | `2024` |  |
| `filters.limit` | int | 100 % | 0 % | 1 | `20` |  |
| `competition` | object | 100 % | 0 % | — |  |  |
| `competition.id` | int | 100 % | 0 % | 2 | `2014` |  |
| `competition.name` | str | 100 % | 0 % | 2 | `Primera Division` |  |
| `competition.code` | str | 100 % | 0 % | 2 | `PD` |  |
| `competition.type` | str | 100 % | 0 % | 1 | `LEAGUE` |  |
| `competition.emblem` | str | 100 % | 0 % | 2 | `https://crests.football-data.org/laliga…` |  |
| `season` | object | 100 % | 0 % | — |  |  |
| `season.id` | int | 100 % | 0 % | 2 | `2292` |  |
| `season.startDate` | str | 100 % | 0 % | 2 | `2024-08-18` |  |
| `season.endDate` | str | 100 % | 0 % | 1 | `2025-05-25` |  |
| `season.currentMatchday` | int | 100 % | 0 % | 1 | `38` |  |
| `season.winner` | null | 100 % | 100 % | 0 |  |  |
| `scorers` | array | 100 % | 0 % | — |  |  |
| `scorers[]` | object | — | 0 % | — |  |  |
| `scorers[].player` | object | 100 % | 0 % | — |  |  |
| `scorers[].player.id` | int | 100 % | 0 % | 40 | `3374` | ✔ |
| `scorers[].player.name` | str | 100 % | 0 % | 40 | `Kylian Mbappé` | ✔ |
| `scorers[].player.firstName` | str | 100 % | 0 % | 28 | `Kylian` |  |
| `scorers[].player.lastName` | str | 100 % | 0 % | 40 | `Mbappé` | ✔ |
| `scorers[].player.dateOfBirth` | str | 100 % | 0 % | 40 | `1998-12-20` | ✔ |
| `scorers[].player.nationality` | str | 100 % | 0 % | 22 | `France` |  |
| `scorers[].player.section` | str | 100 % | 0 % | 2 | `Offence` |  |
| `scorers[].player.position` | null | 100 % | 100 % | 0 |  |  |
| `scorers[].player.shirtNumber` | int, null | 100 % | 90 % | 4 | `7` |  |
| `scorers[].player.lastUpdated` | str | 100 % | 0 % | 21 | `2026-06-01T11:16:30Z` |  |
| `scorers[].team` | object | 100 % | 0 % | — |  |  |
| `scorers[].team.id` | int | 100 % | 0 % | 28 | `86` |  |
| `scorers[].team.name` | str | 100 % | 0 % | 28 | `Real Madrid CF` |  |
| `scorers[].team.shortName` | str | 100 % | 0 % | 28 | `Real Madrid` |  |
| `scorers[].team.tla` | str | 100 % | 0 % | 28 | `RMA` |  |
| `scorers[].team.crest` | str | 100 % | 0 % | 28 | `https://crests.football-data.org/86.png` |  |
| `scorers[].team.address` | str | 100 % | 0 % | 28 | `Avenida Concha Espina, 1 Madrid 28036` |  |
| `scorers[].team.website` | str | 100 % | 0 % | 28 | `http://www.realmadrid.com` |  |
| `scorers[].team.founded` | int | 100 % | 0 % | 24 | `1902` |  |
| `scorers[].team.clubColors` | str | 100 % | 0 % | 19 | `White / Purple` |  |
| `scorers[].team.venue` | str | 100 % | 0 % | 28 | `Estadio Santiago Bernabéu` |  |
| `scorers[].team.lastUpdated` | str | 100 % | 0 % | 28 | `2022-02-19T08:59:31Z` |  |
| `scorers[].playedMatches` | int | 100 % | 0 % | 10 | `34` |  |
| `scorers[].goals` | int | 100 % | 0 % | 17 | `31` |  |
| `scorers[].assists` | int, null | 100 % | 5 % | 12 | `3` |  |
| `scorers[].penalties` | int, null | 100 % | 28 % | 9 | `7` |  |

## `standings`

- Archivos: 2 (PD_2024, PL_2024) · 0.0 MB
- Registros perfilados: 2

| Campo | Tipos | Presencia | Nulos | Distintos | Ejemplo | ¿Clave? |
|---|---|---|---|---|---|---|
| `filters` | object | 100 % | 0 % | — |  |  |
| `filters.season` | str | 100 % | 0 % | 1 | `2024` |  |
| `area` | object | 100 % | 0 % | — |  |  |
| `area.id` | int | 100 % | 0 % | 2 | `2224` |  |
| `area.name` | str | 100 % | 0 % | 2 | `Spain` |  |
| `area.code` | str | 100 % | 0 % | 2 | `ESP` |  |
| `area.flag` | str | 100 % | 0 % | 2 | `https://crests.football-data.org/760.svg` |  |
| `competition` | object | 100 % | 0 % | — |  |  |
| `competition.id` | int | 100 % | 0 % | 2 | `2014` |  |
| `competition.name` | str | 100 % | 0 % | 2 | `Primera Division` |  |
| `competition.code` | str | 100 % | 0 % | 2 | `PD` |  |
| `competition.type` | str | 100 % | 0 % | 1 | `LEAGUE` |  |
| `competition.emblem` | str | 100 % | 0 % | 2 | `https://crests.football-data.org/laliga…` |  |
| `season` | object | 100 % | 0 % | — |  |  |
| `season.id` | int | 100 % | 0 % | 2 | `2292` |  |
| `season.startDate` | str | 100 % | 0 % | 2 | `2024-08-18` |  |
| `season.endDate` | str | 100 % | 0 % | 1 | `2025-05-25` |  |
| `season.currentMatchday` | int | 100 % | 0 % | 1 | `38` |  |
| `season.winner` | null | 100 % | 100 % | 0 |  |  |
| `standings` | array | 100 % | 0 % | — |  |  |
| `standings[]` | object | — | 0 % | — |  |  |
| `standings[].stage` | str | 100 % | 0 % | 1 | `REGULAR_SEASON` |  |
| `standings[].type` | str | 100 % | 0 % | 3 | `TOTAL` |  |
| `standings[].group` | null | 100 % | 100 % | 0 |  |  |
| `standings[].table` | array | 100 % | 0 % | — |  |  |
| `standings[].table[]` | object | — | 0 % | — |  |  |
| `standings[].table[].position` | int | 100 % | 0 % | 20 | `1` |  |
| `standings[].table[].team` | object | 100 % | 0 % | — |  |  |
| `standings[].table[].team.id` | int | 100 % | 0 % | 40 | `81` |  |
| `standings[].table[].team.name` | str | 100 % | 0 % | 40 | `FC Barcelona` |  |
| `standings[].table[].team.shortName` | str | 100 % | 0 % | 40 | `Barça` |  |
| `standings[].table[].team.tla` | str | 100 % | 0 % | 40 | `FCB` |  |
| `standings[].table[].team.crest` | str | 100 % | 0 % | 40 | `https://crests.football-data.org/81.png` |  |
| `standings[].table[].playedGames` | int | 100 % | 0 % | 2 | `38` |  |
| `standings[].table[].form` | str | 100 % | 0 % | 38 | `W,L,W,W,W` |  |
| `standings[].table[].won` | int | 100 % | 0 % | 23 | `28` |  |
| `standings[].table[].draw` | int | 100 % | 0 % | 17 | `4` |  |
| `standings[].table[].lost` | int | 100 % | 0 % | 24 | `6` |  |
| `standings[].table[].points` | int | 100 % | 0 % | 54 | `88` |  |
| `standings[].table[].goalsFor` | int | 100 % | 0 % | 50 | `102` |  |
| `standings[].table[].goalsAgainst` | int | 100 % | 0 % | 51 | `39` |  |
| `standings[].table[].goalDifference` | int | 100 % | 0 % | 58 | `63` |  |

## `team`

- Archivos: 2 (64, 86) · 0.0 MB
- Registros perfilados: 2

| Campo | Tipos | Presencia | Nulos | Distintos | Ejemplo | ¿Clave? |
|---|---|---|---|---|---|---|
| `area` | object | 100 % | 0 % | — |  |  |
| `area.id` | int | 100 % | 0 % | 2 | `2072` |  |
| `area.name` | str | 100 % | 0 % | 2 | `England` |  |
| `area.code` | str | 100 % | 0 % | 2 | `ENG` |  |
| `area.flag` | str | 100 % | 0 % | 2 | `https://crests.football-data.org/770.svg` |  |
| `id` | int | 100 % | 0 % | 2 | `64` |  |
| `name` | str | 100 % | 0 % | 2 | `Liverpool FC` |  |
| `shortName` | str | 100 % | 0 % | 2 | `Liverpool` |  |
| `tla` | str | 100 % | 0 % | 2 | `LIV` |  |
| `crest` | str | 100 % | 0 % | 2 | `https://crests.football-data.org/64.png` |  |
| `address` | str | 100 % | 0 % | 2 | `Anfield Road Liverpool L4 0TH` |  |
| `website` | str | 100 % | 0 % | 2 | `http://www.liverpoolfc.tv` |  |
| `founded` | int | 100 % | 0 % | 2 | `1892` |  |
| `clubColors` | str | 100 % | 0 % | 2 | `Red / White` |  |
| `venue` | str | 100 % | 0 % | 2 | `Anfield` |  |
| `runningCompetitions` | array | 100 % | 0 % | — |  |  |
| `runningCompetitions[]` | object | — | 0 % | — |  |  |
| `runningCompetitions[].id` | int | 100 % | 0 % | 4 | `2021` |  |
| `runningCompetitions[].name` | str | 100 % | 0 % | 4 | `Premier League` |  |
| `runningCompetitions[].code` | str | 100 % | 0 % | 4 | `PL` |  |
| `runningCompetitions[].type` | str | 100 % | 0 % | 2 | `LEAGUE` |  |
| `runningCompetitions[].emblem` | str | 100 % | 0 % | 4 | `https://crests.football-data.org/PL.png` |  |
| `coach` | object | 100 % | 0 % | — |  |  |
| `coach.id` | int, null | 100 % | 50 % | 1 | `11613` |  |
| `coach.firstName` | null, str | 100 % | 50 % | 1 | `""` |  |
| `coach.lastName` | null, str | 100 % | 50 % | 1 | `José Mourinho` |  |
| `coach.name` | null, str | 100 % | 50 % | 1 | `José Mourinho` |  |
| `coach.dateOfBirth` | null, str | 100 % | 50 % | 1 | `1963-01-26` |  |
| `coach.nationality` | null, str | 100 % | 50 % | 1 | `Portugal` |  |
| `coach.contract` | object | 100 % | 0 % | — |  |  |
| `coach.contract.start` | null | 100 % | 100 % | 0 |  |  |
| `coach.contract.until` | null | 100 % | 100 % | 0 |  |  |
| `squad` | array | 100 % | 0 % | — |  |  |
| `squad[]` | object | — | 0 % | — |  |  |
| `squad[].id` | int | 100 % | 0 % | 54 | `1795` | ✔ |
| `squad[].name` | str | 100 % | 0 % | 54 | `Alisson Becker` | ✔ |
| `squad[].position` | str | 100 % | 0 % | 4 | `Goalkeeper` |  |
| `squad[].dateOfBirth` | str | 100 % | 0 % | 53 | `1992-10-02` |  |
| `squad[].nationality` | str | 100 % | 0 % | 22 | `Brazil` |  |
| `staff` | array | 100 % | 0 % | — |  |  |
| `lastUpdated` | str | 100 % | 0 % | 2 | `2022-02-10T19:30:22Z` |  |

## `teams`

- Archivos: 5 (EC_2024, PD_2024, PD_2026, PL_2024, PL_2026) · 0.4 MB
- Registros perfilados: 5

| Campo | Tipos | Presencia | Nulos | Distintos | Ejemplo | ¿Clave? |
|---|---|---|---|---|---|---|
| `count` | int | 100 % | 0 % | 2 | `24` |  |
| `filters` | object | 100 % | 0 % | — |  |  |
| `filters.season` | int | 100 % | 0 % | 2 | `2024` |  |
| `competition` | object | 100 % | 0 % | — |  |  |
| `competition.id` | int | 100 % | 0 % | 3 | `2018` |  |
| `competition.name` | str | 100 % | 0 % | 3 | `European Championship` |  |
| `competition.code` | str | 100 % | 0 % | 3 | `EC` |  |
| `competition.type` | str | 100 % | 0 % | 2 | `CUP` |  |
| `competition.emblem` | str | 100 % | 0 % | 3 | `https://crests.football-data.org/ec.png` |  |
| `season` | object | 100 % | 0 % | — |  |  |
| `season.id` | int | 100 % | 0 % | 5 | `1537` |  |
| `season.startDate` | str | 100 % | 0 % | 5 | `2024-06-14` |  |
| `season.endDate` | str | 100 % | 0 % | 3 | `2024-07-14` |  |
| `season.currentMatchday` | int | 100 % | 0 % | 4 | `7` |  |
| `season.winner` | null, object | 100 % | 80 % | — |  |  |
| `season.winner.id` | int | 100 % | 0 % | 1 | `760` |  |
| `season.winner.name` | str | 100 % | 0 % | 1 | `Spain` |  |
| `season.winner.shortName` | str | 100 % | 0 % | 1 | `Spain` |  |
| `season.winner.tla` | str | 100 % | 0 % | 1 | `ESP` |  |
| `season.winner.crest` | str | 100 % | 0 % | 1 | `https://crests.football-data.org/760.svg` |  |
| `season.winner.address` | str | 100 % | 0 % | 1 | `Ramón y Cajal, s/n Las Rozas 28230` |  |
| `season.winner.website` | str | 100 % | 0 % | 1 | `http://www.rfef.es` |  |
| `season.winner.founded` | int | 100 % | 0 % | 1 | `1909` |  |
| `season.winner.clubColors` | str | 100 % | 0 % | 1 | `Red / Blue / Yellow` |  |
| `season.winner.venue` | null | 100 % | 100 % | 0 |  |  |
| `season.winner.lastUpdated` | str | 100 % | 0 % | 1 | `2026-06-01T09:41:19Z` |  |
| `teams` | array | 100 % | 0 % | — |  |  |
| `teams[]` | object | — | 0 % | — |  |  |
| `teams[].area` | object | 100 % | 0 % | — |  |  |
| `teams[].area.id` | int | 100 % | 0 % | 24 | `2088` |  |
| `teams[].area.name` | str | 100 % | 0 % | 24 | `Germany` |  |
| `teams[].area.code` | str | 100 % | 0 % | 24 | `DEU` |  |
| `teams[].area.flag` | null, str | 100 % | 3 % | 21 | `https://crests.football-data.org/759.svg` |  |
| `teams[].id` | int | 100 % | 0 % | 73 | `759` |  |
| `teams[].name` | str | 100 % | 0 % | 73 | `Germany` |  |
| `teams[].shortName` | str | 100 % | 0 % | 73 | `Germany` |  |
| `teams[].tla` | str | 100 % | 0 % | 71 | `GER` |  |
| `teams[].crest` | str | 100 % | 0 % | 73 | `https://crests.football-data.org/759.svg` |  |
| `teams[].address` | str | 100 % | 0 % | 73 | `Otto-Fleck-Schneise 6 / Postfach 710265…` |  |
| `teams[].website` | str | 100 % | 0 % | 73 | `http://www.dfb.de` |  |
| `teams[].founded` | int | 100 % | 0 % | 47 | `1900` |  |
| `teams[].clubColors` | str | 100 % | 0 % | 35 | `White / Black` |  |
| `teams[].venue` | null, str | 100 % | 12 % | 60 | `City Arena Trnava` |  |
| `teams[].runningCompetitions` | array | 100 % | 0 % | — |  |  |
| `teams[].runningCompetitions[]` | object | — | 0 % | — |  |  |
| `teams[].runningCompetitions[].id` | int | 100 % | 0 % | 10 | `2182` |  |
| `teams[].runningCompetitions[].name` | str | 100 % | 0 % | 10 | `UEFA Nations League` |  |
| `teams[].runningCompetitions[].code` | str | 100 % | 0 % | 10 | `UNL` |  |
| `teams[].runningCompetitions[].type` | str | 100 % | 0 % | 2 | `CUP` |  |
| `teams[].runningCompetitions[].emblem` | null, str | 100 % | 14 % | 9 | `https://crests.football-data.org/laliga…` |  |
| `teams[].coach` | object | 100 % | 0 % | — |  |  |
| `teams[].coach.id` | int, null | 100 % | 58 % | 29 | `111241` |  |
| `teams[].coach.firstName` | null, str | 100 % | 60 % | 13 | `Edin` |  |
| `teams[].coach.lastName` | null, str | 100 % | 60 % | 27 | `Terzić` |  |
| `teams[].coach.name` | null, str | 100 % | 58 % | 29 | `Edin Terzić` |  |
| `teams[].coach.dateOfBirth` | null, str | 100 % | 58 % | 29 | `1982-10-30` |  |
| `teams[].coach.nationality` | null, str | 100 % | 58 % | 7 | `Germany` |  |
| `teams[].coach.contract` | object | 100 % | 0 % | — |  |  |
| `teams[].coach.contract.start` | null | 100 % | 100 % | 0 |  |  |
| `teams[].coach.contract.until` | null | 100 % | 100 % | 0 |  |  |
| `teams[].squad` | array | 100 % | 0 % | — |  |  |
| `teams[].squad[]` | object | — | 0 % | — |  |  |
| `teams[].squad[].id` | int | 100 % | 0 % | 2278 | `316` |  |
| `teams[].squad[].name` | str | 100 % | 0 % | 2264 | `Oliver Baumann` |  |
| `teams[].squad[].position` | null, str | 100 % | <1 % | 13 | `Goalkeeper` |  |
| `teams[].squad[].dateOfBirth` | null, str | 100 % | <1 % | 1893 | `1990-06-02` |  |
| `teams[].squad[].nationality` | str | 100 % | 0 % | 95 | `Germany` |  |
| `teams[].staff` | array | 100 % | 0 % | — |  |  |
| `teams[].lastUpdated` | str | 100 % | 0 % | 73 | `2026-06-01T09:41:12Z` |  |
