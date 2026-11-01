from datetime import datetime, timezone

from journal.engine.clock import Clock
from journal.features.tasks.states.ready import Ready
from journal.models.plan_mode import PlanMode
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from tests.stories.fixtures.main.domain_delivery_setup import merge_worker, setup_domain
from tests.stories.fixtures.main.report_sized_plan import ReportSizedPlan
from tests.stories.fixtures.state_fixture import StateFixture


class PlanWithFinishedDevelopmentExample(StateFixture):
    """The owner accepted delivery of a domain task in a solo plan and made a second solo plan."""

    stack = (Ready,)
    parent = ReportSizedPlan

    def steps(self, story) -> None:
        setup_domain(story, self, "l03-example-development", "development", {
            "criterion": "A successful production deployment of the committed revision.",
            "evidence": "production_deployment",
            "target": "production",
        })
        story.user_approves_plan(self.plans.first).expect_viewer_passed()
        self.workers.first = story.agent_dispatches_worker_on_plan(story.agents.main, "Lady Lovelace", self.plans.first)
        worker = story.agents.workers.first()
        story.agent_starts_a_session(worker)
        story.agent_clocks_in(worker)
        story.time_travel(seconds=3600)
        story.agent_proves(worker, 1, "src/release.py:4, the production artifact is ready")
        story.agent_clocks_out(worker, "the production artifact is ready")
        merge_worker(story)
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
        story.agent_runs(story.agents.main, f"plan mode {self.plans.second} solo").expect_command_passed()

    def expected(self, story) -> None:
        story.expect_plan(self.plans.first, state=PlanState.FINISHED, mode=PlanMode.SOLO)
        story.expect_task(self.tasks.first, state=TaskState.COMPLETED, size=3)
        story.expect_plan(self.plans.second, state=PlanState.DRAFT, mode=PlanMode.SOLO)
        story.expect_stack(story.agents.main, Ready)
