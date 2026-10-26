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


def test_a_plan_closed_on_the_card_stays_a_plan_and_the_agent_brings_it_back(app: App):
    plan = int(app.console().run(["plan", "create", "the floors", "--brief", "the floors are laid"], USER).text.split()[1].rstrip(":"))
    viewer(app, f"plans/{plan}/dismiss")
    closed = app.container.get(Plans).find(plan)
    assert closed.is_dismissed and closed.state.value == "draft", "the plan leaves the card and nothing else of it changes"
    output = app.console().run(["plan", "card", str(plan)], AGENT)
    assert output.code == 0 and not app.container.get(Plans).find(plan).is_dismissed, output.error
