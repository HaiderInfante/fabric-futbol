from datetime import date

import responses

from src.clients.statsbomb import DEFAULT_BASE_URL as SB_URL
from src.clients.statsbomb import StatsBombClient
from src.ingestion.handlers import ConfigRow, match_version
from src.ingestion.records import extract_records
from src.ingestion.runner import run_config
from src.ingestion.source_config import SOURCE_CONFIGS
from tests.ingestion.fakes import InMemoryWriter

TODAY = date(2026, 10, 8)


def config(config_id, **param_overrides):
    source_config = next(c for c in SOURCE_CONFIGS if c.config_id == config_id)
    row = ConfigRow.from_table_row(source_config.as_row())
    return ConfigRow(
        row.config_id, row.source, row.entity, row.load_type, {**row.params, **param_overrides}
    )


def match(match_id, day, *, has_360=False, updated="2023-07-25T03:54:59"):
    return {
        "match_id": match_id,
        "match_date": f"2024-06-{day:02d}",
        "match_status": "available",
        "match_status_360": "available" if has_360 else "scheduled",
        "last_updated": updated,
        "last_updated_360": "2023-07-25T04:25:41" if has_360 else None,
    }


def mock_statsbomb(matches_by_target):
    for (comp, season), matches in matches_by_target.items():
        responses.get(f"{SB_URL}/matches/{comp}/{season}.json", json=matches)
        for m in matches:
            mid = m["match_id"]
            responses.get(
                f"{SB_URL}/events/{mid}.json", json=[{"id": f"e{mid}-1"}, {"id": f"e{mid}-2"}]
            )
            responses.get(f"{SB_URL}/lineups/{mid}.json", json=[{"team_id": 1}, {"team_id": 2}])
            if m["match_status_360"] == "available":
                responses.get(
                    f"{SB_URL}/three-sixty/{mid}.json", json=[{"event_uuid": f"e{mid}-1"}]
                )


def single_target_config(**overrides):
    return config("sb_match_files", targets=[{"competition_id": 55, "season_id": 282}], **overrides)


def sb_client():
    return StatsBombClient(sleep=lambda _: None)


def file_downloads():
    return [c for c in responses.calls if "/matches/" not in c.request.url]


def test_statsbomb_record_keys():
    assert extract_records("statsbomb", "events", [{"id": "uuid-1"}], {})[0].record_key == "uuid-1"
    lineups = extract_records("statsbomb", "lineups", [{"team_id": 9}], {"match_id": 7})
    assert lineups[0].record_key == "7|9"
    assert match_version(match(1, 1, has_360=True)) == "2023-07-25T03:54:59|2023-07-25T04:25:41"


@responses.activate
def test_first_run_downloads_everything_in_chunks_and_fills_manifest():
    mock_statsbomb({(55, 282): [match(1, 14, has_360=True), match(2, 15), match(3, 16)]})
    writer = InMemoryWriter()

    stats = run_config(
        writer, sb_client(), single_target_config(chunk_size=2), None, batch_id="B1", today=TODAY
    )

    assert writer.manifest_writes == 2  # 3 partidos en bloques de 2
    assert set(writer.manifest) == {"match/1", "match/2", "match/3"}
    assert stats.inserted_by_table == {
        "statsbomb_events": 6,
        "statsbomb_lineups": 6,
        "statsbomb_three_sixty": 1,  # solo el partido con 360
    }
    assert stats.watermark_after == "2023-07-25T03:54:59"


@responses.activate
def test_second_run_downloads_nothing():
    mock_statsbomb({(55, 282): [match(1, 14), match(2, 15)]})
    writer = InMemoryWriter()
    run_config(writer, sb_client(), single_target_config(), None, batch_id="B1", today=TODAY)
    downloads_first = len(file_downloads())

    stats = run_config(
        writer, sb_client(), single_target_config(), None, batch_id="B2", today=TODAY
    )

    assert len(file_downloads()) == downloads_first  # solo se volvió a leer la lista de partidos
    assert stats.files_written == 0
    assert stats.records_inserted == 0


@responses.activate
def test_corrected_match_is_downloaded_again():
    mock_statsbomb({(55, 282): [match(1, 14), match(2, 15)]})
    writer = InMemoryWriter()
    run_config(writer, sb_client(), single_target_config(), None, batch_id="B1", today=TODAY)
    responses.replace(
        responses.GET,
        f"{SB_URL}/matches/55/282.json",
        json=[match(1, 14, updated="2026-10-01T10:00:00"), match(2, 15)],
    )

    stats = run_config(
        writer, sb_client(), single_target_config(), None, batch_id="B2", today=TODAY
    )

    assert stats.files_written == 2  # eventos + alineaciones del partido 1
    assert stats.records_inserted == 0  # mismos eventos: Bronze no duplica
    assert writer.manifest["match/1"].startswith("2026-10-01")


@responses.activate
def test_max_matches_per_run_limits_backlog():
    mock_statsbomb({(55, 282): [match(i, i) for i in range(1, 6)]})
    writer = InMemoryWriter()

    run_config(
        writer,
        sb_client(),
        single_target_config(max_matches_per_run=2),
        None,
        batch_id="B1",
        today=TODAY,
    )

    assert set(writer.manifest) == {"match/1", "match/2"}  # los más antiguos primero


@responses.activate
def test_statsbomb_full_loads_competitions_and_matches():
    responses.get(f"{SB_URL}/competitions.json", json=[{"competition_id": 55, "season_id": 282}])
    writer = InMemoryWriter()

    stats = run_config(
        writer, sb_client(), config("sb_competitions"), None, batch_id="B1", today=TODAY
    )

    assert stats.inserted_by_table == {"statsbomb_competitions": 1}
    assert writer.tables["statsbomb_competitions"][0]["record_key"] == "55|282"
