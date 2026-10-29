from journal.features.plans.states.following_plan import FollowingPlan
from journal.features.templates.shipped import PLAN_PHASE_TESTS
from journal.features.tasks.states.ready import Ready
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from tests.stories.fixtures.main.manual_draft_plan import ManualDraftPlan
from tests.stories.fixtures.state_fixture import StateFixture


class MidPhaseTestPlan(StateFixture):
    """The agent built the drafted plan into one phase of three tasks, the user set its testing to the phase ends and approved it, and the agent finished the first task, so the second is in hand mid-phase: story.plans.first, story.tasks.second and story.tasks.third."""

    stack = (Ready, FollowingPlan)

    parent = ManualDraftPlan

    def steps(self, story) -> None:
        story.agent_runs(story.agents.main, f"plan phase {self.plans.first} 'Pages' --when 'every page stands'")
        first_task = story.agent_adds_plan_task(story.agents.main, self.plans.first, "the grid")
        self.tasks.second = story.agent_adds_plan_task(story.agents.main, self.plans.first, "the about page")
        self.tasks.third = story.agent_adds_plan_task(story.agents.main, self.plans.first, "the footer")
        story.agent_runs(story.agents.main, f"plan todos {self.plans.first} 1 {first_task} {self.tasks.second} {self.tasks.third}")
        story.agent_runs(story.agents.main, f"plan ready {self.plans.first}")
        story.user_sets_plan_testing(self.plans.first, PLAN_PHASE_TESTS.title)
        story.user_approves_plan(self.plans.first)
        story.agent_runs(story.agents.main, f"plan start {self.plans.first}")
        story.agent_runs(story.agents.main, f"task complete {first_task} --how 'the grid stands'")

    def expected(self, story) -> None:
        story.expect_plan(self.plans.first, state=PlanState.STARTED)
        story.expect_task(self.tasks.second, state=TaskState.STARTED)
        story.expect_task(self.tasks.third, state=TaskState.OPEN)
        story.expect_stack(story.agents.main, Ready, FollowingPlan)
