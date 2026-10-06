import json
from datetime import date

import pytest
import responses

from src.clients.football_data import DEFAULT_BASE_URL as FD_URL
from src.clients.football_data import FootballDataClient
from src.ingestion.batch import build_batch
from src.ingestion.handlers import ConfigRow, run_handler
from src.ingestion.source_config import SOURCE_CONFIGS

TODAY = date(2026, 10, 5)


def config(config_id):
    source_config = next(c for c in SOURCE_CONFIGS if c.config_id == config_id)
    return ConfigRow.from_table_row(source_config.as_row())


def fd_client():
    return FootballDataClient("key", sleep=lambda _: None)


def competition_payload(code):
    return {"code": code, "currentSeason": {"startDate": "2026-08-21", "endDate": "2027-05-30"}}


@responses.activate
def test_window_requests_each_target_with_lookback_window():
    for code in ("PL", "PD"):
        responses.get(f"{FD_URL}/competitions/{code}", json=competition_payload(code))
        responses.get(f"{FD_URL}/competitions/{code}/matches", json={"matches": [{"id": 1}]})

    result = run_handler(fd_client(), config("fd_matches_current"), "2026-10-04", TODAY)

    match_calls = [c.request for c in responses.calls if c.request.url.count("/matches")]
    assert match_calls[0].params == {"dateFrom": "2026-09-27", "dateTo": "2026-10-19"}
    assert result.watermark_after == "2026-10-05"
    assert [f.context["competition"] for f in result.raw_files] == ["PL", "PD"]


@responses.activate
def test_season_full_skips_completed_targets_and_records_them():
    responses.get(f"{FD_URL}/competitions/PD/matches", json={"matches": []})
    responses.get(f"{FD_URL}/competitions/EC/matches", json={"matches": []})
    watermark = json.dumps(["competition=PL|season=2024"])

    result = run_handler(fd_client(), config("fd_matches_history"), watermark, TODAY)

    assert [f.name for f in result.raw_files] == ["PD_2024", "EC_2024"]
    assert len(responses.calls) == 2  # PL 2024 ya estaba completada: 0 llamadas
    assert set(json.loads(result.watermark_after)) == {
        "competition=PL|season=2024",
        "competition=PD|season=2024",
        "competition=EC|season=2024",
    }


@responses.activate
def test_second_run_of_closed_season_makes_no_calls():
    for code in ("PL", "PD", "EC"):
        responses.get(f"{FD_URL}/competitions/{code}/matches", json={"matches": []})
    first = run_handler(fd_client(), config("fd_matches_history"), None, TODAY)
    calls_after_first = len(responses.calls)

    second = run_handler(fd_client(), config("fd_matches_history"), first.watermark_after, TODAY)

    assert second.raw_files == []
    assert len(responses.calls) == calls_after_first


@responses.activate
def test_snapshot_uses_current_season_without_param():
    responses.get(f"{FD_URL}/competitions/PL/standings", json={"standings": []})
    responses.get(f"{FD_URL}/competitions/PD/standings", json={"standings": []})

    result = run_handler(fd_client(), config("fd_standings"), None, TODAY)

    assert all("season" not in c.request.params for c in responses.calls)
    assert result.raw_files[0].context["snapshot_date"] == "2026-10-05"


def test_unknown_handler_is_explicit():
    with pytest.raises(NotImplementedError):
        run_handler(None, config("sb_match_files"), None, TODAY)


@responses.activate
def test_build_batch_maps_files_and_rows_per_table():
    responses.get(
        f"{FD_URL}/competitions",
        json={"competitions": [{"id": 2021, "code": "PL"}, {"id": 2014, "code": "PD"}]},
    )
    result = run_handler(fd_client(), config("fd_competitions"), None, TODAY)

    batch = build_batch(
        result,
        source="football_data",
        config_id="fd_competitions",
        batch_id="B1",
        ingest_date=TODAY,
    )

    assert batch.files[0][0] == (
        "Files/raw/football_data/competitions/ingest_date=2026-10-05/B1/competitions.json"
    )
    rows = batch.rows_by_table["football_data_competitions"]
    assert [r["record_key"] for r in rows] == ["2021", "2014"]
    assert {r["_batch_id"] for r in rows} == {"B1"}
    assert batch.records_read == 2
