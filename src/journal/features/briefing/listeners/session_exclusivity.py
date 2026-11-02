from journal.events.agent.session_started import SessionStarted
from journal.events.agent_listener import AgentListener
from journal.features.organization.support.seat_agent_rows import SeatAgentRows
from journal.repositories.agents import Agents
from journal.support.actor import Actor
from journal.support.decision import Decision


class SessionExclusivity(AgentListener[SessionStarted]):
    """Keeps one main session per provider and environment, allowing distinct organization seats to run together."""

    def __init__(self, agents: Agents, seats: SeatAgentRows) -> None:
        self.agents, self.seats = agents, seats

    def handle(self, event: SessionStarted) -> Decision | None:
        if event.subagent:
            return None
        current = self.agents.newest_row(event.agent)
        identity = self.seats.identity(current)
        for counterpart in self.agents.running_peers(current):
            peer_identity = self.seats.identity(counterpart)
            if identity and peer_identity and identity != peer_identity:
                continue
            self.agents.save(counterpart.retired(event.time), Actor.system())
        return None
