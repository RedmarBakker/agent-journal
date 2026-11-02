from journal.features.organization.support.seat_runtime import SeatMember, SeatRuntime
from journal.repositories.agents import Agents
from journal.repositories.rigs import Rigs
from journal.support.supervisor_reply import SupervisorReply


class SeatLineDelivery:
    """Send the target agent's lines to its live organization seat by native session."""

    def __init__(self, agents: Agents, rigs: Rigs, runtime: SeatRuntime) -> None:
        self.agents, self.rigs, self.runtime = agents, rigs, runtime

    def send(self, agent_id: int, line: str) -> SupervisorReply | None:
        seat = self.seat(agent_id)
        if seat is None:
            return None
        self.runtime.send(seat, line)
        return SupervisorReply(True)

    def seat(self, agent_id: int) -> SeatMember | None:
        agent = self.agents.unended_agent(agent_id) if agent_id else None
        if agent is None:
            return None
        for rig in self.rigs.global_matching():
            identity = self.runtime.organization_seat_for_session(rig.name, agent.provider, agent.session)
            if identity:
                return self.runtime.organization_member(rig.name, identity, agent.provider)
        return None
