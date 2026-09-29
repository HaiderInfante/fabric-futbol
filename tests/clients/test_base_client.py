import pytest
import requests
import responses

from src.clients.base_client import ApiClient, ApiError, RateLimiter
from src.clients.budget import BudgetExceededError, InMemoryBudget

BASE_URL = "https://api.example.com/v1"


class FakeClock:
    def __init__(self) -> None:
        self.now = 0.0
        self.sleeps: list[float] = []

    def __call__(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.now += seconds


def make_client(**kwargs) -> tuple[ApiClient, list[float]]:
    sleeps: list[float] = []
    client = ApiClient(BASE_URL, sleep=sleeps.append, backoff_base_seconds=1.0, **kwargs)
    return client, sleeps


# --- RateLimiter -----------------------------------------------------------------------------


def test_rate_limiter_allows_burst_then_waits():
    clock = FakeClock()
    limiter = RateLimiter(max_calls=3, period_seconds=60, clock=clock, sleep=clock.sleep)

    for _ in range(3):
        limiter.acquire()
    assert clock.sleeps == []

    limiter.acquire()
    assert clock.sleeps == [60]


def test_rate_limiter_does_not_wait_after_window_expires():
    clock = FakeClock()
    limiter = RateLimiter(max_calls=2, period_seconds=60, clock=clock, sleep=clock.sleep)
    limiter.acquire()
    limiter.acquire()

    clock.now = 61
    limiter.acquire()

    assert clock.sleeps == []


# --- ApiClient ---------------------------------------------------------------------------------


@responses.activate
def test_get_json_returns_payload_and_sends_headers():
    responses.get(f"{BASE_URL}/items", json={"ok": True})
    client, _ = make_client(headers={"X-Key": "secreto"})

    assert client.get_json("/items") == {"ok": True}
    assert responses.calls[0].request.headers["X-Key"] == "secreto"


@responses.activate
def test_retries_on_5xx_and_then_succeeds():
    responses.get(f"{BASE_URL}/items", status=503)
    responses.get(f"{BASE_URL}/items", status=502)
    responses.get(f"{BASE_URL}/items", json={"ok": True})
    client, sleeps = make_client()

    assert client.get_json("items") == {"ok": True}
    assert len(responses.calls) == 3
    # Backoff exponencial con base 1 s: 1 s y 2 s, más un jitter de hasta 1 s
    assert 1 <= sleeps[0] <= 2
    assert 2 <= sleeps[1] <= 3


@responses.activate
def test_honors_retry_after_header_on_429():
    responses.get(f"{BASE_URL}/items", status=429, headers={"Retry-After": "7"})
    responses.get(f"{BASE_URL}/items", json={})
    client, sleeps = make_client()

    client.get("items")

    assert sleeps == [7.0]


@responses.activate
def test_does_not_retry_on_4xx():
    responses.get(f"{BASE_URL}/items", status=403, body="forbidden")
    client, sleeps = make_client()

    with pytest.raises(ApiError) as exc_info:
        client.get("items")

    assert exc_info.value.status_code == 403
    assert len(responses.calls) == 1
    assert sleeps == []


@responses.activate
def test_raises_after_exhausting_retries():
    responses.get(f"{BASE_URL}/items", status=500)
    client, sleeps = make_client(max_retries=2)

    with pytest.raises(ApiError) as exc_info:
        client.get("items")

    assert exc_info.value.status_code == 500
    assert len(responses.calls) == 3
    assert len(sleeps) == 2


@responses.activate
def test_retries_on_connection_error():
    responses.get(f"{BASE_URL}/items", body=requests.ConnectionError("caída"))
    responses.get(f"{BASE_URL}/items", json={"ok": True})
    client, sleeps = make_client()

    assert client.get_json("items") == {"ok": True}
    assert len(sleeps) == 1


@responses.activate
def test_budget_blocks_call_before_hitting_the_api():
    responses.get(f"{BASE_URL}/items", json={})
    budget = InMemoryBudget(limit=1)
    client, _ = make_client(budgets=[budget])

    client.get("items")
    with pytest.raises(BudgetExceededError):
        client.get("items")

    assert len(responses.calls) == 1


@responses.activate
def test_each_retry_consumes_budget():
    responses.get(f"{BASE_URL}/items", status=500)
    responses.get(f"{BASE_URL}/items", json={})
    budget = InMemoryBudget(limit=10)
    client, _ = make_client(budgets=[budget])

    client.get("items")

    assert budget.used == 2


@responses.activate
def test_exhausted_budget_is_not_charged_on_others():
    responses.get(f"{BASE_URL}/items", json={})
    daily = InMemoryBudget(limit=10, name="daily")
    run = InMemoryBudget(limit=0, name="run")
    client, _ = make_client(budgets=[daily, run])

    with pytest.raises(BudgetExceededError):
        client.get("items")

    assert daily.used == 0


@responses.activate
def test_consume_budget_false_skips_budget():
    responses.get(f"{BASE_URL}/status", json={})
    budget = InMemoryBudget(limit=0)
    client, _ = make_client(budgets=[budget])

    client.get("status", consume_budget=False)

    assert len(responses.calls) == 1
