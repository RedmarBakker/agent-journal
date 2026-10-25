from datetime import datetime, timedelta

from journal.db.query import Query
from journal.models.agent import Agent
from journal.models.agent_role import AgentRole
from journal.support.missing_row import MissingRow
from journal.repositories.scoped_repository import ScopedRepository


class Agents(ScopedRepository[Agent]):
    model = Agent

    def current(self) -> Agent | None:
        responsive = [item for item in self.scoped() if item.state != "ended" and item.role == AgentRole.MAIN]
        return responsive[-1] if responsive else None

    def all_agents(self) -> list[Agent]:
        return self.global_matching()

    def queried_number(self, number: str) -> list[Agent]:
        return self.global_matching(id=int(number)) if number.isdigit() else []

    def main_agents(self) -> list[Agent]:
        return self.global_matching(role=AgentRole.MAIN)

    def sequence_agents(self, environment_id: int) -> list[Agent]:
        return [agent for agent in self.global_matching(environment_id=environment_id) if agent.sequence_runs]

    def ended_sequence_agents(self, session: str) -> list[Agent]:
        return self.newest(self.query().filter(state="ended").filter_unequal("session", session).filter_unequal("sequence_runs", ()))

    def active_session_agents(self, session: str) -> list[Agent]:
        return [agent for agent in self.global_matching(session=session) if agent.state != "ended"] if session else []

    def active_main_agents(self) -> list[Agent]:
        return [agent for agent in self.main_agents() if agent.state != "ended"]

    def active_main_agent(self, session: str) -> Agent | None:
        rows = self.selected_globally(self.query().filter(role=AgentRole.MAIN, session=session).filter_unequal("state", "ended").order("id"))
        return rows[0] if rows else None

    def program_main_agents(self) -> list[Agent]:
        return [agent for agent in self.active_main_agents() if agent.has_program()]

    def active_agents(self) -> list[Agent]:
        return [agent for agent in self.scoped() if agent.state != "ended"]

    def conversation_agents(self, count: int) -> list[Agent]:
        return [agent for agent in self.scoped() if agent.has_program() and agent.role == AgentRole.MAIN][-count:]

    def ended_main_agents(self, environment_id: int) -> list[Agent]:
        return self.global_matching(environment_id=environment_id, role=AgentRole.MAIN, state="ended")

    def main_scoped(self, environment_id: int) -> list[Agent]:
        return [item for item in self.global_matching(environment_id=environment_id, role=AgentRole.MAIN) if item.state != "ended"]

    def unended(self) -> list[Agent]:
        return [item for item in self.global_matching() if item.state != "ended"]

    def unended_scoped(self, environment_id: int) -> list[Agent]:
        return [item for item in self.global_matching(environment_id=environment_id) if item.state != "ended"]

    def running_peers(self, agent: Agent) -> list[Agent]:
        if agent.role != AgentRole.MAIN:
            return []
        return self.selected_globally(self.query().filter(environment_id=agent.environment_id, role=AgentRole.MAIN, provider=agent.provider).filter_unequal("state", "ended").filter_unequal("session", agent.session).order("id"))

    def all_current(self) -> Agent | None:
        responsive = sorted((item for item in self.main_agents() if item.state != "ended"), key=lambda item: item.update_time)
        return responsive[-1] if responsive else None

    def with_state(self, name: str) -> list[Agent]:
        return self.matching(state=name)

    def global_state(self, name: str) -> list[Agent]:
        return self.global_matching(state=name)

    def session_roles(self, session: str) -> list[AgentRole]:
        return [agent.role for agent in self.global_matching(session=session)]

    def session_numbers(self, sessions: set[str]) -> dict[str, int]:
        return {agent.session: agent.row_id for agent in self.selected(self.query().filter_listed("session", sorted(sessions)))}

    def session_agent(self, session: str) -> Agent:
        rows = self.session_rows(session)
        if not rows:
            raise MissingRow(self.table, session)
        return rows[0]

    def session_rows(self, session: str) -> list[Agent]:
        """The session's agent, the first if two share it, or none."""
        return self.selected_globally(self.session_query(session))

    def session_query(self, session: str) -> Query:
        return self.query().filter(session=session).order("id").limit(1)

    def recent_peers(self, session: str | None, start: datetime) -> list[Agent]:
        recent = self.newest(self.query().filter_unequal("session", session).filter_greater_equal("updated_at", start))
        return [item for item in recent if not (item.state == "ended" and item.update_time - item.creation_time < timedelta(minutes=1))]

    def _row_reads(self, row: Agent) -> list[Query]:
        return [self.session_query(row.session)]
