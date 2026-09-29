from datetime import date

import pytest

from src.clients.budget import BudgetExceededError, InMemoryBudget, LocalFileBudget


def test_in_memory_budget_stops_at_limit():
    budget = InMemoryBudget(limit=2)
    budget.consume()
    budget.consume()
    assert budget.remaining() == 0
    with pytest.raises(BudgetExceededError):
        budget.consume()


def test_local_file_budget_persists_between_instances(tmp_path):
    path = tmp_path / "budget.json"
    today = lambda: date(2026, 9, 29)  # noqa: E731

    LocalFileBudget(path, "api_football", daily_limit=100, today=today).consume(3)
    budget = LocalFileBudget(path, "api_football", daily_limit=100, today=today)

    assert budget.used() == 3
    assert budget.remaining() == 97


def test_local_file_budget_resets_on_new_day(tmp_path):
    path = tmp_path / "budget.json"
    LocalFileBudget(path, "api_football", 100, today=lambda: date(2026, 9, 29)).consume(50)

    budget = LocalFileBudget(path, "api_football", 100, today=lambda: date(2026, 9, 30))

    assert budget.used() == 0
    assert budget.remaining() == 100


def test_local_file_budget_respects_reserve(tmp_path):
    budget = LocalFileBudget(
        tmp_path / "b.json", "api_football", daily_limit=10, reserve=8, today=lambda: date.today()
    )
    budget.consume(2)
    with pytest.raises(BudgetExceededError):
        budget.consume()


def test_sync_used_never_goes_backwards(tmp_path):
    budget = LocalFileBudget(tmp_path / "b.json", "api_football", 100, today=lambda: date.today())
    budget.consume(5)

    budget.sync_used(3)
    assert budget.used() == 5

    budget.sync_used(12)
    assert budget.used() == 12


def test_sources_are_independent(tmp_path):
    path = tmp_path / "b.json"
    LocalFileBudget(path, "api_football", 100).consume(4)

    assert LocalFileBudget(path, "football_data", 100).used() == 0
    assert LocalFileBudget(path, "api_football", 100).used() == 4
