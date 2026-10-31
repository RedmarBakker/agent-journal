from journal.features.tasks.states.ready import Ready
from journal.features.estimates.estimates_options import EstimatesOptions
from tests.stories.fixtures.main.domain_delivery_setup import setup_domain
from tests.stories.fixtures.main.working_agent import WorkingAgent
from tests.stories.fixtures.state_fixture import StateFixture


class PlanWithFinishedDevelopmentExample(StateFixture):
    """The owner has one production-delivered, sized development task and a second draft plan for the builder."""

    stack = (Ready,)
    parent = WorkingAgent

    def steps(self, story) -> None:
        setup_domain(story, self, "l03-example-development", "development", {
            "criterion": "A successful production deployment of the committed revision.",
            "evidence": "production_deployment",
            "target": "production",
        })
        self.plans.first = story.user_creates_plan("finished release", "the release reaches production")
        self.tasks.first = story.user_adds_plan_task(self.plans.first, "deploy the release")
        story.user_presses(f"/journal/tasks/{self.tasks.first}/domain", {
            "domain": "development", "kind": "planned", "reason": "the release is owned by development",
        }).expect_viewer_passed()
        story.user_presses(f"/journal/tasks/{self.tasks.first}/size", {
            "size": 3, "reason": "the original relative size",
        }).expect_viewer_passed()
        sprint = story.user_presses("/journal/sprints", {
            "start": story.local_moment(0), "timezone": "Europe/Amsterdam",
        })
        sprint.expect_viewer_passed()
        story.user_presses(f"/journal/sprints/{sprint.viewer_answer['id']}/plans", {
            "plan": self.plans.first,
        }).expect_viewer_passed()
        story.user_presses(f"/journal/sprints/{sprint.viewer_answer['id']}/start", {}).expect_viewer_passed()
        story.agent_runs(story.agents.main, f"plan ready {self.plans.first}").expect_command_passed()
        story.user_approves_plan(self.plans.first)
        self.workers.first = story.agent_dispatches_worker_on_plan(story.agents.main, "Lady Lovelace", self.plans.first)
        story.agent_starts_a_session(story.agents.workers.first())
        story.agent_clocks_in(story.agents.workers.first())
        story.time_travel(seconds=3600)
        story.agent_proves(story.agents.workers.first(), 1, "release.py:3, the production artifact is ready")
        story.agent_clocks_out(story.agents.workers.first(), "the production artifact is ready")
        story.agent_runs(story.agents.main, f"worker check {self.workers.first} 1 --task {self.tasks.first}")
        story.agent_runs(story.agents.main, f"worker merge {self.workers.first}")
        story.time_travel(seconds=3600)
        story.user_presses(f"/journal/plans/{self.plans.first}/delivery", {
            "kind": "production_deployment", "source": "deployment-l03", "artifact": "revision-l03",
            "environment": "production", "scope": [self.tasks.first], "succeeded": True,
        }).expect_viewer_passed()
        self.plans.second = story.user_creates_plan("next release", "the next release reaches production")
        story.user_sets(EstimatesOptions.MODE, "report").expect_viewer_passed()

    def expected(self, story) -> None:
        story.expect_stack(story.agents.main, Ready)
