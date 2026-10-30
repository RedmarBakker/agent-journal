from pathlib import Path

from journal.engine.states.void import Void
from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.features.workers.organization_options import OrganizationOptions
from journal.features.workers.states.working_task import WorkingTask
from journal.features.plans.plans_options import PlansOptions
from journal.models.worker_state import WorkerState
from journal.support.agent_role import AgentRole
from tests.stories.fixtures.main.working_agent import WorkingAgent


class RolePeerWorkers(WorkingAgent):
    """Three workers with tasks in two domains; the alpha builder works while the alpha scout and beta reviewer are idle."""

    stack = (Ready, ExternalWait)
    settings = (
        (OrganizationOptions.FOLDER, str(Path(__file__).parents[1] / "main" / "organization_hub")),
        (PlansOptions.PLAN_AGENTS, True),
    )

    def steps(self, story) -> None:
        super().steps(story)
        self.tasks.first = story.agent_creates_briefed_task(story.agents.main, "alpha build", "- the alpha change is ready")
        self.tasks.second = story.agent_creates_briefed_task(story.agents.main, "alpha research", "- alpha research is ready")
        self.tasks.third = story.agent_creates_briefed_task(story.agents.main, "beta review", "- beta review is ready")
        self.workers.first = self.dispatch(story, "Ada Lovelace", self.tasks.first, "builder")
        self.workers.second = self.dispatch(story, "Grace Hopper", self.tasks.second, "scout")
        self.workers.third = self.dispatch(story, "Edsger Dijkstra", self.tasks.third, "reviewer")
        for worker in (story.agents.workers.first(), story.agents.workers.second(), story.agents.workers.third()):
            story.agent_starts_a_session(worker)
            story.agent_clocks_in(worker)
        for worker in (story.agents.workers.second(), story.agents.workers.third()):
            story.agent_runs(worker, f"worker report {worker} 'waiting for a task'")

    def dispatch(self, story, name: str, task: int, role: str) -> int:
        result = story.agent_runs(
            story.agents.main,
            f"worker dispatch '{name}' --task {task} --changes 'the files of its task' --tests 'Scoped tests' --role {role}",
        )
        result.expect_command_passed()
        return story.newest("workers")

    def expected(self, story) -> None:
        story.expect_stack(story.agents.main, Ready, ExternalWait)
        story.expect_worker(self.workers.first, role="builder", state=WorkerState.READY)
        story.expect_worker(self.workers.second, role="scout", state=WorkerState.REPORTED)
        story.expect_worker(self.workers.third, role="reviewer", state=WorkerState.REPORTED)
        story.expect_stack(story.agents.workers.first(), Void, WorkingTask)
