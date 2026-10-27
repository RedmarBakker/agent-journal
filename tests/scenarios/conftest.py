import pytest

from tests.replay import PROVIDERS, catch_typed
from tests.scenario_builder.scenario import Scenario
from tests.test_features import booted


@pytest.fixture(scope="module")
def boot():
    return booted


@pytest.fixture(params=PROVIDERS)
def scenario(app, monkeypatch, request) -> Scenario:
    """A story played for each provider in turn on the module's journal, lines typed to the agent caught and seen back at once."""
    catch_typed(app, monkeypatch, [])
    return Scenario(app, request.param)
