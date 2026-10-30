from journal.features.tasks.states.ready import Ready
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from tests.stories.fixtures.main.enforced_draft_plan import EnforcedDraftPlan
from tests.stories.fixtures.state_fixture import StateFixture


class EnforcedDependencyPlan(StateFixture):
    """The owner enabled enforcement and the builder composed a sized, domain-scoped plan with a declared prerequisite."""

    stack = (Ready,)
    parent = EnforcedDraftPlan

    def steps(self, story) -> None:
        phase = story.agent_runs(story.agents.main, f"plan phase {self.plans.first} 'Delivery' --when 'production accepts the revision'")
        phase.expect_command_passed()
        first = story.agent_runs(story.agents.main, f"plan add {self.plans.first} 'build' --brief 'the artifact builds' --domain development --size 3 --phase 1")
        first.expect_command_passed()
        self.tasks.first = story.created_number("task")
        second = story.agent_runs(story.agents.main, f"plan add {self.plans.first} 'deploy' --brief 'the artifact is deployed' --domain development --size 5 --phase 1 --after {self.tasks.first} --reason 'deployment uses the built artifact'")
        second.expect_command_passed()
        self.tasks.second = story.created_number("task")

    def expected(self, story) -> None:
        story.expect_plan(self.plans.first, state=PlanState.DRAFT)
        story.expect_task(self.tasks.first, state=TaskState.OPEN, size=3)
        story.expect_task(self.tasks.second, state=TaskState.OPEN, size=5)
        story.expect_stack(story.agents.main, Ready)
