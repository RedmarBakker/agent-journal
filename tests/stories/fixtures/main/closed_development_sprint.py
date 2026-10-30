from datetime import datetime
from zoneinfo import ZoneInfo

from journal.engine.clock import Clock
from journal.features.tasks.states.ready import Ready
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.models.worker_state import WorkerState
from tests.stories.fixtures.main.working_agent import WorkingAgent
from tests.stories.fixtures.main.domain_delivery_setup import setup_domain
from tests.stories.fixtures.state_fixture import StateFixture


class ClosedDevelopmentSprint(StateFixture):
    """The owner closed a missed development sprint after one planned task merged and before either task received production evidence."""

    stack = (Ready,)
    parent = WorkingAgent

    def steps(self, story) -> None:
        setup_domain(story, self, "w03-development", "development", {
            "criterion": "A successful production deployment of the committed revision.",
            "evidence": "production_deployment",
            "target": "production",
        })
        self.plans.first = story.user_creates_plan("release plan", "production accepts the release")
        self.tasks.first = self.plan_task(story, "built release", "the release artifact is built")
        self.tasks.second = self.plan_task(story, "remaining change", "the remaining change is complete")
        story.user_approves_plan(self.plans.first).expect_viewer_passed()
        self.sprints.first = self.start_sprint(story)
        self.workers.first = story.agent_dispatches_worker(story.agents.main, "Lady Lovelace", self.tasks.first)
        story.agent_starts_a_session(story.agents.workers.first())
        story.agent_clocks_in(story.agents.workers.first())
        story.agent_proves(story.agents.workers.first(), 1, "src/release.py:3, the release artifact is built")
        story.agent_clocks_out(story.agents.workers.first(), "the release artifact is built")
        story.agent_runs(story.agents.main, f"worker check {story.agents.workers.first()} 1 --task {self.tasks.first}").expect_command_passed()
        story.agent_runs(story.agents.main, f"worker merge {story.agents.workers.first()}").expect_command_passed()

    def expected(self, story) -> None:
        story.expect_plan(self.plans.first, state=PlanState.APPROVED)
        story.expect_task(self.tasks.first, state=TaskState.COMPLETED, size=3)
        story.expect_task(self.tasks.second, state=TaskState.OPEN, size=3)
        story.expect_worker(self.workers.first, state=WorkerState.MERGED)
        story.expect_stack(story.agents.main, Ready)

    def plan_task(self, story, title: str, brief: str) -> int:
        created = story.user_presses(f"/journal/plans/{self.plans.first}/tasks", {
            "title": title, "brief": f"- {brief}", "size": 3, "domain": "development",
        })
        created.expect_viewer_passed()
        return created.viewer_answer["id"]

    def start_sprint(self, story) -> int:
        started_on = datetime.fromtimestamp(story.app.container.get(Clock).held_at, ZoneInfo("Europe/Amsterdam")).date().isoformat()
        created = story.user_presses("/journal/sprints", {"starts_on": started_on, "timezone": "Europe/Amsterdam"})
        created.expect_viewer_passed()
        sprint = created.viewer_answer["id"]
        assigned = story.user_presses(f"/journal/sprints/{sprint}/plans", {"plan_id": self.plans.first})
        assigned.expect_viewer_passed()
        story.user_presses(f"/journal/sprints/{sprint}/start", {}).expect_viewer_passed()
        return sprint
