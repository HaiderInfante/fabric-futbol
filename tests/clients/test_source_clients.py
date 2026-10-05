from datetime import date

import pytest
import responses

from src.clients.api_football import DEFAULT_BASE_URL as AF_URL
from src.clients.api_football import ApiFootballClient, ApiFootballError
from src.clients.budget import InMemoryBudget, LocalFileBudget
from src.clients.football_data import DEFAULT_BASE_URL as FD_URL
from src.clients.football_data import FootballDataClient
from src.clients.statsbomb import DEFAULT_BASE_URL as SB_URL
from src.clients.statsbomb import StatsBombClient


def no_sleep(_: float) -> None:
    pass


# --- football-data.org -------------------------------------------------------------------------


@responses.activate
def test_football_data_sends_token_and_skips_empty_params():
    responses.get(f"{FD_URL}/competitions/PL/matches", json={"matches": []})
    client = FootballDataClient("key-fd", sleep=no_sleep)

    client.matches("PL", season=2026)

    request = responses.calls[0].request
    assert request.headers["X-Auth-Token"] == "key-fd"
    assert request.url.endswith("/competitions/PL/matches?season=2026")


@responses.activate
def test_football_data_waits_for_counter_reset_on_429():
    responses.get(f"{FD_URL}/competitions", status=429, headers={"X-RequestCounter-Reset": "13"})
    responses.get(f"{FD_URL}/competitions", json={"competitions": []})
    sleeps: list[float] = []
    client = FootballDataClient("key-fd", sleep=sleeps.append)

    client.competitions()

    assert sleeps == [13.0]


# --- API-Football ------------------------------------------------------------------------------


def af_payload(response, *, errors=None, current=1, total=1):
    return {
        "get": "x",
        "parameters": {},
        "errors": errors if errors is not None else [],
        "results": len(response),
        "paging": {"current": current, "total": total},
        "response": response,
    }


@responses.activate
def test_api_football_raises_on_errors_in_http_200():
    plan_error = {"plan": "Free plans do not have access to this season."}
    responses.get(f"{AF_URL}/standings", json=af_payload([], errors=plan_error))
    client = ApiFootballClient("key-af", sleep=no_sleep)

    with pytest.raises(ApiFootballError) as exc_info:
        client.standings(league=39, season=2026)

    assert exc_info.value.errors == plan_error
    assert responses.calls[0].request.headers["x-apisports-key"] == "key-af"


@responses.activate
def test_api_football_status_does_not_consume_budget():
    status = {"requests": {"current": 7, "limit_day": 100}}
    responses.get(f"{AF_URL}/status", json=af_payload(status))
    budget = InMemoryBudget(limit=0)
    client = ApiFootballClient("key-af", budgets=[budget], sleep=no_sleep)

    assert client.status() == status


@responses.activate
def test_api_football_sync_budget_uses_provider_count(tmp_path):
    status = {"requests": {"current": 42, "limit_day": 100}}
    responses.get(f"{AF_URL}/status", json=af_payload(status))
    budget = LocalFileBudget(tmp_path / "b.json", "api_football", 100, today=lambda: date.today())
    client = ApiFootballClient("key-af", budgets=[budget], sleep=no_sleep)

    client.sync_budget(budget)

    assert budget.used() == 42


@responses.activate
def test_api_football_syncs_daily_budget_from_headers():
    quota = {"x-ratelimit-requests-limit": "100", "x-ratelimit-requests-remaining": "60"}
    responses.get(f"{AF_URL}/teams", json=af_payload([]), headers=quota)
    daily = InMemoryBudget(limit=90, name="daily", used=5)
    run_cap = InMemoryBudget(limit=10, name="run")
    client = ApiFootballClient("key-af", daily_budget=daily, budgets=[run_cap], sleep=no_sleep)

    client.teams(league=39, season=2024)

    assert client.provider_used == 40
    assert daily.used == 40  # el proveedor manda: 100 - 60
    assert run_cap.used == 1  # el tope por ejecución no se sincroniza


@responses.activate
def test_api_football_header_sync_never_goes_backwards():
    quota = {"x-ratelimit-requests-limit": "100", "x-ratelimit-requests-remaining": "99"}
    responses.get(f"{AF_URL}/teams", json=af_payload([]), headers=quota)
    daily = InMemoryBudget(limit=90, name="daily", used=30)
    client = ApiFootballClient("key-af", daily_budget=daily, sleep=no_sleep)

    client.teams(league=39, season=2024)

    assert daily.used == 31  # 30 previas + esta llamada; el header (1) va por detrás


@responses.activate
def test_api_football_get_all_pages_follows_paging():
    responses.get(f"{AF_URL}/players", json=af_payload([1, 2], current=1, total=3))
    responses.get(f"{AF_URL}/players", json=af_payload([3], current=2, total=3))
    responses.get(f"{AF_URL}/players", json=af_payload([4], current=3, total=3))
    client = ApiFootballClient("key-af", sleep=no_sleep)

    result = client.get_all_pages("players", {"league": 39, "season": 2024})

    assert result == [1, 2, 3, 4]
    assert [call.request.params["page"] for call in responses.calls] == ["1", "2", "3"]


@responses.activate
def test_api_football_get_all_pages_respects_max_pages():
    responses.get(f"{AF_URL}/players", json=af_payload([1], current=1, total=5))
    responses.get(f"{AF_URL}/players", json=af_payload([2], current=2, total=5))
    client = ApiFootballClient("key-af", sleep=no_sleep)

    assert client.get_all_pages("players", max_pages=2) == [1, 2]
    assert len(responses.calls) == 2


# --- StatsBomb ---------------------------------------------------------------------------------


@responses.activate
def test_statsbomb_three_sixty_returns_none_when_missing():
    responses.get(f"{SB_URL}/three-sixty/123.json", status=404)
    client = StatsBombClient(sleep=no_sleep)

    assert client.three_sixty(123) is None


@responses.activate
def test_statsbomb_matches_path():
    responses.get(f"{SB_URL}/matches/11/90.json", json=[{"match_id": 1}])
    client = StatsBombClient(sleep=no_sleep)

    assert client.matches(11, 90) == [{"match_id": 1}]
