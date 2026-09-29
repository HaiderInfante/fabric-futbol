# Cobertura de fuentes (Fase 1, paso A)

> Generado por `scripts/explore/discover_coverage.py` el 2026-09-29 23:24 UTC. Se regenera en cada ejecución: no editar a mano.

## Resumen por competición candidata

| Competición | football-data: plan · temporada actual | StatsBomb: temporadas |
|---|---|---|
| Premier League | TIER_ONE · 2026-08-21 → 2027-05-30 | 2003/2004, 2015/2016 |
| La Liga | TIER_ONE · 2026-08-16 → 2027-05-30 | 1973/1974, 2004/2005, 2005/2006, 2006/2007, 2007/2008, 2008/2009, 2009/2010, 2010/2011, 2011/2012, 2012/2013, 2013/2014, 2014/2015, 2015/2016, 2016/2017, 2017/2018, 2018/2019, 2019/2020, 2020/2021 (360) |
| Bundesliga | TIER_ONE · 2026-08-28 → 2027-05-22 | 2015/2016, 2023/2024 (360) |
| Serie A | TIER_ONE · 2026-08-23 → 2027-05-30 | 1986/1987, 2015/2016 |
| Ligue 1 | TIER_ONE · 2026-08-22 → 2027-05-29 | 2015/2016, 2021/2022 (360), 2022/2023 (360) |
| Champions League | TIER_ONE · 2026-09-08 → 2027-01-27 | 1970/1971, 1971/1972, 1972/1973, 1999/2000, 2003/2004, 2004/2005, 2006/2007, 2008/2009, 2009/2010, 2010/2011, 2011/2012, 2012/2013, 2013/2014, 2014/2015, 2015/2016, 2016/2017, 2017/2018, 2018/2019 |
| FIFA World Cup | TIER_ONE · 2026-06-11 → 2026-07-19 | 1958, 1962, 1970, 1974, 1986, 1990, 2018, 2022 (360) |
| UEFA Euro | TIER_ONE · 2024-06-14 → 2024-07-14 | 2020 (360), 2024 (360) |

## API-Football: temporadas y cobertura por liga

Temporadas desde 2015; `*` = temporada actual. Cobertura: `E` eventos, `L` alineaciones, `S` estadísticas de partido, `P` estadísticas de jugador, `I` lesiones (`·` = no disponible).

| Competición | Liga (id) | Temporadas |
|---|---|---|
| Premier League | Premier League (39) | 2015 `ELSP·`, 2016 `ELSP·`, 2017 `ELSP·`, 2018 `ELSP·`, 2019 `ELSP·`, 2020 `ELSPI`, 2021 `ELSPI`, 2022 `ELSPI`, 2023 `ELSPI`, 2024 `ELSPI`, 2025 `ELSPI`, 2026* `ELSPI` |
| La Liga | La Liga (140) | 2015 `ELSP·`, 2016 `ELSP·`, 2017 `ELSP·`, 2018 `ELSP·`, 2019 `ELSP·`, 2020 `ELSPI`, 2021 `ELSPI`, 2022 `ELSPI`, 2023 `ELSPI`, 2024 `ELSPI`, 2025 `ELSPI`, 2026* `ELSPI` |
| Bundesliga | Bundesliga (78) | 2015 `ELSP·`, 2016 `ELSP·`, 2017 `ELSP·`, 2018 `ELSP·`, 2019 `ELSP·`, 2020 `ELSPI`, 2021 `ELSPI`, 2022 `ELSPI`, 2023 `ELSPI`, 2024 `ELSPI`, 2025 `ELSPI`, 2026* `ELSPI` |
| Serie A | Serie A (135) | 2015 `ELSP·`, 2016 `ELSP·`, 2017 `ELSP·`, 2018 `ELSP·`, 2019 `ELSP·`, 2020 `ELSPI`, 2021 `ELSPI`, 2022 `ELSPI`, 2023 `ELSPI`, 2024 `ELSPI`, 2025 `ELSPI`, 2026* `ELSPI` |
| Ligue 1 | Ligue 1 (61) | 2015 `ELSP·`, 2016 `ELSP·`, 2017 `ELSP·`, 2018 `ELSP·`, 2019 `ELSP·`, 2020 `ELSPI`, 2021 `ELSPI`, 2022 `ELSPI`, 2023 `ELSPI`, 2024 `ELSPI`, 2025 `ELSPI`, 2026* `ELSPI` |
| Champions League | UEFA Champions League (2) | 2015 `ELSP·`, 2016 `ELSP·`, 2017 `ELSP·`, 2018 `ELSP·`, 2019 `ELSP·`, 2020 `ELSPI`, 2021 `ELSPI`, 2022 `ELSPI`, 2023 `ELSPI`, 2024 `ELSPI`, 2025 `ELSPI`, 2026* `ELSPI` |
| FIFA World Cup | World Cup (1) | 2018 `ELSP·`, 2022 `ELSP·`, 2026* `ELSPI` |
| UEFA Euro | Euro Championship (4) | 2016 `ELSP·`, 2020 `ELSP·`, 2024* `ELSP·` |

## Pruebas de acceso por temporada

Consulta de la tabla de posiciones de una temporada concreta: muestra si el plan gratuito da acceso a ella.

| Fuente | Competición | Temporada | Acceso | Detalle |
|---|---|---|---|---|
| football-data | PL | 2026 | ✅ | 20 equipos |
| football-data | PL | 2025 | ✅ | 20 equipos |
| football-data | PL | 2024 | ✅ | 20 equipos |
| football-data | PL | 2023 | ✅ | 20 equipos |
| football-data | PL | 2015 | ❌ | HTTP 403 en https://api.football-data.org/v4/competitions/PL/standings: {"message":"The resource you are looking for is restricted and apparently not within you |
| football-data | PD | 2026 | ✅ | 20 equipos |
| football-data | PD | 2025 | ✅ | 20 equipos |
| football-data | PD | 2024 | ✅ | 20 equipos |
| football-data | PD | 2020 | ❌ | HTTP 403 en https://api.football-data.org/v4/competitions/PD/standings: {"message":"The resource you are looking for is restricted and apparently not within you |
| API-Football | 39 | 2026 | ❌ | API-Football devolvió errores: {'plan': 'Free plans do not have access to this season, try from 2022 to 2024.'} |
| API-Football | 39 | 2024 | ✅ | 1 tabla(s) |
| API-Football | 39 | 2015 | ❌ | API-Football devolvió errores: {'plan': 'Free plans do not have access to this season, try from 2022 to 2024.'} |
| API-Football | 140 | 2024 | ✅ | 1 tabla(s) |
| API-Football | 140 | 2020 | ❌ | API-Football devolvió errores: {'plan': 'Free plans do not have access to this season, try from 2022 to 2024.'} |

## football-data.org: competiciones visibles (13)

| Código | Nombre | Tipo | Plan | Temporada actual | Temporadas disponibles |
|---|---|---|---|---|---|
| CLI | Copa Libertadores | CUP | TIER_FOUR | 2026-02-04 → 2026-11-28 | 6 |
| BL1 | Bundesliga | LEAGUE | TIER_ONE | 2026-08-28 → 2027-05-22 | 64 |
| BSA | Campeonato Brasileiro Série A | LEAGUE | TIER_ONE | 2026-01-28 → 2026-12-02 | 10 |
| CL | UEFA Champions League | CUP | TIER_ONE | 2026-09-08 → 2027-01-27 | 47 |
| DED | Eredivisie | LEAGUE | TIER_ONE | 2026-08-07 → 2027-05-23 | 71 |
| EC | European Championship | CUP | TIER_ONE | 2024-06-14 → 2024-07-14 | 17 |
| ELC | Championship | LEAGUE | TIER_ONE | 2026-08-14 → 2027-05-01 | 10 |
| FL1 | Ligue 1 | LEAGUE | TIER_ONE | 2026-08-22 → 2027-05-29 | 83 |
| PD | Primera Division | LEAGUE | TIER_ONE | 2026-08-16 → 2027-05-30 | 95 |
| PL | Premier League | LEAGUE | TIER_ONE | 2026-08-21 → 2027-05-30 | 128 |
| PPL | Primeira Liga | LEAGUE | TIER_ONE | 2026-08-08 → 2027-05-16 | 78 |
| SA | Serie A | LEAGUE | TIER_ONE | 2026-08-23 → 2027-05-30 | 95 |
| WC | FIFA World Cup | CUP | TIER_ONE | 2026-06-11 → 2026-07-19 | 23 |

## Cuotas observadas

- API-Football: 6 llamadas con cuota en esta ejecución (sin contar `/status`). Uso del día según el contador local: 10; según la API: 1/100.
- Headers de cuota de API-Football: `{'x-ratelimit-limit': '10', 'x-ratelimit-remaining': '6', 'x-ratelimit-requests-limit': '100', 'x-ratelimit-requests-remaining': '95'}`
- Headers de cuota de football-data.org: `{'X-RequestCounter-Reset': '58', 'x-requests-available-minute': '2'}`

## StatsBomb: todas las competiciones disponibles

| Id | Competición | País | Género | Temporadas |
|---|---|---|---|---|
| 2 | Premier League | England | male | 2003/2004, 2015/2016 |
| 7 | Ligue 1 | France | male | 2015/2016, 2021/2022 (360), 2022/2023 (360) |
| 9 | 1. Bundesliga | Germany | male | 2015/2016, 2023/2024 (360) |
| 11 | La Liga | Spain | male | 1973/1974, 2004/2005, 2005/2006, 2006/2007, 2007/2008, 2008/2009, 2009/2010, 2010/2011, 2011/2012, 2012/2013, 2013/2014, 2014/2015, 2015/2016, 2016/2017, 2017/2018, 2018/2019, 2019/2020, 2020/2021 (360) |
| 12 | Serie A | Italy | male | 1986/1987, 2015/2016 |
| 16 | Champions League | Europe | male | 1970/1971, 1971/1972, 1972/1973, 1999/2000, 2003/2004, 2004/2005, 2006/2007, 2008/2009, 2009/2010, 2010/2011, 2011/2012, 2012/2013, 2013/2014, 2014/2015, 2015/2016, 2016/2017, 2017/2018, 2018/2019 |
| 35 | UEFA Europa League | Europe | male | 1988/1989 |
| 37 | FA Women's Super League | England | female | 2018/2019, 2019/2020, 2020/2021, 2023/2024 |
| 43 | FIFA World Cup | International | male | 1958, 1962, 1970, 1974, 1986, 1990, 2018, 2022 (360) |
| 44 | Major League Soccer | United States of America | male | 2023 (360) |
| 49 | NWSL | United States of America | female | 2018, 2023 |
| 53 | UEFA Women's Euro | Europe | female | 2022 (360), 2025 (360) |
| 55 | UEFA Euro | Europe | male | 2020 (360), 2024 (360) |
| 72 | Women's World Cup | International | female | 2019, 2023 (360) |
| 81 | Liga Profesional | Argentina | male | 1981, 1997/1998 |
| 87 | Copa del Rey | Spain | male | 1977/1978, 1982/1983, 1983/1984 |
| 116 | North American League | North and Central America | male | 1977 |
| 131 | Serie A Women | Italy | female | 2023/2024 |
| 135 | Frauen Bundesliga | Germany | female | 2023/2024 |
| 182 | Liga F | Spain | female | 2023/2024 |
| 223 | Copa America | South America | male | 2024 |
| 1238 | Indian Super league | India | male | 2021/2022 |
| 1267 | African Cup of Nations | Africa | male | 2023 (360) |
| 1470 | FIFA U20 World Cup | International | male | 1979 |
