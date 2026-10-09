import json
from datetime import date

import responses

from src.clients.api_football import DEFAULT_BASE_URL as AF_URL
from src.clients.api_football import ApiFootballClient
from src.clients.budget import InMemoryBudget
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


# --- players por páginas ------------------------------------------------------------------------


@responses.activate
def test_players_pages_resume_where_previous_run_stopped():
    for page in range(1, 4):
        responses.get(
            f"{AF_URL}/players",
            json=af_payload([{"player": {"id": page}}], total=3, current=page),
            match=[
                responses.matchers.query_param_matcher(
                    {"league": "4", "season": "2024", "page": str(page)}
                )
            ],
        )
    writer = InMemoryWriter()
    cfg = config("af_players", targets=[EURO])

    first = run_config(writer, af_client(quota=2)[0], cfg, None, batch_id="B1", today=TODAY)
    second = run_config(
        writer, af_client(quota=2)[0], cfg, first.watermark_after, batch_id="B2", today=TODAY
    )

    assert first.stopped_by_budget
    assert json.loads(first.watermark_after) == {
        "league=4|season=2024": {"next_page": 3, "total_pages": 3}
    }
    assert not second.stopped_by_budget
    assert [c.request.params["page"] for c in responses.calls] == ["1", "2", "3"]
    assert writer.existing_keys("api_football_players") == {"4|2024|1", "4|2024|2", "4|2024|3"}


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
