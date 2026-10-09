import json
from datetime import date

import responses

from src.clients.api_football import DEFAULT_BASE_URL as AF_URL
from src.clients.api_football import ApiFootballClient, ApiFootballError
from src.clients.base_client import ApiError
from src.clients.budget import InMemoryBudget
from src.ingestion.errors import is_permanent_error
from src.ingestion.handlers import ConfigRow, plan_fixture_backfill
from src.ingestion.runner import run_config
from src.ingestion.source_config import SOURCE_CONFIGS
from tests.ingestion.fakes import InMemoryWriter

TODAY = date(2026, 10, 9)
EURO, PL = {"league": 4, "season": 2024}, {"league": 39, "season": 2024}


def config(config_id, **param_overrides):
    source_config = next(c for c in SOURCE_CONFIGS if c.config_id == config_id)
    row = ConfigRow.from_table_row(source_config.as_row())
    return ConfigRow(
        row.config_id, row.source, row.entity, row.load_type, {**row.params, **param_overrides}
    )


def af_payload(response, *, total=1, current=1):
    return {
        "errors": [],
        "results": len(response),
        "paging": {"current": current, "total": total},
        "response": response,
    }


def af_client(quota=None, daily_used=0):
    daily = InMemoryBudget(90, name="diario", used=daily_used)
    budgets = [InMemoryBudget(quota, name="cuota")] if quota is not None else []
    return ApiFootballClient("k", daily_budget=daily, budgets=budgets, sleep=lambda _: None), daily


def fixture(fid, day, status="FT"):
    return {
        "fixture": {
            "id": fid,
            "date": f"2024-08-{day:02d}T19:00:00+00:00",
            "status": {"short": status},
        }
    }


def load_fixtures(writer, target, fixtures):
    """Simula que af_fixtures ya cargó estos partidos en Bronze."""
    writer.tables.setdefault("api_football_fixtures", []).extend(
        {
            "record_key": str(f["fixture"]["id"]),
            "record_hash": str(f["fixture"]["id"]),
            "record_context": json.dumps(target),
            "payload": json.dumps(f),
        }
        for f in fixtures
    )


# --- season_full --------------------------------------------------------------------------------


@responses.activate
def test_season_full_stops_at_quota_and_only_marks_fetched_targets():
    responses.get(f"{AF_URL}/fixtures", json=af_payload([fixture(1, 1)]))
    client, _ = af_client(quota=2)
    writer = InMemoryWriter()

    stats = run_config(writer, client, config("af_fixtures"), None, batch_id="B1", today=TODAY)

    assert stats.stopped_by_budget
    assert len(responses.calls) == 2  # Euro y PL; La Liga queda para la siguiente ejecución
    assert json.loads(stats.watermark_after) == ["league=39|season=2024", "league=4|season=2024"]


# --- players por equipo (tope de página del plan gratuito) -------------------------------------


def load_teams(writer, target, team_ids):
    """Simula que af_teams ya cargó estos equipos en Bronze."""
    writer.tables.setdefault("api_football_teams", []).extend(
        {
            "record_key": f"{target['league']}|{target['season']}|{tid}",
            "record_hash": str(tid),
            "record_context": json.dumps(target),
            "payload": json.dumps({"team": {"id": tid}}),
        }
        for tid in team_ids
    )


def mock_team_pages(team, total_pages):
    for page in range(1, total_pages + 1):
        responses.get(
            f"{AF_URL}/players",
            json=af_payload(
                [{"player": {"id": team * 100 + page}}], total=total_pages, current=page
            ),
            match=[
                responses.matchers.query_param_matcher(
                    {"team": str(team), "season": "2024", "page": str(page)}
                )
            ],
        )


@responses.activate
def test_players_by_team_caps_pages_and_marks_truncated():
    writer = InMemoryWriter()
    load_teams(writer, EURO, [1, 2])
    mock_team_pages(1, total_pages=4)  # el plan gratuito no deja pedir la página 4
    mock_team_pages(2, total_pages=2)

    stats = run_config(
        writer, af_client(quota=10)[0], config("af_players"), None, batch_id="B1", today=TODAY
    )

    progress = json.loads(stats.watermark_after)
    assert progress["4|2024|1"] == {"next_page": 4, "total_pages": 4, "truncated": True}
    assert progress["4|2024|2"] == {"next_page": 3, "total_pages": 2, "truncated": False}
    assert len(responses.calls) == 5  # 3 + 2 páginas; nunca la 4
    assert "4|2024|1|101" in writer.existing_keys("api_football_players")


@responses.activate
def test_players_by_team_resumes_after_budget_stop():
    writer = InMemoryWriter()
    load_teams(writer, EURO, [1, 2])
    mock_team_pages(1, total_pages=2)
    mock_team_pages(2, total_pages=2)
    cfg = config("af_players")

    first = run_config(writer, af_client(quota=3)[0], cfg, None, batch_id="B1", today=TODAY)
    second = run_config(
        writer, af_client(quota=3)[0], cfg, first.watermark_after, batch_id="B2", today=TODAY
    )

    assert first.stopped_by_budget and first.files_written == 3
    assert not second.stopped_by_budget and second.files_written == 1  # solo la página que faltaba
    assert len(responses.calls) == 4


@responses.activate
def test_error_mid_run_keeps_what_was_downloaded():
    writer = InMemoryWriter()
    load_teams(writer, EURO, [1])
    mock_team_pages(1, total_pages=1)
    load_teams(writer, PL, [33])
    responses.get(
        f"{AF_URL}/players",
        json={"errors": {"plan": "Free plans are limited"}, "response": [], "paging": {}},
    )

    stats = run_config(
        writer, af_client(quota=10)[0], config("af_players"), None, batch_id="B1", today=TODAY
    )

    assert stats.error is not None and is_permanent_error(stats.error)
    assert stats.files_written == 1  # la página de la Euro se guardó antes del error
    assert json.loads(stats.watermark_after)["4|2024|1"]["next_page"] == 2


def test_error_classification():
    assert is_permanent_error(ApiFootballError({"plan": "x"}))
    assert is_permanent_error(ApiError("forbidden", status_code=403))
    assert not is_permanent_error(ApiError("rate", status_code=429))
    assert not is_permanent_error(ApiError("server", status_code=503))
    assert not is_permanent_error(ApiError("red", status_code=None))


@responses.activate
def test_status_call_is_not_billable():
    responses.get(f"{AF_URL}/status", json=af_payload({"requests": {"current": 0}}))
    responses.get(f"{AF_URL}/teams", json=af_payload([]))
    client, _ = af_client()

    client.sync_budget()
    client.teams(league=4, season=2024)

    assert client.calls_made == 2
    assert client.billable_calls == 1


# --- relleno por partido ------------------------------------------------------------------------


def test_plan_fixture_backfill_orders_by_target_then_date_and_skips_done():
    writer = InMemoryWriter()
    load_fixtures(writer, PL, [fixture(10, 16), fixture(11, 17, status="NS")])
    load_fixtures(writer, EURO, [fixture(2, 20), fixture(1, 14)])

    pending = plan_fixture_backfill(
        config("af_fixture_statistics"), writer.latest_records("api_football_fixtures"), {"1"}
    )

    # Euro primero (orden de targets); el 1 ya está hecho y el 11 no está terminado
    assert [p["fixture_id"] for p in pending] == [2, 10]


@responses.activate
def test_fixture_backfill_consumes_quota_and_continues_next_run():
    writer = InMemoryWriter()
    load_fixtures(writer, EURO, [fixture(i, i) for i in range(1, 6)])
    responses.get(f"{AF_URL}/fixtures/statistics", json=af_payload([{"team": {"id": 1}}]))
    cfg = config("af_fixture_statistics")

    first = run_config(writer, af_client(quota=3)[0], cfg, None, batch_id="B1", today=TODAY)
    second = run_config(writer, af_client(quota=3)[0], cfg, None, batch_id="B2", today=TODAY)

    assert first.stopped_by_budget and first.files_written == 3
    assert json.loads(first.watermark_after) == {"done": 3, "pending": 2}
    assert not second.stopped_by_budget and second.files_written == 2
    assert writer.existing_keys("api_football_fixture_statistics") == {"1", "2", "3", "4", "5"}
    assert len(responses.calls) == 5  # ningún partido se pidió dos veces


@responses.activate
def test_fixture_backfill_without_fixtures_has_nothing_pending():
    # La pipeline no garantiza el orden (ADR-010): si aún no hay partidos, no pasa nada
    stats = run_config(
        InMemoryWriter(),
        af_client(quota=40)[0],
        config("af_fixture_players"),
        None,
        batch_id="B1",
        today=TODAY,
    )

    assert stats.files_written == 0
    assert len(responses.calls) == 0


@responses.activate
def test_daily_budget_stops_backfill_even_with_quota_left():
    writer = InMemoryWriter()
    load_fixtures(writer, EURO, [fixture(i, i) for i in range(1, 6)])
    responses.get(f"{AF_URL}/fixtures/players", json=af_payload([]))
    client, daily = af_client(quota=40, daily_used=88)  # quedan 2 del presupuesto diario

    stats = run_config(
        writer, client, config("af_fixture_players"), None, batch_id="B1", today=TODAY
    )

    assert stats.stopped_by_budget
    assert stats.files_written == 2
    assert daily.used == 90
