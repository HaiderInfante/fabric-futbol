# Perfil de muestras: API-Football

> Generado por `scripts/explore/profile_samples.py` a partir de `data/samples/`. Se regenera en cada ejecución: no editar a mano. La interpretación de negocio está en `docs/diccionario_datos.md`.

Leyenda: *Presencia* = % de objetos padre que tienen el campo (— en elementos de lista); *Distintos* = valores no nulos distintos; *¿Clave?* = único, sin nulos y presente en el 100 % de los casos dentro de la muestra.

## `fixture_events`

- Archivos: 1 (1208021) · 0.0 MB
- Registros perfilados: 16

| Campo | Tipos | Presencia | Nulos | Distintos | Ejemplo | ¿Clave? |
|---|---|---|---|---|---|---|
| `time` | object | 100 % | 0 % | — |  |  |
| `time.elapsed` | int | 100 % | 0 % | 12 | `18` |  |
| `time.extra` | int, null | 100 % | 88 % | 1 | `1` |  |
| `team` | object | 100 % | 0 % | — |  |  |
| `team.id` | int | 100 % | 0 % | 2 | `33` |  |
| `team.name` | str | 100 % | 0 % | 2 | `Manchester United` |  |
| `team.logo` | str | 100 % | 0 % | 2 | `https://media.api-sports.io/football/te…` |  |
| `player` | object | 100 % | 0 % | — |  |  |
| `player.id` | int | 100 % | 0 % | 13 | `19220` |  |
| `player.name` | str | 100 % | 0 % | 15 | `Mason Mount` |  |
| `assist` | object | 100 % | 0 % | — |  |  |
| `assist.id` | int, null | 100 % | 31 % | 10 | `284324` |  |
| `assist.name` | null, str | 100 % | 31 % | 10 | `A. Garnacho` |  |
| `type` | str | 100 % | 0 % | 3 | `Card` |  |
| `detail` | str | 100 % | 0 % | 7 | `Yellow Card` |  |
| `comments` | null, str | 100 % | 69 % | 3 | `Foul` |  |

## `fixture_lineups`

- Archivos: 1 (1208021) · 0.0 MB
- Registros perfilados: 2

| Campo | Tipos | Presencia | Nulos | Distintos | Ejemplo | ¿Clave? |
|---|---|---|---|---|---|---|
| `team` | object | 100 % | 0 % | — |  |  |
| `team.id` | int | 100 % | 0 % | 2 | `33` |  |
| `team.name` | str | 100 % | 0 % | 2 | `Manchester United` |  |
| `team.logo` | str | 100 % | 0 % | 2 | `https://media.api-sports.io/football/te…` |  |
| `team.colors` | object | 100 % | 0 % | — |  |  |
| `team.colors.player` | object | 100 % | 0 % | — |  |  |
| `team.colors.player.primary` | str | 100 % | 0 % | 2 | `ea0000` |  |
| `team.colors.player.number` | str | 100 % | 0 % | 2 | `ffffff` |  |
| `team.colors.player.border` | str | 100 % | 0 % | 2 | `ea0000` |  |
| `team.colors.goalkeeper` | object | 100 % | 0 % | — |  |  |
| `team.colors.goalkeeper.primary` | str | 100 % | 0 % | 2 | `000000` |  |
| `team.colors.goalkeeper.number` | str | 100 % | 0 % | 1 | `ffffff` |  |
| `team.colors.goalkeeper.border` | str | 100 % | 0 % | 2 | `000000` |  |
| `coach` | object | 100 % | 0 % | — |  |  |
| `coach.id` | int | 100 % | 0 % | 2 | `1993` |  |
| `coach.name` | str | 100 % | 0 % | 2 | `E. ten Hag` |  |
| `coach.photo` | str | 100 % | 0 % | 2 | `https://media.api-sports.io/football/co…` |  |
| `formation` | str | 100 % | 0 % | 1 | `4-2-3-1` |  |
| `startXI` | array | 100 % | 0 % | — |  |  |
| `startXI[]` | object | — | 0 % | — |  |  |
| `startXI[].player` | object | 100 % | 0 % | — |  |  |
| `startXI[].player.id` | int | 100 % | 0 % | 22 | `526` | ✔ |
| `startXI[].player.name` | str | 100 % | 0 % | 22 | `A. Onana` | ✔ |
| `startXI[].player.number` | int | 100 % | 0 % | 19 | `24` |  |
| `startXI[].player.pos` | str | 100 % | 0 % | 4 | `G` |  |
| `startXI[].player.grid` | str | 100 % | 0 % | 11 | `1:1` |  |
| `substitutes` | array | 100 % | 0 % | — |  |  |
| `substitutes[]` | object | — | 0 % | — |  |  |
| `substitutes[].player` | object | 100 % | 0 % | — |  |  |
| `substitutes[].player.id` | int | 100 % | 0 % | 18 | `284324` | ✔ |
| `substitutes[].player.name` | str | 100 % | 0 % | 18 | `A. Garnacho` | ✔ |
| `substitutes[].player.number` | int | 100 % | 0 % | 17 | `17` |  |
| `substitutes[].player.pos` | str | 100 % | 0 % | 4 | `F` |  |
| `substitutes[].player.grid` | null | 100 % | 100 % | 0 |  |  |

## `fixture_players`

- Archivos: 1 (1208021) · 0.0 MB
- Registros perfilados: 2

| Campo | Tipos | Presencia | Nulos | Distintos | Ejemplo | ¿Clave? |
|---|---|---|---|---|---|---|
| `team` | object | 100 % | 0 % | — |  |  |
| `team.id` | int | 100 % | 0 % | 2 | `33` |  |
| `team.name` | str | 100 % | 0 % | 2 | `Manchester United` |  |
| `team.logo` | str | 100 % | 0 % | 2 | `https://media.api-sports.io/football/te…` |  |
| `team.update` | str | 100 % | 0 % | 1 | `2025-06-06T09:04:06+00:00` |  |
| `players` | array | 100 % | 0 % | — |  |  |
| `players[]` | object | — | 0 % | — |  |  |
| `players[].player` | object | 100 % | 0 % | — |  |  |
| `players[].player.id` | int | 100 % | 0 % | 40 | `526` | ✔ |
| `players[].player.name` | str | 100 % | 0 % | 40 | `André Onana` | ✔ |
| `players[].player.photo` | str | 100 % | 0 % | 40 | `https://media.api-sports.io/football/pl…` | ✔ |
| `players[].statistics` | array | 100 % | 0 % | — |  |  |
| `players[].statistics[]` | object | — | 0 % | — |  |  |
| `players[].statistics[].games` | object | 100 % | 0 % | — |  |  |
| `players[].statistics[].games.minutes` | int, null | 100 % | 20 % | 13 | `90` |  |
| `players[].statistics[].games.number` | int | 100 % | 0 % | 28 | `24` |  |
| `players[].statistics[].games.position` | str | 100 % | 0 % | 4 | `G` |  |
| `players[].statistics[].games.rating` | null, str | 100 % | 25 % | 11 | `7.2` |  |
| `players[].statistics[].games.captain` | bool | 100 % | 0 % | 2 | `False` |  |
| `players[].statistics[].games.substitute` | bool | 100 % | 0 % | 2 | `False` |  |
| `players[].statistics[].offsides` | int, null | 100 % | 92 % | 2 | `2` |  |
| `players[].statistics[].shots` | object | 100 % | 0 % | — |  |  |
| `players[].statistics[].shots.total` | int, null | 100 % | 72 % | 4 | `3` |  |
| `players[].statistics[].shots.on` | int, null | 100 % | 88 % | 2 | `1` |  |
| `players[].statistics[].goals` | object | 100 % | 0 % | — |  |  |
| `players[].statistics[].goals.total` | int, null | 100 % | 98 % | 1 | `1` |  |
| `players[].statistics[].goals.conceded` | int | 100 % | 0 % | 2 | `0` |  |
| `players[].statistics[].goals.assists` | int, null | 100 % | 20 % | 2 | `0` |  |
| `players[].statistics[].goals.saves` | int, null | 100 % | 95 % | 2 | `2` |  |
| `players[].statistics[].passes` | object | 100 % | 0 % | — |  |  |
| `players[].statistics[].passes.total` | int, null | 100 % | 22 % | 27 | `23` |  |
| `players[].statistics[].passes.key` | int, null | 100 % | 78 % | 4 | `1` |  |
| `players[].statistics[].passes.accuracy` | null, str | 100 % | 22 % | 27 | `16` |  |
| `players[].statistics[].tackles` | object | 100 % | 0 % | — |  |  |
| `players[].statistics[].tackles.total` | int, null | 100 % | 55 % | 5 | `2` |  |
| `players[].statistics[].tackles.blocks` | int, null | 100 % | 88 % | 1 | `1` |  |
| `players[].statistics[].tackles.interceptions` | int, null | 100 % | 68 % | 4 | `3` |  |
| `players[].statistics[].duels` | object | 100 % | 0 % | — |  |  |
| `players[].statistics[].duels.total` | int, null | 100 % | 25 % | 16 | `7` |  |
| `players[].statistics[].duels.won` | int, null | 100 % | 30 % | 9 | `6` |  |
| `players[].statistics[].dribbles` | object | 100 % | 0 % | — |  |  |
| `players[].statistics[].dribbles.attempts` | int, null | 100 % | 62 % | 5 | `2` |  |
| `players[].statistics[].dribbles.success` | int, null | 100 % | 78 % | 3 | `1` |  |
| `players[].statistics[].dribbles.past` | int, null | 100 % | 75 % | 2 | `2` |  |
| `players[].statistics[].fouls` | object | 100 % | 0 % | — |  |  |
| `players[].statistics[].fouls.drawn` | int, null | 100 % | 62 % | 4 | `1` |  |
| `players[].statistics[].fouls.committed` | int, null | 100 % | 65 % | 3 | `2` |  |
| `players[].statistics[].cards` | object | 100 % | 0 % | — |  |  |
| `players[].statistics[].cards.yellow` | int | 100 % | 0 % | 2 | `0` |  |
| `players[].statistics[].cards.red` | int | 100 % | 0 % | 1 | `0` |  |
| `players[].statistics[].penalty` | object | 100 % | 0 % | — |  |  |
| `players[].statistics[].penalty.won` | null | 100 % | 100 % | 0 |  |  |
| `players[].statistics[].penalty.commited` | null | 100 % | 100 % | 0 |  |  |
| `players[].statistics[].penalty.scored` | int | 100 % | 0 % | 1 | `0` |  |
| `players[].statistics[].penalty.missed` | int | 100 % | 0 % | 1 | `0` |  |
| `players[].statistics[].penalty.saved` | int, null | 100 % | 95 % | 1 | `0` |  |

## `fixture_statistics`

- Archivos: 1 (1208021) · 0.0 MB
- Registros perfilados: 2

| Campo | Tipos | Presencia | Nulos | Distintos | Ejemplo | ¿Clave? |
|---|---|---|---|---|---|---|
| `team` | object | 100 % | 0 % | — |  |  |
| `team.id` | int | 100 % | 0 % | 2 | `33` |  |
| `team.name` | str | 100 % | 0 % | 2 | `Manchester United` |  |
| `team.logo` | str | 100 % | 0 % | 2 | `https://media.api-sports.io/football/te…` |  |
| `statistics` | array | 100 % | 0 % | — |  |  |
| `statistics[]` | object | — | 0 % | — |  |  |
| `statistics[].type` | str | 100 % | 0 % | 18 | `Shots on Goal` |  |
| `statistics[].value` | int, null, str | 100 % | 6 % | 22 | `5` |  |

## `fixtures`

- Archivos: 3 (140_2024, 39_2024, 4_2024) · 0.8 MB
- Registros perfilados: 811

| Campo | Tipos | Presencia | Nulos | Distintos | Ejemplo | ¿Clave? |
|---|---|---|---|---|---|---|
| `fixture` | object | 100 % | 0 % | — |  |  |
| `fixture.id` | int | 100 % | 0 % | 811 | `1208494` | ✔ |
| `fixture.referee` | str | 100 % | 0 % | 60 | `Alejandro Muñiz` |  |
| `fixture.timezone` | str | 100 % | 0 % | 1 | `UTC` |  |
| `fixture.date` | str | 100 % | 0 % | 563 | `2024-08-15T17:00:00+00:00` |  |
| `fixture.timestamp` | int | 100 % | 0 % | 563 | `1723741200` |  |
| `fixture.periods` | object | 100 % | 0 % | — |  |  |
| `fixture.periods.first` | int | 100 % | 0 % | 563 | `1723741200` |  |
| `fixture.periods.second` | int | 100 % | 0 % | 563 | `1723744800` |  |
| `fixture.venue` | object | 100 % | 0 % | — |  |  |
| `fixture.venue.id` | int | 100 % | 0 % | 58 | `1460` |  |
| `fixture.venue.name` | str | 100 % | 0 % | 58 | `San Mamés Barria` |  |
| `fixture.venue.city` | str | 100 % | 0 % | 40 | `Bilbao` |  |
| `fixture.status` | object | 100 % | 0 % | — |  |  |
| `fixture.status.long` | str | 100 % | 0 % | 1 | `Match Finished` |  |
| `fixture.status.short` | str | 100 % | 0 % | 3 | `FT` |  |
| `fixture.status.elapsed` | int | 100 % | 0 % | 2 | `90` |  |
| `fixture.status.extra` | int, null | 100 % | 20 % | 15 | `5` |  |
| `league` | object | 100 % | 0 % | — |  |  |
| `league.id` | int | 100 % | 0 % | 3 | `140` |  |
| `league.name` | str | 100 % | 0 % | 3 | `La Liga` |  |
| `league.country` | str | 100 % | 0 % | 3 | `Spain` |  |
| `league.logo` | str | 100 % | 0 % | 3 | `https://media.api-sports.io/football/le…` |  |
| `league.flag` | null, str | 100 % | 6 % | 2 | `https://media.api-sports.io/flags/es.svg` |  |
| `league.season` | int | 100 % | 0 % | 1 | `2024` |  |
| `league.round` | str | 100 % | 0 % | 60 | `Regular Season - 1` |  |
| `league.standings` | bool | 100 % | 0 % | 1 | `True` |  |
| `teams` | object | 100 % | 0 % | — |  |  |
| `teams.home` | object | 100 % | 0 % | — |  |  |
| `teams.home.id` | int | 100 % | 0 % | 64 | `531` |  |
| `teams.home.name` | str | 100 % | 0 % | 64 | `Athletic Club` |  |
| `teams.home.logo` | str | 100 % | 0 % | 64 | `https://media.api-sports.io/football/te…` |  |
| `teams.home.winner` | bool, null | 100 % | 25 % | 2 | `True` |  |
| `teams.away` | object | 100 % | 0 % | — |  |  |
| `teams.away.id` | int | 100 % | 0 % | 64 | `546` |  |
| `teams.away.name` | str | 100 % | 0 % | 64 | `Getafe` |  |
| `teams.away.logo` | str | 100 % | 0 % | 64 | `https://media.api-sports.io/football/te…` |  |
| `teams.away.winner` | bool, null | 100 % | 25 % | 2 | `False` |  |
| `goals` | object | 100 % | 0 % | — |  |  |
| `goals.home` | int | 100 % | 0 % | 7 | `1` |  |
| `goals.away` | int | 100 % | 0 % | 7 | `1` |  |
| `score` | object | 100 % | 0 % | — |  |  |
| `score.halftime` | object | 100 % | 0 % | — |  |  |
| `score.halftime.home` | int | 100 % | 0 % | 6 | `1` |  |
| `score.halftime.away` | int | 100 % | 0 % | 5 | `0` |  |
| `score.fulltime` | object | 100 % | 0 % | — |  |  |
| `score.fulltime.home` | int | 100 % | 0 % | 7 | `1` |  |
| `score.fulltime.away` | int | 100 % | 0 % | 7 | `1` |  |
| `score.extratime` | object | 100 % | 0 % | — |  |  |
| `score.extratime.home` | int, null | 100 % | >99 % | 2 | `1` |  |
| `score.extratime.away` | int, null | 100 % | >99 % | 1 | `0` |  |
| `score.penalty` | object | 100 % | 0 % | — |  |  |
| `score.penalty.home` | int, null | 100 % | >99 % | 2 | `3` |  |
| `score.penalty.away` | int, null | 100 % | >99 % | 3 | `0` |  |

## `injuries`

- Archivos: 1 (39_2024) · 1.8 MB
- Registros perfilados: 3168

| Campo | Tipos | Presencia | Nulos | Distintos | Ejemplo | ¿Clave? |
|---|---|---|---|---|---|---|
| `player` | object | 100 % | 0 % | — |  |  |
| `player.id` | int | 100 % | 0 % | 403 | `153434` |  |
| `player.name` | str | 100 % | 0 % | 402 | `W. Fish` |  |
| `player.photo` | str | 100 % | 0 % | 403 | `https://media.api-sports.io/football/pl…` |  |
| `player.type` | str | 100 % | 0 % | 2 | `Missing Fixture` |  |
| `player.reason` | str | 100 % | 0 % | 41 | `Ankle Injury` |  |
| `team` | object | 100 % | 0 % | — |  |  |
| `team.id` | int | 100 % | 0 % | 20 | `33` |  |
| `team.name` | str | 100 % | 0 % | 20 | `Manchester United` |  |
| `team.logo` | str | 100 % | 0 % | 20 | `https://media.api-sports.io/football/te…` |  |
| `fixture` | object | 100 % | 0 % | — |  |  |
| `fixture.id` | int | 100 % | 0 % | 371 | `1208021` |  |
| `fixture.timezone` | str | 100 % | 0 % | 1 | `UTC` |  |
| `fixture.date` | str | 100 % | 0 % | 211 | `2024-08-16T19:00:00+00:00` |  |
| `fixture.timestamp` | int | 100 % | 0 % | 211 | `1723834800` |  |
| `league` | object | 100 % | 0 % | — |  |  |
| `league.id` | int | 100 % | 0 % | 1 | `39` |  |
| `league.season` | int | 100 % | 0 % | 1 | `2024` |  |
| `league.name` | str | 100 % | 0 % | 1 | `Premier League` |  |
| `league.country` | str | 100 % | 0 % | 1 | `England` |  |
| `league.logo` | str | 100 % | 0 % | 1 | `https://media.api-sports.io/football/le…` |  |
| `league.flag` | str | 100 % | 0 % | 1 | `https://media.api-sports.io/flags/gb-en…` |  |

## `players`

- Archivos: 4 (140_2024_p1, 39_2024_p1, 39_2024_p2, 4_2024_p1) · 0.1 MB
- Registros perfilados: 80

| Campo | Tipos | Presencia | Nulos | Distintos | Ejemplo | ¿Clave? |
|---|---|---|---|---|---|---|
| `player` | object | 100 % | 0 % | — |  |  |
| `player.id` | int | 100 % | 0 % | 67 | `15` |  |
| `player.name` | str | 100 % | 0 % | 67 | `T. Delaney` |  |
| `player.firstname` | str | 100 % | 0 % | 63 | `Thomas Joseph` |  |
| `player.lastname` | str | 100 % | 0 % | 67 | `Delaney` |  |
| `player.age` | int | 100 % | 0 % | 18 | `34` |  |
| `player.birth` | object | 100 % | 0 % | — |  |  |
| `player.birth.date` | str | 100 % | 0 % | 67 | `1991-09-03` |  |
| `player.birth.place` | null, str | 100 % | 1 % | 54 | `Frederiksberg` |  |
| `player.birth.country` | str | 100 % | 0 % | 26 | `Denmark` |  |
| `player.nationality` | str | 100 % | 0 % | 25 | `Denmark` |  |
| `player.height` | str | 100 % | 0 % | 27 | `182` |  |
| `player.weight` | str | 100 % | 0 % | 32 | `79` |  |
| `player.injured` | bool | 100 % | 0 % | 1 | `False` |  |
| `player.photo` | str | 100 % | 0 % | 67 | `https://media.api-sports.io/football/pl…` |  |
| `statistics` | array | 100 % | 0 % | — |  |  |
| `statistics[]` | object | — | 0 % | — |  |  |
| `statistics[].team` | object | 100 % | 0 % | — |  |  |
| `statistics[].team.id` | int | 100 % | 0 % | 36 | `536` |  |
| `statistics[].team.name` | str | 100 % | 0 % | 36 | `Sevilla` |  |
| `statistics[].team.logo` | str | 100 % | 0 % | 36 | `https://media.api-sports.io/football/te…` |  |
| `statistics[].league` | object | 100 % | 0 % | — |  |  |
| `statistics[].league.id` | int | 100 % | 0 % | 3 | `140` |  |
| `statistics[].league.name` | str | 100 % | 0 % | 3 | `La Liga` |  |
| `statistics[].league.country` | str | 100 % | 0 % | 3 | `Spain` |  |
| `statistics[].league.logo` | str | 100 % | 0 % | 3 | `https://media.api-sports.io/football/le…` |  |
| `statistics[].league.flag` | null, str | 100 % | 24 % | 2 | `https://media.api-sports.io/flags/es.svg` |  |
| `statistics[].league.season` | int | 100 % | 0 % | 1 | `2024` |  |
| `statistics[].games` | object | 100 % | 0 % | — |  |  |
| `statistics[].games.appearences` | int, null | 100 % | 15 % | 27 | `38` |  |
| `statistics[].games.lineups` | int, null | 100 % | 15 % | 31 | `23` |  |
| `statistics[].games.minutes` | int, null | 100 % | 18 % | 56 | `858` |  |
| `statistics[].games.number` | int, null | 100 % | 82 % | 12 | `5` |  |
| `statistics[].games.position` | str | 100 % | 0 % | 5 | `Midfielder` |  |
| `statistics[].games.rating` | null, str | 100 % | 28 % | 53 | `7.038461` |  |
| `statistics[].games.captain` | bool | 100 % | 0 % | 1 | `False` |  |
| `statistics[].substitutes` | object | 100 % | 0 % | — |  |  |
| `statistics[].substitutes.in` | int, null | 100 % | 15 % | 15 | `15` |  |
| `statistics[].substitutes.out` | int, null | 100 % | 47 % | 14 | `0` |  |
| `statistics[].substitutes.bench` | int, null | 100 % | 47 % | 15 | `0` |  |
| `statistics[].shots` | object | 100 % | 0 % | — |  |  |
| `statistics[].shots.total` | int, null | 100 % | 46 % | 22 | `14` |  |
| `statistics[].shots.on` | int, null | 100 % | 55 % | 13 | `10` |  |
| `statistics[].goals` | object | 100 % | 0 % | — |  |  |
| `statistics[].goals.total` | int, null | 100 % | 38 % | 8 | `2` |  |
| `statistics[].goals.conceded` | int, null | 100 % | 25 % | 9 | `0` |  |
| `statistics[].goals.assists` | int, null | 100 % | 26 % | 9 | `1` |  |
| `statistics[].goals.saves` | int, null | 100 % | 91 % | 8 | `86` |  |
| `statistics[].passes` | object | 100 % | 0 % | — |  |  |
| `statistics[].passes.total` | int, null | 100 % | 28 % | 54 | `543` |  |
| `statistics[].passes.key` | int, null | 100 % | 46 % | 19 | `2` |  |
| `statistics[].passes.accuracy` | int, null | 100 % | 81 % | 13 | `46` |  |
| `statistics[].tackles` | object | 100 % | 0 % | — |  |  |
| `statistics[].tackles.total` | int, null | 100 % | 39 % | 29 | `16` |  |
| `statistics[].tackles.blocks` | int, null | 100 % | 58 % | 13 | `8` |  |
| `statistics[].tackles.interceptions` | int, null | 100 % | 47 % | 18 | `11` |  |
| `statistics[].duels` | object | 100 % | 0 % | — |  |  |
| `statistics[].duels.total` | int, null | 100 % | 29 % | 46 | `69` |  |
| `statistics[].duels.won` | int, null | 100 % | 31 % | 39 | `46` |  |
| `statistics[].dribbles` | object | 100 % | 0 % | — |  |  |
| `statistics[].dribbles.attempts` | int, null | 100 % | 44 % | 24 | `2` |  |
| `statistics[].dribbles.success` | int, null | 100 % | 49 % | 18 | `1` |  |
| `statistics[].dribbles.past` | null | 100 % | 100 % | 0 |  |  |
| `statistics[].fouls` | object | 100 % | 0 % | — |  |  |
| `statistics[].fouls.drawn` | int, null | 100 % | 36 % | 18 | `5` |  |
| `statistics[].fouls.committed` | int, null | 100 % | 44 % | 23 | `4` |  |
| `statistics[].cards` | object | 100 % | 0 % | — |  |  |
| `statistics[].cards.yellow` | int, null | 100 % | 15 % | 7 | `1` |  |
| `statistics[].cards.yellowred` | int, null | 100 % | 47 % | 1 | `0` |  |
| `statistics[].cards.red` | int, null | 100 % | 15 % | 2 | `0` |  |
| `statistics[].penalty` | object | 100 % | 0 % | — |  |  |
| `statistics[].penalty.won` | int, null | 100 % | 98 % | 1 | `1` |  |
| `statistics[].penalty.commited` | int, null | 100 % | 99 % | 1 | `1` |  |
| `statistics[].penalty.scored` | int, null | 100 % | 25 % | 2 | `0` |  |
| `statistics[].penalty.missed` | int, null | 100 % | 25 % | 2 | `0` |  |
| `statistics[].penalty.saved` | int, null | 100 % | 89 % | 1 | `0` |  |

## `standings`

- Archivos: 1 (39_2024) · 0.0 MB
- Registros perfilados: 1

| Campo | Tipos | Presencia | Nulos | Distintos | Ejemplo | ¿Clave? |
|---|---|---|---|---|---|---|
| `league` | object | 100 % | 0 % | — |  |  |
| `league.id` | int | 100 % | 0 % | 1 | `39` |  |
| `league.name` | str | 100 % | 0 % | 1 | `Premier League` |  |
| `league.country` | str | 100 % | 0 % | 1 | `England` |  |
| `league.logo` | str | 100 % | 0 % | 1 | `https://media.api-sports.io/football/le…` |  |
| `league.flag` | str | 100 % | 0 % | 1 | `https://media.api-sports.io/flags/gb-en…` |  |
| `league.season` | int | 100 % | 0 % | 1 | `2024` |  |
| `league.standings` | array | 100 % | 0 % | — |  |  |
| `league.standings[]` | array | — | 0 % | — |  |  |
| `league.standings[][]` | object | — | 0 % | — |  |  |
| `league.standings[][].rank` | int | 100 % | 0 % | 20 | `1` | ✔ |
| `league.standings[][].team` | object | 100 % | 0 % | — |  |  |
| `league.standings[][].team.id` | int | 100 % | 0 % | 20 | `40` | ✔ |
| `league.standings[][].team.name` | str | 100 % | 0 % | 20 | `Liverpool` | ✔ |
| `league.standings[][].team.logo` | str | 100 % | 0 % | 20 | `https://media.api-sports.io/football/te…` | ✔ |
| `league.standings[][].points` | int | 100 % | 0 % | 17 | `84` |  |
| `league.standings[][].goalsDiff` | int | 100 % | 0 % | 16 | `45` |  |
| `league.standings[][].group` | str | 100 % | 0 % | 1 | `Premier League` |  |
| `league.standings[][].form` | str | 100 % | 0 % | 19 | `DLDLW` |  |
| `league.standings[][].status` | str | 100 % | 0 % | 1 | `same` |  |
| `league.standings[][].description` | null, str | 100 % | 40 % | 4 | `Champions League` |  |
| `league.standings[][].all` | object | 100 % | 0 % | — |  |  |
| `league.standings[][].all.played` | int | 100 % | 0 % | 1 | `38` |  |
| `league.standings[][].all.win` | int | 100 % | 0 % | 12 | `25` |  |
| `league.standings[][].all.draw` | int | 100 % | 0 % | 10 | `9` |  |
| `league.standings[][].all.lose` | int | 100 % | 0 % | 13 | `4` |  |
| `league.standings[][].all.goals` | object | 100 % | 0 % | — |  |  |
| `league.standings[][].all.goals.for` | int | 100 % | 0 % | 15 | `86` |  |
| `league.standings[][].all.goals.against` | int | 100 % | 0 % | 16 | `41` |  |
| `league.standings[][].home` | object | 100 % | 0 % | — |  |  |
| `league.standings[][].home.played` | int | 100 % | 0 % | 1 | `19` |  |
| `league.standings[][].home.win` | int | 100 % | 0 % | 11 | `14` |  |
| `league.standings[][].home.draw` | int | 100 % | 0 % | 8 | `4` |  |
| `league.standings[][].home.lose` | int | 100 % | 0 % | 11 | `1` |  |
| `league.standings[][].home.goals` | object | 100 % | 0 % | — |  |  |
| `league.standings[][].home.goals.for` | int | 100 % | 0 % | 13 | `42` |  |
| `league.standings[][].home.goals.against` | int | 100 % | 0 % | 13 | `16` |  |
| `league.standings[][].away` | object | 100 % | 0 % | — |  |  |
| `league.standings[][].away.played` | int | 100 % | 0 % | 1 | `19` |  |
| `league.standings[][].away.win` | int | 100 % | 0 % | 11 | `11` |  |
| `league.standings[][].away.draw` | int | 100 % | 0 % | 7 | `5` |  |
| `league.standings[][].away.lose` | int | 100 % | 0 % | 11 | `3` |  |
| `league.standings[][].away.goals` | object | 100 % | 0 % | — |  |  |
| `league.standings[][].away.goals.for` | int | 100 % | 0 % | 16 | `44` |  |
| `league.standings[][].away.goals.against` | int | 100 % | 0 % | 15 | `25` |  |
| `league.standings[][].update` | str | 100 % | 0 % | 1 | `2025-05-26T00:00:00+00:00` |  |

## `teams`

- Archivos: 3 (140_2024, 39_2024, 4_2024) · 0.0 MB
- Registros perfilados: 64

| Campo | Tipos | Presencia | Nulos | Distintos | Ejemplo | ¿Clave? |
|---|---|---|---|---|---|---|
| `team` | object | 100 % | 0 % | — |  |  |
| `team.id` | int | 100 % | 0 % | 64 | `529` | ✔ |
| `team.name` | str | 100 % | 0 % | 64 | `Barcelona` | ✔ |
| `team.code` | str | 100 % | 0 % | 61 | `BAR` |  |
| `team.country` | str | 100 % | 0 % | 24 | `Spain` |  |
| `team.founded` | int, null | 100 % | 2 % | 43 | `1899` |  |
| `team.national` | bool | 100 % | 0 % | 2 | `False` |  |
| `team.logo` | str | 100 % | 0 % | 64 | `https://media.api-sports.io/football/te…` | ✔ |
| `venue` | object | 100 % | 0 % | — |  |  |
| `venue.id` | int | 100 % | 0 % | 63 | `19939` |  |
| `venue.name` | str | 100 % | 0 % | 64 | `Camp Nou` | ✔ |
| `venue.address` | str | 100 % | 0 % | 64 | `Les Corts, 08028` | ✔ |
| `venue.city` | str | 100 % | 0 % | 53 | `Barcelona` |  |
| `venue.capacity` | int | 100 % | 0 % | 64 | `55926` | ✔ |
| `venue.surface` | str | 100 % | 0 % | 1 | `grass` |  |
| `venue.image` | str | 100 % | 0 % | 63 | `https://media.api-sports.io/football/ve…` |  |
