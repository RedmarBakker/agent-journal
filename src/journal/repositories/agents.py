from journal.support.researcher_session import ResearcherSession
from datetime import datetime

from journal.db.query import Query
from journal.models.agent import Agent
from journal.support.agent_role import AgentRole
from journal.support.missing_row import MissingRow
from journal.repositories.scoped_repository import ScopedRepository

# an agent ended sooner than this after it began never worked, so is no peer
PEER_SECONDS = 60

class Agents(ScopedRepository[Agent]):
    model = Agent

    def current(self) -> Agent | None:
        responsive = self.selected(self.unended_query().filter(role=AgentRole.MAIN).order_descending("id").limit(1))
        return responsive[0] if responsive else None

    def all_agents(self) -> list[Agent]:
        return self.global_matching()

    def queried_number(self, number: str) -> list[Agent]:
        return self.global_matching(id=int(number)) if number.isdigit() else []

    def main_agents(self) -> list[Agent]:
        return self.global_matching(role=AgentRole.MAIN)

    def ended_stacked_agent(self, environment_id: int, session: str, state_name: str) -> Agent | None:
        newest = self.selected_ids(self.ended_main_query(environment_id).filter_unequal("session", session).order_descending("id").limit(1))
        return next(iter(self.selected_globally(self.query().filter(id=newest[0]).filter_record("stack", state=state_name))), None) if newest else None

    def declined_agents(self) -> list[Agent]:
        return self.selected_globally(self.query().filter(paused_declined=True).order("id"))

    def stacked_main_agents(self, state_name: str) -> list[Agent]:
        return self.selected_globally(self.unended_query().filter(role=AgentRole.MAIN).filter_record("stack", state=state_name).order("id"))

    def active_session_agents(self, session: str) -> list[Agent]:
        return self.selected_globally(self.unended_query().filter(session=session).order("id")) if session else []

    def active_main_agents(self) -> list[Agent]:
        return self.selected_globally(self.unended_query().filter(role=AgentRole.MAIN).order("id"))

    def active_main_agent(self, session: str) -> Agent | None:
        rows = self.selected_globally(self.query().filter(role=AgentRole.MAIN, session=session).filter_unequal("state", "ended").order("id"))
        return rows[0] if rows else None

    def program_main_agents(self) -> list[Agent]:
        return [agent for agent in self.active_main_agents() if agent.has_program()]

    def active_agents(self) -> list[Agent]:
        return self.selected(self.unended_query().order("id"))

    def conversation_agents(self, count: int) -> list[Agent]:
        return [agent for agent in self.scoped() if agent.has_program() and agent.role == AgentRole.MAIN][-count:]

    def ended_main_query(self, environment_id: int) -> Query:
        return self.query().filter(environment_id=environment_id, role=AgentRole.MAIN, state="ended")

    def main_scoped(self, environment_id: int) -> list[Agent]:
        return self.selected_globally(self.unended_query().filter(environment_id=environment_id, role=AgentRole.MAIN).order("id"))

    def researchers(self, session: str) -> list[Agent]:
        return self.selected_globally(self.unended_query().filter(role=AgentRole.SUBAGENT).filter_prefix("session", ResearcherSession.joined(session, "")))

    def unended(self) -> list[Agent]:
        return self.selected_globally(self.unended_query().order("id"))

    def skill_debtors(self) -> list[Agent]:
        return self.selected_globally(self.unended_query().filter_unequal("skills_due", ()).order("id"))

    def unended_scoped(self, environment_id: int) -> list[Agent]:
        return self.selected_globally(self.unended_query().filter(environment_id=environment_id).order("id"))

    def unended_query(self) -> Query:
        return self.query().filter_unequal("state", "ended")

    def running_peers(self, agent: Agent) -> list[Agent]:
        if agent.role != AgentRole.MAIN:
            return []
        return self.selected_globally(self.query().filter(environment_id=agent.environment_id, role=AgentRole.MAIN, provider=agent.provider).filter_unequal("state", "ended").filter_unequal("session", agent.session).order("id"))

    def all_current(self) -> Agent | None:
        responsive = sorted(self.active_main_agents(), key=lambda item: item.update_time)
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
        return self.selected_globally(self.session_query(session))

    def environment_main_agent(self, environment_id: int) -> Agent | None:
        rows = self.selected_globally(self.query().filter(environment_id=environment_id, role=AgentRole.MAIN).order_descending("updated_at").limit(1))
        return rows[0] if rows else None

    def main_row(self, session: str) -> Agent | None:
        rows = self.session_rows(session)
        return rows[0] if rows and rows[0].role == AgentRole.MAIN else None

    def session_query(self, session: str) -> Query:
        return self.query().filter(session=session).order("id").limit(1)

    def recent_peer(self, session: str | None, start: datetime) -> Agent | None:
        lasting = self.query().filter_alternatives(self.query().filter_unequal("state", "ended"), self.query().filter_lasting("created_at", "updated_at", PEER_SECONDS))
        rows = self.selected(lasting.filter_unequal("session", session).filter_greater_equal("updated_at", start).order_descending("id").limit(1))
        return rows[0] if rows else None

    def _row_reads(self, row: Agent) -> list[Query]:
        return [self.session_query(row.session)]
