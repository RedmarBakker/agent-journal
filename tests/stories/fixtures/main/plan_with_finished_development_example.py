from datetime import datetime, timezone

from journal.features.tasks.states.ready import Ready
from journal.engine.clock import Clock
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.features.estimates.estimates_options import EstimatesOptions
from tests.stories.fixtures.main.domain_delivery_setup import setup_domain
from tests.stories.fixtures.main.report_sized_plan import ReportSizedPlan
from tests.stories.fixtures.state_fixture import StateFixture


class PlanWithFinishedDevelopmentExample(StateFixture):
    """The owner deployed a sized task from ReportSizedPlan and made a second draft plan for the builder."""

    stack = (Ready,)
    parent = ReportSizedPlan

    def steps(self, story) -> None:
        setup_domain(story, self, "l03-example-development", "development", {
            "criterion": "A successful production deployment of the committed revision.",
            "evidence": "production_deployment",
            "target": "production",
        })
        story.user_sets(EstimatesOptions.MODE, "report").expect_viewer_passed()
        sprint = story.user_presses("/journal/sprints", {
            "starts_on": story.local_moment(0).split(" ")[0], "timezone": "Europe/Amsterdam",
        })
        sprint.expect_viewer_passed()
        sprint_id = sprint.viewer_answer["id"]
        story.user_presses(f"/journal/sprints/{sprint_id}/plans", {
            "plan_id": self.plans.first,
        }).expect_viewer_passed()
        story.user_presses(f"/journal/sprints/{sprint_id}/start", {}).expect_viewer_passed()
        story.agent_runs(story.agents.main, f"plan ready {self.plans.first}").expect_command_passed()
        story.user_approves_plan(self.plans.first).expect_viewer_passed()
        story.agent_runs(story.agents.main, f"task start {self.tasks.first}").expect_command_passed()
        story.time_travel(seconds=3600)
        story.agent_runs(story.agents.main,
                         f"task complete {self.tasks.first} --how 'the release artifact is ready'").expect_command_passed()
        story.time_travel(seconds=3600)
        story.user_presses(f"/journal/plans/{self.plans.first}/delivery", {
            "action": "accept", "evidence": {
                "kind": "production_deployment", "source": "deployment pipeline", "reference": "release-l03",
                "artifact": "revision-l03", "environment": "production", "result": "succeeded",
                "task_ids": [self.tasks.first],
                "occurred_at": datetime.fromtimestamp(story.app.container.get(Clock).held_at, timezone.utc).isoformat(),
            },
        }).expect_viewer_passed()
        self.plans.second = story.user_creates_plan("next release", "the next release reaches production")

    def expected(self, story) -> None:
        story.expect_plan(self.plans.first, state=PlanState.FINISHED)
        story.expect_task(self.tasks.first, state=TaskState.COMPLETED, size=3)
        story.expect_stack(story.agents.main, Ready)
