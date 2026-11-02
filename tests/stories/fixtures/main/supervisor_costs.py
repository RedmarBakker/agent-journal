from journal.models.plan import Plan
from journal.models.plan_mode import PlanMode
from journal.models.plan_state import PlanState
from journal.repositories.environments import Environments
from journal.repositories.plans import Plans
from journal.repositories.scope import Scope
from journal.support.actor import Actor
from journal.support.time_source import TimeSource
from journal.features.plans.support.plan_owners import PlanOwners
from journal.supervisor_authority import SupervisorAuthority
from tests.agent_hooks import story_seconds
from tests.stories.fixtures.main.supervisor_cost_data import add_quiet, add_run
from tests.stories.fixtures.supervisor.version_one_grant import VersionOneGrant


class SupervisorCosts(VersionOneGrant):
    """Known and unknown run costs span several plans and days."""

    parent = VersionOneGrant

    def steps(self, story) -> None:
        authority = story.app.container.get(SupervisorAuthority)
        principal = authority.authenticate(self.supervisor_credential)
        plan = story.app.container.get(Plans).global_matching(id=story.plans.first)[0]
        owner = story.app.container.get(PlanOwners).number(plan)
        with story.app.container.get(Scope).environment(plan.environment_id):
            second = story.app.container.get(Plans).save(
                Plan(title="Other plan", brief="Cost data for another plan", state=PlanState.STARTED,
                     mode=PlanMode.SOLO), Actor.user(owner),
            )
        self.plans.second = second.row_id
        now = story_seconds(story.app)
        source = story.app.container.get(TimeSource)
        add_run(story, principal, plan.row_id, "month", now - 14 * 86400, "0.50", ("check_interval",))
        add_run(story, principal, plan.row_id, "week", now - 6 * 86400, "0.10", ("check_interval",), True)
        add_run(story, principal, plan.row_id, "yesterday", now - 86400, "0.30",
                ("check_interval", "diagnostic_task"), True)
        add_run(story, principal, plan.row_id, "unknown", now - 3600, None, ("diagnostic_task",))
        add_run(story, principal, second.row_id, "other-plan", now - 2 * 86400, "0.20",
                ("diagnostic_task",))
        add_quiet(story, principal, plan.row_id, "one", now - 7200)
        add_quiet(story, principal, plan.row_id, "two", now - 3600)
        source.pin(now)
        result = story.user_opens_in(
            story.app.container.get(Environments).find(plan.environment_id).name,
            "/journal/supervisor/costs",
        )
        result.expect_viewer_passed()
