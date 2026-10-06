import json
from datetime import UTC, date, datetime

import pytest

from src.ingestion.raw_layout import (
    bronze_table_name,
    new_batch_id,
    raw_relative_path,
    safe_name,
)
from src.ingestion.records import extract_records, stable_hash

MATCH = {"id": 1, "status": "TIMED", "lastUpdated": "2026-10-01T00:00:00Z", "score": {"home": None}}


def test_raw_path_follows_bronze_layout():
    path = raw_relative_path("football_data", "matches", date(2026, 10, 5), "B1", "PL 2024/25")

    assert path == "Files/raw/football_data/matches/ingest_date=2026-10-05/B1/PL_2024_25.json"
    assert bronze_table_name("football_data", "matches") == "football_data_matches"
    assert safe_name("///") == "payload"


def test_batch_id_is_sortable_and_unique():
    now = datetime(2026, 10, 5, 17, 15, tzinfo=UTC)
    first, second = new_batch_id(now), new_batch_id(now)

    assert first.startswith("20261005T171500Z_")
    assert first != second


def test_hash_ignores_volatile_fields_but_not_real_changes():
    volatile = frozenset({"lastUpdated"})
    refreshed = {**MATCH, "lastUpdated": "2026-10-05T09:00:00Z"}
    rescheduled = {**MATCH, "status": "POSTPONED"}

    assert stable_hash(MATCH, volatile) == stable_hash(refreshed, volatile)
    assert stable_hash(MATCH, volatile) != stable_hash(rescheduled, volatile)


def test_hash_ignores_key_order_and_nested_volatile_fields():
    a = {"x": 1, "season": {"id": 9, "currentMatchday": 3}}
    b = {"season": {"currentMatchday": 4, "id": 9}, "x": 1}

    assert stable_hash(a, frozenset({"currentMatchday"})) == stable_hash(
        b, frozenset({"currentMatchday"})
    )


def test_football_data_matches_one_record_per_match():
    payload = {"matches": [MATCH, {**MATCH, "id": 2}]}

    records = extract_records("football_data", "matches", payload, {"competition": "PL"})

    assert [r.record_key for r in records] == ["1", "2"]
    assert json.loads(records[0].payload)["lastUpdated"] == MATCH["lastUpdated"]  # crudo intacto
    assert json.loads(records[0].record_context) == {"competition": "PL"}


def test_football_data_teams_key_includes_season():
    payload = {"season": {"id": 2292}, "teams": [{"id": 57}, {"id": 61}]}

    keys = [r.record_key for r in extract_records("football_data", "teams", payload, {})]

    assert keys == ["2292|57", "2292|61"]


def test_football_data_standings_is_one_document_per_competition_season():
    payload = {"competition": {"code": "PL"}, "season": {"id": 2502}, "standings": []}

    records = extract_records("football_data", "standings", payload, {})

    assert [r.record_key for r in records] == ["PL|2502"]


def test_unknown_entity_fails_loudly():
    with pytest.raises(ValueError, match="No hay regla"):
        extract_records("football_data", "unknown", {}, {})
