# Perfil de muestras: StatsBomb Open Data

> Generado por `scripts/explore/profile_samples.py` a partir de `data/samples/`. Se regenera en cada ejecución: no editar a mano. La interpretación de negocio está en `docs/diccionario_datos.md`.

Leyenda: *Presencia* = % de objetos padre que tienen el campo (— en elementos de lista); *Distintos* = valores no nulos distintos; *¿Clave?* = único, sin nulos y presente en el 100 % de los casos dentro de la muestra.

## `events`

- Archivos: 6 (3754097, 3754159, 3773457, 3773593, 3930158, 3943043) · 14.6 MB
- Registros perfilados: 22827

| Campo | Tipos | Presencia | Nulos | Distintos | Ejemplo | ¿Clave? |
|---|---|---|---|---|---|---|
| `id` | str | 100 % | 0 % | muchos | `70b5e25c-033c-43f1-adf5-ee871496669b` |  |
| `index` | int | 100 % | 0 % | 4342 | `1` |  |
| `period` | int | 100 % | 0 % | 2 | `1` |  |
| `timestamp` | str | 100 % | 0 % | muchos | `00:00:00.000` |  |
| `minute` | int | 100 % | 0 % | 95 | `0` |  |
| `second` | int | 100 % | 0 % | 60 | `0` |  |
| `type` | object | 100 % | 0 % | — |  |  |
| `type.id` | int | 100 % | 0 % | 30 | `35` |  |
| `type.name` | str | 100 % | 0 % | 30 | `Starting XI` |  |
| `possession` | int | 100 % | 0 % | 202 | `1` |  |
| `possession_team` | object | 100 % | 0 % | — |  |  |
| `possession_team.id` | int | 100 % | 0 % | 10 | `39` |  |
| `possession_team.name` | str | 100 % | 0 % | 10 | `Manchester United` |  |
| `play_pattern` | object | 100 % | 0 % | — |  |  |
| `play_pattern.id` | int | 100 % | 0 % | 9 | `1` |  |
| `play_pattern.name` | str | 100 % | 0 % | 9 | `Regular Play` |  |
| `team` | object | 100 % | 0 % | — |  |  |
| `team.id` | int | 100 % | 0 % | 10 | `39` |  |
| `team.name` | str | 100 % | 0 % | 10 | `Manchester United` |  |
| `duration` | float | 72 % | 0 % | muchos | `0.0` |  |
| `tactics` | object | <1 % | 0 % | — |  |  |
| `tactics.formation` | int | 100 % | 0 % | 8 | `4231` |  |
| `tactics.lineup` | array | 100 % | 0 % | — |  |  |
| `tactics.lineup[]` | object | — | 0 % | — |  |  |
| `tactics.lineup[].player` | object | 100 % | 0 % | — |  |  |
| `tactics.lineup[].player.id` | int | 100 % | 0 % | 137 | `4892` |  |
| `tactics.lineup[].player.name` | str | 100 % | 0 % | 137 | `Sergio Germán Romero` |  |
| `tactics.lineup[].position` | object | 100 % | 0 % | — |  |  |
| `tactics.lineup[].position.id` | int | 100 % | 0 % | 21 | `1` |  |
| `tactics.lineup[].position.name` | str | 100 % | 0 % | 21 | `Goalkeeper` |  |
| `tactics.lineup[].jersey_number` | int | 100 % | 0 % | 33 | `20` |  |
| `related_events` | array | 97 % | 0 % | — |  |  |
| `related_events[]` | str | — | 0 % | muchos | `02309f9c-f8e1-4920-89ba-a9ea9ed84022` |  |
| `player` | object | >99 % | 0 % | — |  |  |
| `player.id` | int | 100 % | 0 % | 156 | `10955` |  |
| `player.name` | str | 100 % | 0 % | 156 | `Harry Kane` |  |
| `position` | object | >99 % | 0 % | — |  |  |
| `position.id` | int | 100 % | 0 % | 21 | `23` |  |
| `position.name` | str | 100 % | 0 % | 21 | `Center Forward` |  |
| `location` | array | >99 % | 0 % | — |  |  |
| `location[]` | float | — | 0 % | 1187 | `61.0` |  |
| `pass` | object | 29 % | 0 % | — |  |  |
| `pass.recipient` | object | 96 % | 0 % | — |  |  |
| `pass.recipient.id` | int | 100 % | 0 % | 155 | `3043` |  |
| `pass.recipient.name` | str | 100 % | 0 % | 155 | `Christian Dannemann Eriksen` |  |
| `pass.length` | float | 100 % | 0 % | 5526 | `1.8027756` |  |
| `pass.angle` | float | 100 % | 0 % | 6069 | `-0.33929262` |  |
| `pass.height` | object | 100 % | 0 % | — |  |  |
| `pass.height.id` | int | 100 % | 0 % | 3 | `1` |  |
| `pass.height.name` | str | 100 % | 0 % | 3 | `Ground Pass` |  |
| `pass.end_location` | array | 100 % | 0 % | — |  |  |
| `pass.end_location[]` | float | — | 0 % | 1175 | `62.7` |  |
| `pass.body_part` | object | 95 % | 0 % | — |  |  |
| `pass.body_part.id` | int | 100 % | 0 % | 7 | `40` |  |
| `pass.body_part.name` | str | 100 % | 0 % | 7 | `Right Foot` |  |
| `pass.type` | object | 15 % | 0 % | — |  |  |
| `pass.type.id` | int | 100 % | 0 % | 7 | `65` |  |
| `pass.type.name` | str | 100 % | 0 % | 7 | `Kick Off` |  |
| `carry` | object | 23 % | 0 % | — |  |  |
| `carry.end_location` | array | 100 % | 0 % | — |  |  |
| `carry.end_location[]` | float | — | 0 % | 1145 | `57.6` |  |
| `pass.switch` | bool | 3 % | 0 % | 1 | `True` |  |
| `pass.outcome` | object | 15 % | 0 % | — |  |  |
| `pass.outcome.id` | int | 100 % | 0 % | 5 | `75` |  |
| `pass.outcome.name` | str | 100 % | 0 % | 5 | `Out` |  |
| `ball_receipt` | object | 3 % | 0 % | — |  |  |
| `ball_receipt.outcome` | object | 100 % | 0 % | — |  |  |
| `ball_receipt.outcome.id` | int | 100 % | 0 % | 1 | `9` |  |
| `ball_receipt.outcome.name` | str | 100 % | 0 % | 1 | `Incomplete` |  |
| `under_pressure` | bool | 18 % | 0 % | 1 | `True` |  |
| `pass.aerial_won` | bool | 1 % | 0 % | 1 | `True` |  |
| `duel` | object | 2 % | 0 % | — |  |  |
| `duel.type` | object | 100 % | 0 % | — |  |  |
| `duel.type.id` | int | 100 % | 0 % | 2 | `10` |  |
| `duel.type.name` | str | 100 % | 0 % | 2 | `Aerial Lost` |  |
| `counterpress` | bool | 3 % | 0 % | 1 | `True` |  |
| `duel.outcome` | object | 61 % | 0 % | — |  |  |
| `duel.outcome.id` | int | 100 % | 0 % | 5 | `16` |  |
| `duel.outcome.name` | str | 100 % | 0 % | 5 | `Success In Play` |  |
| `dribble` | object | <1 % | 0 % | — |  |  |
| `dribble.outcome` | object | 100 % | 0 % | — |  |  |
| `dribble.outcome.id` | int | 100 % | 0 % | 2 | `8` |  |
| `dribble.outcome.name` | str | 100 % | 0 % | 2 | `Complete` |  |
| `off_camera` | bool | 1 % | 0 % | 1 | `True` |  |
| `out` | bool | <1 % | 0 % | 1 | `True` |  |
| `pass.assisted_shot_id` | str | 1 % | 0 % | 97 | `6d085fd9-815d-48d3-b3ae-eeacee6b8378` |  |
| `pass.shot_assist` | bool | 1 % | 0 % | 1 | `True` |  |
| `pass.technique` | object | 1 % | 0 % | — |  |  |
| `pass.technique.id` | int | 100 % | 0 % | 3 | `108` |  |
| `pass.technique.name` | str | 100 % | 0 % | 3 | `Through Ball` |  |
| `pass.through_ball` | bool | <1 % | 0 % | 1 | `True` |  |
| `shot` | object | <1 % | 0 % | — |  |  |
| `shot.statsbomb_xg` | float | 100 % | 0 % | 129 | `0.18283193` |  |
| `shot.end_location` | array | 100 % | 0 % | — |  |  |
| `shot.end_location[]` | float | — | 0 % | 197 | `120.0` |  |
| `shot.key_pass_id` | str | 75 % | 0 % | 97 | `7bdac8ac-655b-4d65-8212-6ba34651f95f` |  |
| `shot.outcome` | object | 100 % | 0 % | — |  |  |
| `shot.outcome.id` | int | 100 % | 0 % | 5 | `98` |  |
| `shot.outcome.name` | str | 100 % | 0 % | 5 | `Off T` |  |
| `shot.technique` | object | 100 % | 0 % | — |  |  |
| `shot.technique.id` | int | 100 % | 0 % | 5 | `92` |  |
| `shot.technique.name` | str | 100 % | 0 % | 5 | `Lob` |  |
| `shot.body_part` | object | 100 % | 0 % | — |  |  |
| `shot.body_part.id` | int | 100 % | 0 % | 3 | `38` |  |
| `shot.body_part.name` | str | 100 % | 0 % | 3 | `Left Foot` |  |
| `shot.type` | object | 100 % | 0 % | — |  |  |
| `shot.type.id` | int | 100 % | 0 % | 3 | `87` |  |
| `shot.type.name` | str | 100 % | 0 % | 3 | `Open Play` |  |
| `shot.freeze_frame` | array | 98 % | 0 % | — |  |  |
| `shot.freeze_frame[]` | object | — | 0 % | — |  |  |
| `shot.freeze_frame[].location` | array | 100 % | 0 % | — |  |  |
| `shot.freeze_frame[].location[]` | float | — | 0 % | 861 | `112.9` |  |
| `shot.freeze_frame[].player` | object | 100 % | 0 % | — |  |  |
| `shot.freeze_frame[].player.id` | int | 100 % | 0 % | 155 | `4892` |  |
| `shot.freeze_frame[].player.name` | str | 100 % | 0 % | 155 | `Sergio Germán Romero` |  |
| `shot.freeze_frame[].position` | object | 100 % | 0 % | — |  |  |
| `shot.freeze_frame[].position.id` | int | 100 % | 0 % | 21 | `1` |  |
| `shot.freeze_frame[].position.name` | str | 100 % | 0 % | 21 | `Goalkeeper` |  |
| `shot.freeze_frame[].teammate` | bool | 100 % | 0 % | 2 | `False` |  |
| `goalkeeper` | object | <1 % | 0 % | — |  |  |
| `goalkeeper.end_location` | array | 52 % | 0 % | — |  |  |
| `goalkeeper.end_location[]` | float | — | 0 % | 84 | `7.2` |  |
| `goalkeeper.position` | object | 83 % | 0 % | — |  |  |
| `goalkeeper.position.id` | int | 100 % | 0 % | 3 | `42` |  |
| `goalkeeper.position.name` | str | 100 % | 0 % | 3 | `Moving` |  |
| `goalkeeper.type` | object | 100 % | 0 % | — |  |  |
| `goalkeeper.type.id` | int | 100 % | 0 % | 7 | `32` |  |
| `goalkeeper.type.name` | str | 100 % | 0 % | 7 | `Shot Faced` |  |
| `pass.cross` | bool | 2 % | 0 % | 1 | `True` |  |
| `goalkeeper.outcome` | object | 48 % | 0 % | — |  |  |
| `goalkeeper.outcome.id` | int | 100 % | 0 % | 10 | `15` |  |
| `goalkeeper.outcome.name` | str | 100 % | 0 % | 10 | `Success` |  |
| `pass.cut_back` | bool | <1 % | 0 % | 1 | `True` |  |
| `clearance` | object | <1 % | 0 % | — |  |  |
| `clearance.body_part` | object | 100 % | 0 % | — |  |  |
| `clearance.body_part.id` | int | 100 % | 0 % | 4 | `37` |  |
| `clearance.body_part.name` | str | 100 % | 0 % | 4 | `Head` |  |
| `clearance.head` | bool | 45 % | 0 % | 1 | `True` |  |
| `dribble.nutmeg` | bool | 7 % | 0 % | 1 | `True` |  |
| `pass.outswinging` | bool | <1 % | 0 % | 1 | `True` |  |
| `shot.first_time` | bool | 32 % | 0 % | 1 | `True` |  |
| `goalkeeper.technique` | object | 31 % | 0 % | — |  |  |
| `goalkeeper.technique.id` | int | 100 % | 0 % | 2 | `46` |  |
| `goalkeeper.technique.name` | str | 100 % | 0 % | 2 | `Standing` |  |
| `foul_won` | object | <1 % | 0 % | — |  |  |
| `foul_won.defensive` | bool | 70 % | 0 % | 1 | `True` |  |
| `clearance.right_foot` | bool | 32 % | 0 % | 1 | `True` |  |
| `goalkeeper.body_part` | object | 24 % | 0 % | — |  |  |
| `goalkeeper.body_part.id` | int | 100 % | 0 % | 6 | `40` |  |
| `goalkeeper.body_part.name` | str | 100 % | 0 % | 6 | `Right Foot` |  |
| `foul_committed` | object | <1 % | 0 % | — |  |  |
| `foul_committed.advantage` | bool | 40 % | 0 % | 1 | `True` |  |
| `foul_won.advantage` | bool | 33 % | 0 % | 1 | `True` |  |
| `interception` | object | <1 % | 0 % | — |  |  |
| `interception.outcome` | object | 100 % | 0 % | — |  |  |
| `interception.outcome.id` | int | 100 % | 0 % | 4 | `4` |  |
| `interception.outcome.name` | str | 100 % | 0 % | 4 | `Won` |  |
| `foul_committed.card` | object | 43 % | 0 % | — |  |  |
| `foul_committed.card.id` | int | 100 % | 0 % | 3 | `7` |  |
| `foul_committed.card.name` | str | 100 % | 0 % | 3 | `Yellow Card` |  |
| `pass.inswinging` | bool | <1 % | 0 % | 1 | `True` |  |
| `clearance.aerial_won` | bool | 16 % | 0 % | 1 | `True` |  |
| `clearance.left_foot` | bool | 22 % | 0 % | 1 | `True` |  |
| `ball_recovery` | object | <1 % | 0 % | — |  |  |
| `ball_recovery.recovery_failure` | bool | 96 % | 0 % | 1 | `True` |  |
| `dribble.overrun` | bool | 4 % | 0 % | 1 | `True` |  |
| `substitution` | object | <1 % | 0 % | — |  |  |
| `substitution.outcome` | object | 100 % | 0 % | — |  |  |
| `substitution.outcome.id` | int | 100 % | 0 % | 2 | `103` |  |
| `substitution.outcome.name` | str | 100 % | 0 % | 2 | `Tactical` |  |
| `substitution.replacement` | object | 100 % | 0 % | — |  |  |
| `substitution.replacement.id` | int | 100 % | 0 % | 43 | `40127` |  |
| `substitution.replacement.name` | str | 100 % | 0 % | 43 | `Ryan Mason` |  |
| `foul_committed.type` | object | 11 % | 0 % | — |  |  |
| `foul_committed.type.id` | int | 100 % | 0 % | 2 | `21` |  |
| `foul_committed.type.name` | str | 100 % | 0 % | 2 | `Dangerous Play` |  |
| `miscontrol` | object | <1 % | 0 % | — |  |  |
| `miscontrol.aerial_won` | bool | 100 % | 0 % | 1 | `True` |  |
| `50_50` | object | <1 % | 0 % | — |  |  |
| `50_50.outcome` | object | 100 % | 0 % | — |  |  |
| `50_50.outcome.id` | int | 100 % | 0 % | 4 | `1` |  |
| `50_50.outcome.name` | str | 100 % | 0 % | 4 | `Lost` |  |
| `ball_recovery.offensive` | bool | 4 % | 0 % | 1 | `True` |  |
| `shot.one_on_one` | bool | 5 % | 0 % | 1 | `True` |  |
| `shot.deflected` | bool | 4 % | 0 % | 1 | `True` |  |
| `block` | object | <1 % | 0 % | — |  |  |
| `block.deflection` | bool | 80 % | 0 % | 1 | `True` |  |
| `pass.no_touch` | bool | <1 % | 0 % | 1 | `True` |  |
| `foul_committed.offensive` | bool | 11 % | 0 % | 1 | `True` |  |
| `pass.goal_assist` | bool | <1 % | 0 % | 1 | `True` |  |
| `shot.aerial_won` | bool | 8 % | 0 % | 1 | `True` |  |
| `pass.miscommunication` | bool | <1 % | 0 % | 1 | `True` |  |
| `pass.deflected` | bool | <1 % | 0 % | 1 | `True` |  |
| `clearance.other` | bool | 1 % | 0 % | 1 | `True` |  |
| `block.offensive` | bool | 13 % | 0 % | 1 | `True` |  |
| `foul_committed.penalty` | bool | 4 % | 0 % | 1 | `True` |  |
| `foul_won.penalty` | bool | 4 % | 0 % | 1 | `True` |  |
| `injury_stoppage` | object | <1 % | 0 % | — |  |  |
| `injury_stoppage.in_chain` | bool | 100 % | 0 % | 1 | `True` |  |
| `block.save_block` | bool | 7 % | 0 % | 1 | `True` |  |

## `lineups`

- Archivos: 6 (3754097, 3754159, 3773457, 3773593, 3930158, 3943043) · 0.1 MB
- Registros perfilados: 12

| Campo | Tipos | Presencia | Nulos | Distintos | Ejemplo | ¿Clave? |
|---|---|---|---|---|---|---|
| `team_id` | int | 100 % | 0 % | 10 | `39` |  |
| `team_name` | str | 100 % | 0 % | 10 | `Manchester United` |  |
| `lineup` | array | 100 % | 0 % | — |  |  |
| `lineup[]` | object | — | 0 % | — |  |  |
| `lineup[].player_id` | int | 100 % | 0 % | 224 | `2988` |  |
| `lineup[].player_name` | str | 100 % | 0 % | 224 | `Memphis Depay` |  |
| `lineup[].player_nickname` | null, str | 100 % | 56 % | 93 | `Antonio Valencia` |  |
| `lineup[].jersey_number` | int | 100 % | 0 % | 43 | `7` |  |
| `lineup[].country` | object | 100 % | 0 % | — |  |  |
| `lineup[].country.id` | int | 100 % | 0 % | 32 | `160` |  |
| `lineup[].country.name` | str | 100 % | 0 % | 32 | `Netherlands` |  |
| `lineup[].cards` | array | 100 % | 0 % | — |  |  |
| `lineup[].positions` | array | 100 % | 0 % | — |  |  |
| `lineup[].positions[]` | object | — | 0 % | — |  |  |
| `lineup[].positions[].position_id` | int | 100 % | 0 % | 21 | `19` |  |
| `lineup[].positions[].position` | str | 100 % | 0 % | 21 | `Center Attacking Midfield` |  |
| `lineup[].positions[].from` | str | 100 % | 0 % | 47 | `00:00` |  |
| `lineup[].positions[].to` | null, str | 100 % | 63 % | 47 | `67:54` |  |
| `lineup[].positions[].from_period` | int | 100 % | 0 % | 2 | `1` |  |
| `lineup[].positions[].to_period` | int, null | 100 % | 63 % | 2 | `2` |  |
| `lineup[].positions[].start_reason` | str | 100 % | 0 % | 4 | `Starting XI` |  |
| `lineup[].positions[].end_reason` | str | 100 % | 0 % | 6 | `Substitution - Off (Tactical)` |  |
| `lineup[].cards[]` | object | — | 0 % | — |  |  |
| `lineup[].cards[].time` | str | 100 % | 0 % | 20 | `89:44` | ✔ |
| `lineup[].cards[].card_type` | str | 100 % | 0 % | 3 | `Yellow Card` |  |
| `lineup[].cards[].reason` | str | 100 % | 0 % | 1 | `Foul Committed` |  |
| `lineup[].cards[].period` | int | 100 % | 0 % | 2 | `2` |  |

## `matches`

- Archivos: 3 (11_90, 2_27, 55_282) · 0.6 MB
- Registros perfilados: 466

| Campo | Tipos | Presencia | Nulos | Distintos | Ejemplo | ¿Clave? |
|---|---|---|---|---|---|---|
| `match_id` | int | 100 % | 0 % | 466 | `3773386` | ✔ |
| `match_date` | str | 100 % | 0 % | 156 | `2020-10-31` |  |
| `kick_off` | str | 100 % | 0 % | 22 | `21:00:00.000` |  |
| `competition` | object | 100 % | 0 % | — |  |  |
| `competition.competition_id` | int | 100 % | 0 % | 3 | `11` |  |
| `competition.country_name` | str | 100 % | 0 % | 3 | `Spain` |  |
| `competition.competition_name` | str | 100 % | 0 % | 3 | `La Liga` |  |
| `season` | object | 100 % | 0 % | — |  |  |
| `season.season_id` | int | 100 % | 0 % | 3 | `90` |  |
| `season.season_name` | str | 100 % | 0 % | 3 | `2020/2021` |  |
| `home_team` | object | 100 % | 0 % | — |  |  |
| `home_team.home_team_id` | int | 100 % | 0 % | 62 | `206` |  |
| `home_team.home_team_name` | str | 100 % | 0 % | 62 | `Deportivo Alavés` |  |
| `home_team.home_team_gender` | str | 100 % | 0 % | 1 | `male` |  |
| `home_team.home_team_group` | null | 100 % | 100 % | 0 |  |  |
| `home_team.country` | object | 100 % | 0 % | — |  |  |
| `home_team.country.id` | int | 100 % | 0 % | 25 | `214` |  |
| `home_team.country.name` | str | 100 % | 0 % | 25 | `Spain` |  |
| `home_team.managers` | array | 100 % | 0 % | — |  |  |
| `home_team.managers[]` | object | — | 0 % | — |  |  |
| `home_team.managers[].id` | int | 100 % | 0 % | 68 | `234` |  |
| `home_team.managers[].name` | str | 100 % | 0 % | 68 | `Pablo Javier Machín Díez` |  |
| `home_team.managers[].nickname` | null, str | 100 % | 76 % | 22 | `Pablo Machín` |  |
| `home_team.managers[].dob` | str | 100 % | 0 % | 68 | `1975-04-07` |  |
| `home_team.managers[].country` | object | 100 % | 0 % | — |  |  |
| `home_team.managers[].country.id` | int | 100 % | 0 % | 22 | `214` |  |
| `home_team.managers[].country.name` | str | 100 % | 0 % | 22 | `Spain` |  |
| `away_team` | object | 100 % | 0 % | — |  |  |
| `away_team.away_team_id` | int | 100 % | 0 % | 63 | `217` |  |
| `away_team.away_team_name` | str | 100 % | 0 % | 63 | `Barcelona` |  |
| `away_team.away_team_gender` | str | 100 % | 0 % | 1 | `male` |  |
| `away_team.away_team_group` | null | 100 % | 100 % | 0 |  |  |
| `away_team.country` | object | 100 % | 0 % | — |  |  |
| `away_team.country.id` | int | 100 % | 0 % | 25 | `214` |  |
| `away_team.country.name` | str | 100 % | 0 % | 25 | `Spain` |  |
| `away_team.managers` | array | 100 % | 0 % | — |  |  |
| `away_team.managers[]` | object | — | 0 % | — |  |  |
| `away_team.managers[].id` | int | 100 % | 0 % | 68 | `676` |  |
| `away_team.managers[].name` | str | 100 % | 0 % | 68 | `Ronald Koeman` |  |
| `away_team.managers[].nickname` | null, str | 100 % | 76 % | 23 | `Eduardo Coudet` |  |
| `away_team.managers[].dob` | str | 100 % | 0 % | 68 | `1963-03-21` |  |
| `away_team.managers[].country` | object | 100 % | 0 % | — |  |  |
| `away_team.managers[].country.id` | int | 100 % | 0 % | 22 | `160` |  |
| `away_team.managers[].country.name` | str | 100 % | 0 % | 22 | `Netherlands` |  |
| `home_score` | int | 100 % | 0 % | 7 | `1` |  |
| `away_score` | int | 100 % | 0 % | 7 | `1` |  |
| `match_status` | str | 100 % | 0 % | 1 | `available` |  |
| `match_status_360` | str | 100 % | 0 % | 3 | `available` |  |
| `last_updated` | str | 100 % | 0 % | 436 | `2023-07-25T03:54:59.280826` |  |
| `last_updated_360` | str | 100 % | 0 % | 77 | `2023-07-25T04:25:41.348202` |  |
| `metadata` | object | 100 % | 0 % | — |  |  |
| `metadata.data_version` | str | 100 % | 0 % | 1 | `1.1.0` |  |
| `metadata.shot_fidelity_version` | str | 100 % | 0 % | 1 | `2` |  |
| `metadata.xy_fidelity_version` | str | 100 % | 0 % | 1 | `2` |  |
| `match_week` | int | 100 % | 0 % | 38 | `8` |  |
| `competition_stage` | object | 100 % | 0 % | — |  |  |
| `competition_stage.id` | int | 100 % | 0 % | 6 | `1` |  |
| `competition_stage.name` | str | 100 % | 0 % | 6 | `Regular Season` |  |
| `stadium` | object | 100 % | 0 % | — |  |  |
| `stadium.id` | int | 100 % | 0 % | 49 | `348` |  |
| `stadium.name` | str | 100 % | 0 % | 49 | `Estadio de Mendizorroza` |  |
| `stadium.country` | object | 100 % | 0 % | — |  |  |
| `stadium.country.id` | int | 100 % | 0 % | 4 | `214` |  |
| `stadium.country.name` | str | 100 % | 0 % | 4 | `Spain` |  |
| `referee` | object | 99 % | 0 % | — |  |  |
| `referee.id` | int | 100 % | 0 % | 51 | `2602` |  |
| `referee.name` | str | 100 % | 0 % | 51 | `Ricardo De Burgos Bengoetxea` |  |
| `referee.country` | object | 100 % | 0 % | — |  |  |
| `referee.country.id` | int | 100 % | 0 % | 15 | `214` |  |
| `referee.country.name` | str | 100 % | 0 % | 15 | `Spain` |  |

## `three_sixty`

- Archivos: 4 (3773457, 3773593, 3930158, 3943043) · 26.2 MB
- Registros perfilados: 13739

| Campo | Tipos | Presencia | Nulos | Distintos | Ejemplo | ¿Clave? |
|---|---|---|---|---|---|---|
| `event_uuid` | str | 100 % | 0 % | muchos | `daac9c8d-95b6-4e42-8cfa-b05779fd7755` |  |
| `visible_area` | array | 100 % | 0 % | — |  |  |
| `visible_area[]` | float | — | 0 % | muchos | `45.677289609455414` |  |
| `freeze_frame` | array | 100 % | 0 % | — |  |  |
| `freeze_frame[]` | object | — | 0 % | — |  |  |
| `freeze_frame[].teammate` | bool | 100 % | 0 % | 2 | `True` |  |
| `freeze_frame[].actor` | bool | 100 % | 0 % | 2 | `False` |  |
| `freeze_frame[].keeper` | bool | 100 % | 0 % | 2 | `False` |  |
| `freeze_frame[].location` | array | 100 % | 0 % | — |  |  |
| `freeze_frame[].location[]` | float | — | 0 % | muchos | `38.754391867375126` |  |
