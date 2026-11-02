from journal.features.organization.support.seat_runtime import SeatRuntime
from journal.repositories.agents import Agents
from journal.repositories.rigs import Rigs
from journal.repositories.scope import Scope
from journal.support.supervisor_reply import SupervisorReply


class SeatLineDelivery:
    """Send an environment's lines to its live organization seat by native session."""

    def __init__(self, agents: Agents, rigs: Rigs, scope: Scope, runtime: SeatRuntime) -> None:
        self.agents, self.rigs, self.scope, self.runtime = agents, rigs, scope, runtime

    def send(self, environment_id: int, line: str) -> SupervisorReply | None:
        rigs = self.rigs.global_matching()
        if not rigs:
            return None
        with self.scope.environment(environment_id):
            agent = self.agents.current()
            if agent is None:
                return None
            for rig in rigs:
                identity = self.runtime.organization_seat_for_session(rig.name, agent.provider, agent.session)
                if identity:
                    seat = self.runtime.organization_member(rig.name, identity, agent.provider)
                    self.runtime.send(seat, line)
                    return SupervisorReply(True)
        return None
