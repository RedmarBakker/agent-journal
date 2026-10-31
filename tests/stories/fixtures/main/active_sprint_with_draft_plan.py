from journal.features.tasks.states.ready import Ready
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from tests.stories.fixtures.main.user_drafted_plan import UserDraftedPlan


class ActiveSprintWithDraftPlan(UserDraftedPlan):
    """An active sprint contains the user's draft plan and its original two tasks."""

    parent = UserDraftedPlan

    def steps(self, story) -> None:
        result = story.user_presses("/journal/sprints", {"starts_on": "2026-10-26", "timezone": "Europe/Amsterdam"})
        result.expect_viewer_passed()
        self.sprints.first = result.viewer_answer["id"]
        story.user_presses(f"/journal/sprints/{self.sprints.first}/plans", {"plan_id": self.plans.first}).expect_viewer_passed()
        story.user_presses(f"/journal/sprints/{self.sprints.first}/start", {}).expect_viewer_passed()
        sprint = story.user_opens(f"/journal/sprints/{self.sprints.first}")
        sprint.expect_viewer_shows("state", "active")

    def expected(self, story) -> None:
        story.expect_plan(self.plans.first, state=PlanState.DRAFT)
        story.expect_task(self.tasks.first, state=TaskState.OPEN)
        story.expect_task(self.tasks.second, state=TaskState.OPEN)
        story.expect_stack(story.agents.main, Ready)
