from src.exploration.json_profiler import (
    JsonProfiler,
    format_pct,
    json_type,
    render_markdown_table,
)


def profile_by_path(records, **kwargs):
    kwargs.setdefault("min_key_samples", 2)
    profiler = JsonProfiler(**kwargs)
    profiler.add_many(records)
    return {p.path: p for p in profiler.profiles()}


def test_json_type_distinguishes_bool_from_int():
    assert json_type(True) == "bool"
    assert json_type(1) == "int"
    assert json_type(None) == "null"
    assert json_type([]) == "array"


def test_nested_paths_and_lists():
    profiles = profile_by_path(
        [{"id": 1, "team": {"name": "Arsenal"}, "players": [{"id": 10}, {"id": 11}]}]
    )

    assert set(profiles) == {"id", "team", "team.name", "players", "players[]", "players[].id"}
    assert profiles["players[].id"].occurrences == 2
    assert profiles["players[]"].presence_pct is None


def test_presence_counts_missing_keys_against_parent():
    profiles = profile_by_path([{"id": 1, "coach": "A"}, {"id": 2}, {"id": 3}, {"id": 4}])

    assert profiles["id"].presence_pct == 100.0
    assert profiles["coach"].presence_pct == 25.0


def test_null_pct_and_mixed_types():
    profiles = profile_by_path([{"score": 1}, {"score": None}, {"score": 1.5}, {"score": None}])

    assert profiles["score"].null_pct == 50.0
    assert profiles["score"].types == ("float", "int", "null")


def test_candidate_key_requires_unique_complete_values():
    profiles = profile_by_path(
        [
            {"id": 1, "status": "FT", "ref": None},
            {"id": 2, "status": "FT", "ref": "x"},
            {"id": 3, "status": "NS", "ref": "y"},
        ]
    )

    assert profiles["id"].is_candidate_key
    assert not profiles["status"].is_candidate_key  # repetido
    assert not profiles["ref"].is_candidate_key  # tiene nulos


def test_nested_list_key_is_unique_across_records():
    profiles = profile_by_path([{"matches": [{"id": 1}, {"id": 2}]}, {"matches": [{"id": 3}]}])

    assert profiles["matches[].id"].is_candidate_key
    assert profiles["matches[].id"].distinct_count == 3


def test_small_samples_are_not_flagged_as_keys():
    profiles = profile_by_path([{"id": 1}, {"id": 2}, {"id": 3}], min_key_samples=10)

    assert not profiles["id"].is_candidate_key


def test_format_pct_keeps_extremes_visible():
    assert format_pct(0.0) == "0 %"
    assert format_pct(0.3) == "<1 %"
    assert format_pct(99.7) == ">99 %"
    assert format_pct(100.0) == "100 %"


def test_distinct_cap_marks_field_as_high_cardinality():
    profiles = profile_by_path([{"v": i} for i in range(20)], max_distinct=5)

    assert profiles["v"].distinct_capped
    assert profiles["v"].distinct_count is None
    assert not profiles["v"].is_candidate_key


def test_example_is_first_non_null_scalar():
    profiles = profile_by_path([{"name": None}, {"name": "Messi"}, {"name": "Xavi"}])

    assert profiles["name"].example == "Messi"


def test_markdown_escapes_pipes():
    profiler = JsonProfiler()
    profiler.add({"label": "a|b"})

    table = render_markdown_table(profiler.profiles())

    assert "`a\\|b`" in table
