import json

import pytest

from src.ingestion.control import CONTROL_TABLES_DDL
from src.ingestion.source_config import (
    LOAD_TYPES,
    SOURCE_CONFIGS,
    SourceConfig,
    config_rows,
    validate,
)


def test_config_rows_are_valid_and_serializable():
    rows = config_rows()

    assert len(rows) == len(SOURCE_CONFIGS)
    for row in rows:
        assert row["load_type"] in LOAD_TYPES
        json.loads(row["params"])  # params debe ser JSON válido


def test_config_ids_are_unique():
    ids = [c.config_id for c in SOURCE_CONFIGS]
    assert len(ids) == len(set(ids))


def test_validate_rejects_duplicates_and_unknown_load_types():
    dup = SourceConfig("x", "s", "e", "full", 1, "d")
    with pytest.raises(ValueError, match="duplicados"):
        validate([dup, dup])
    with pytest.raises(ValueError, match="load_type"):
        validate([SourceConfig("y", "s", "e", "otro", 1, "d")])


def test_api_football_targets_respect_free_plan_and_priority():
    af = [c for c in SOURCE_CONFIGS if c.source == "api_football"]
    for config in af:
        seasons = {t["season"] for t in config.params["targets"]}
        assert seasons <= {2022, 2023, 2024}  # el plan gratuito solo cubre 2022-2024
        # ADR-005: el relleno empieza por la Euro 2024 (liga 4)
        assert config.params["targets"][0]["league"] == 4


def test_every_control_table_has_idempotent_ddl():
    expected = {
        "ctl_source_config",
        "ctl_watermark",
        "ctl_run_log",
        "ctl_api_budget",
        "ctl_file_manifest",
    }
    assert set(CONTROL_TABLES_DDL) == expected
    for name, ddl in CONTROL_TABLES_DDL.items():
        assert f"CREATE TABLE IF NOT EXISTS {name}" in ddl
