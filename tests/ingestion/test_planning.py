import json
from datetime import date

from src.ingestion.planning import (
    compute_window,
    mark_completed,
    parse_completed,
    pending_targets,
    target_key,
)

SEASON = {"season_start": date(2026, 8, 21), "season_end": date(2027, 5, 30)}


def window(watermark, today, lookback=7, lookahead=14):
    return compute_window(
        watermark=watermark,
        today=today,
        lookback_days=lookback,
        lookahead_days=lookahead,
        **SEASON,
    )


def test_first_run_starts_at_season_start():
    assert window(None, date(2026, 10, 5)) == (date(2026, 8, 21), date(2026, 10, 19))


def test_next_runs_look_back_from_watermark():
    # El margen hacia atrás vuelve a leer partidos recientes por si se corrigieron
    assert window(date(2026, 10, 5), date(2026, 10, 6)) == (date(2026, 9, 28), date(2026, 10, 20))


def test_window_is_clamped_to_season():
    start, end = window(date(2026, 8, 22), date(2027, 5, 25))
    assert start == date(2026, 8, 21)
    assert end == date(2027, 5, 30)


def test_window_never_inverts_after_season_end():
    start, end = window(date(2027, 6, 30), date(2027, 7, 1))
    assert start <= end


def test_pending_targets_skip_completed_but_always_refresh_current():
    targets = [
        {"competition": "PL", "season": 2024},
        {"competition": "PD", "season": 2024},
        {"competition": "PL", "season": "current"},
    ]
    completed = {target_key(targets[0])}

    assert pending_targets(targets, completed) == targets[1:]


def test_mark_completed_only_stores_closed_seasons():
    targets = [{"competition": "PL", "season": 2024}, {"competition": "PL", "season": "current"}]

    watermark = mark_completed(set(), targets)

    assert json.loads(watermark) == ["competition=PL|season=2024"]
    assert parse_completed(watermark) == {"competition=PL|season=2024"}
    assert parse_completed(None) == set()
