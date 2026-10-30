from collections.abc import Iterable

from journal.support.caller import Caller
from tests.observation import Observation
from tests.simulation.agent_session import AgentSession
from tests.simulation.simulator import Simulator


class CoordinatorActor:
    """The main simulated agent starts every approved plan through the journal hooks and commands."""

    def __init__(self, simulator: Simulator) -> None:
        self.session = AgentSession(simulator, Caller.agent("main", "lab-coordinator", simulator.provider))

    def session_start(self) -> Observation:
        return self.session.session_start()

    @property
    def session_id(self) -> str:
        return self.session.caller.agent_session

    def start_plans(self, plan_ids: Iterable[int]) -> tuple[Observation, ...]:
        return tuple(self.session.command(["plan", "start", str(plan_id)]) for plan_id in plan_ids)
