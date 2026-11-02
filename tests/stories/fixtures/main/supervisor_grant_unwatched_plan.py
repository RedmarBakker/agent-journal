from journal.features.tasks.states.ready import Ready
from journal.models.plan import Plan
from journal.models.plan_state import PlanState
from journal.repositories.environments import Environments
from journal.repositories.plans import Plans
from journal.repositories.scope import Scope
from tests.stories.fixtures.main.supervisor_grant_cli_act import SupervisorGrantCliAct


class SupervisorGrantUnwatchedPlan(SupervisorGrantCliAct):
    """The supervisor has another started plan outside its watched plan list."""

    parent = SupervisorGrantCliAct

    def steps(self, story) -> None:
        environment = story.app.container.get(Environments).lookup(self.supervisor_environment)
        plans = story.app.container.get(Plans)
        scope = story.app.container.get(Scope)
        with scope.environment(environment.row_id):
            plan = plans.save(Plan(environment_id=environment.row_id, title="unwatched plan", state=PlanState.STARTED), self.supervisor_owner)
        self.plans.second = plan.row_id
        result = story.user_opens_in(self.supervisor_environment, f"/journal/plans/{plan.row_id}")
        result.expect_viewer_passed()

    def expected(self, story) -> None:
        story.expect_stack(story.agents.main, Ready)
