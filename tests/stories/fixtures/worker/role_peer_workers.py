from pathlib import Path

from journal.engine.states_catalogue import StatesCatalogue
from journal.engine.states.void import Void
from journal.features.plans.states.coordinating_plans import CoordinatingPlans
from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.features.workers.organization_options import OrganizationOptions
from journal.features.workers.states.working_task import WorkingTask
from journal.features.plans.plans_options import PlansOptions
from journal.models.worker_state import WorkerState
from journal.support.agent_role import AgentRole
from tests.stories.fixtures.main.working_agent import WorkingAgent


def awaiting_state(story):
    return story.app.container.get(StatesCatalogue).restored("awaiting", {})


class RolePeerWorkers(WorkingAgent):
    """An alpha builder works while another alpha Role is idle with a resumable session."""

    stack = (Ready, ExternalWait)
    peer_role = "maker"
    peer_task = "alpha research"
    settings = (
        (OrganizationOptions.FOLDER, str(Path(__file__).resolve().with_name("role_peer_org"))),
        (PlansOptions.PLAN_AGENTS, True),
    )

    def steps(self, story) -> None:
        super().steps(story)
        self.tasks.first = story.agent_creates_briefed_task(story.agents.main, "alpha build", "- the alpha change is ready")
        self.tasks.second = story.agent_creates_briefed_task(story.agents.main, self.peer_task, f"- {self.peer_task} is ready")
        self.workers.first = self.dispatch(story, "Ada Lovelace", self.tasks.first, "builder")
        self.workers.second = self.dispatch(story, "Grace Hopper", self.tasks.second, self.peer_role)
        for worker in (story.agents.workers.first(), story.agents.workers.second()):
            story.agent_starts_a_session(worker)
        story.agent_clocks_in(story.agents.workers.first())
        peer = story.agents.workers.second()
        story.worker_run_ends_with_its_session(peer, "waiting for a task")
        story.agent_runs(peer, f"worker report {peer} 'waiting for a task'").expect_command_passed()

    def dispatch(self, story, name: str, task: int, role: str) -> int:
        result = story.agent_runs(
            story.agents.main,
            f"worker dispatch '{name}' --task {task} --changes 'the files of its task' --tests 'Scoped tests' --role {role}",
        )
        result.expect_command_passed()
        return story.newest("workers")

    def expected(self, story) -> None:
        story.expect_stack(story.agents.main, CoordinatingPlans, awaiting_state(story))
        story.expect_worker(self.workers.first, role="builder", state=WorkerState.READY)
        story.expect_worker(self.workers.second, role=self.peer_role, state=WorkerState.REPORTED)
        story.expect_stack(story.agents.workers.first(), Void, WorkingTask)
