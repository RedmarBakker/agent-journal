from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.templates.shipped import PLAN_PHASE_TESTS
from journal.features.tasks.states.ready import Ready
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from tests.stories.fixtures.main.manual_draft_plan import ManualDraftPlan
from tests.stories.fixtures.state_fixture import StateFixture


class MidPhaseTestPlan(StateFixture):
    """The agent built the drafted plan into one phase of three tasks, the user set its testing to the phase ends and approved it, and the agent finished the first task, so the second is in hand mid-phase: start.plan, start.second_task and start.third_task."""

    stack = (Ready, FollowingPlan)

    parent = ManualDraftPlan

    def steps(self, story) -> None:
        story.agent_runs(f"plan phase {self.plan} 'Pages' --when 'every page stands'")
        first_task = story.agent_adds_plan_task(self.plan, "the grid")
        self.second_task = story.agent_adds_plan_task(self.plan, "the about page")
        self.third_task = story.agent_adds_plan_task(self.plan, "the footer")
        story.agent_runs(f"plan todos {self.plan} 1 {first_task} {self.second_task} {self.third_task}")
        story.agent_runs(f"plan ready {self.plan}")
        story.user_sets_plan_testing(self.plan, PLAN_PHASE_TESTS.title)
        story.user_approves_plan(self.plan)
        story.agent_runs(f"plan start {self.plan}")
        story.agent_runs(f"task complete {first_task} --how 'the grid stands'")

    def expected(self, story) -> None:
        story.expect_plan(self.plan, state=PlanState.STARTED)
        story.expect_task(self.second_task, state=TaskState.STARTED)
        story.expect_task(self.third_task, state=TaskState.OPEN)
        story.expect_stack(Ready, FollowingPlan)
