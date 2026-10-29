"""A plan's mode, organization or solo: set by command and on the plan page while the plan is a draft or paused, shown by plan show, and refused while the plan runs."""

import pytest

from journal.app import App
from journal.models.plan_mode import PlanMode
from journal.models.plan_state import PlanState
from journal.repositories.plans import Plans
from journal.repositories.scope import Scope
from journal.support.actor import Actor
from journal.support.caller import Caller
from tests.in_process import posted
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


def test_a_plans_mode_is_set_while_it_is_a_draft_or_paused_and_refused_while_it_runs(app: App):
    plan = int(app.console().run(["plan", "create", "the floors", "--brief", "the floors are laid"], USER).text.split()[1].rstrip(":"))
    plans = app.container.get(Plans)
    assert plans.find(plan).mode == PlanMode.SOLO, "a new plan is solo"
    output = app.console().run(["plan", "mode", str(plan), "organization"], USER)
    assert output.code == 0 and plans.find(plan).mode == PlanMode.ORGANIZATION, output.error
    assert "mode: organization" in app.console().run(["plan", "show", str(plan)], AGENT).text, "plan show names the mode"
    plans.save(plans.find(plan).with_(state=PlanState.STARTED), Actor.system())
    refused = app.console().run(["plan", "mode", str(plan), "solo"], USER)
    assert refused.code != 0 and "never while it runs" in refused.error and plans.find(plan).mode == PlanMode.ORGANIZATION, "a running plan keeps its mode"
    status, answer = posted(app, f"/journal/plans/{plan}/mode", {"mode": "solo"}, {"X-Journal-Env": "main"})
    assert status == 409 and plans.find(plan).mode == PlanMode.ORGANIZATION, answer
    plans.save(plans.find(plan).with_(state=PlanState.PAUSED), Actor.system())
    assert viewer(app, f"plans/{plan}/mode", {"mode": "solo"})["mode"] == "solo", "the plan page sets the mode of a paused plan"
    status, answer = posted(app, f"/journal/plans/{plan}/mode", {"mode": "crew"}, {"X-Journal-Env": "main"})
    assert status == 409 and plans.find(plan).mode == PlanMode.SOLO, "a mode that is not organization or solo is refused"
