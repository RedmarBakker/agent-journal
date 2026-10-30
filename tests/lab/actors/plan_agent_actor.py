from collections.abc import Iterable, Mapping

from journal.models.plan_mode import PlanMode
from journal.support.caller import Caller
from tests.observation import Observation
from tests.simulation.agent_session import AgentSession
from tests.simulation.simulator import Simulator


class PlanAgentActor:
    """A simulated Plan agent works as one Role at a time in solo mode or hands tasks to Domains in organization mode."""

    def __init__(
        self,
        simulator: Simulator,
        plan_id: int,
        environment: str,
        mode: PlanMode,
        task_domains: Mapping[int, str],
        task_prerequisites: Mapping[int, tuple[int, ...]],
    ) -> None:
        if set(task_domains) != set(task_prerequisites):
            raise ValueError("every scenario task needs its domain and prerequisites")
        self.mode, self.task_domains = mode, tuple(task_domains.items())
        self.task_prerequisites = dict(task_prerequisites)
        self.active_role = ""
        self.session = AgentSession(simulator, Caller.agent(environment, f"lab-plan-{plan_id}", simulator.provider))

    @property
    def session_id(self) -> str:
        return self.session.caller.agent_session

    def session_start(self) -> Observation:
        return self.session.session_start()

    def take_role(self, role_id: str) -> Observation:
        if self.active_role:
            raise RuntimeError("a Plan agent works as one Role at a time")
        result = self.session.command(["role", "take", role_id])
        if self.command_succeeded(result):
            self.active_role = role_id
        return result

    def finish_role(self) -> Observation:
        if not self.active_role:
            raise RuntimeError("a Plan agent has no Role step in progress")
        result = self.session.command(["role", "done"])
        if self.command_succeeded(result):
            self.active_role = ""
        return result

    def handoffs(self, completed_tasks: Iterable[int] = ()) -> tuple[tuple[int, str], ...]:
        if self.mode is not PlanMode.ORGANIZATION:
            raise RuntimeError("only an organization Plan agent hands tasks to Domains")
        completed = frozenset(completed_tasks)
        return tuple(
            (task_id, domain)
            for task_id, domain in self.task_domains
            if set(self.task_prerequisites[task_id]) <= completed
        )

    @staticmethod
    def command_succeeded(result: Observation) -> bool:
        return isinstance(result.answer, tuple) and bool(result.answer) and result.answer[0] == 0
