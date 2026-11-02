from journal.engine.support.session_agents import SessionAgents
from journal.features.organization.support.seat_runtime import SeatMember
from journal.models.agent import Agent
from journal.models.environment import Environment
from journal.models.support.ref import Ref
from journal.repositories.agents import Agents
from journal.repositories.links import Links
from journal.support.actor import Actor

SEAT_AGENT_LINK = "organization_seat/"


class SeatAgentRows:
    """The stable agent row of an organization seat, linked to its environment by rig, provider and seat."""

    def __init__(self, agents: Agents, links: Links, sessions: SessionAgents) -> None:
        self.agents, self.links, self.sessions = agents, links, sessions

    def peer(self, parent: Agent, member: SeatMember, session: str) -> Agent:
        links = self.links.all_matching(target=Ref(Environment.table(), parent.environment_id), link_type=self.key(member))
        for link in reversed(links):
            rows = self.agents.global_matching(id=link.source.id, environment_id=parent.environment_id, provider=member.provider)
            if rows and rows[0].row_id != parent.row_id:
                return rows[0]
        return self.sessions.peer_row(parent, session, member.provider)

    def remember(self, agent: Agent, member: SeatMember) -> None:
        target, kind = Ref(Environment.table(), agent.environment_id), self.key(member)
        for link in self.links.all_matching(target=target, link_type=kind):
            if link.source != Ref.build(agent):
                self.links.delete(link, Actor.system())
        self.links.linked(Ref.build(agent), target, kind, Actor.system())

    def identity(self, agent: Agent) -> str:
        return next((link.link_type for link in self.links.all_matching(source=Ref.build(agent)) if link.link_type.startswith(SEAT_AGENT_LINK)), "")

    @staticmethod
    def key(member: SeatMember) -> str:
        return f"{SEAT_AGENT_LINK}{member.rig}/{member.provider}/{member.organization_seat}"
