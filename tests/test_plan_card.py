"""The plan card above the chat: the user closes a plan there and it stays in the plans list, and the agent brings it back to the card on request."""

import pytest

from journal.app import App
from journal.repositories.plans import Plans
from journal.repositories.scope import Scope
from journal.support.caller import Caller
from tests.test_features import booted, hook, viewer

AGENT = Caller.agent("main", "s1", "claude")
USER = Caller.user("main")
MAIN = 1


@pytest.fixture(scope="module")
def boot():
    return booted


@pytest.fixture
def app(app: App):
    with app.container.get(Scope).environment(MAIN):
        hook(app, "SessionStart")
        app.console().run(["environment", "overview"], AGENT)
        yield app


