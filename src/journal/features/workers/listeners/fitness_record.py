from journal.events.agent.tool_finished import ToolFinished
from journal.events.agent_listener import AgentListener
from journal.features.workers.support.fitness_point import FitnessPoint
from journal.features.workers.support.fitness_scoring import FitnessScoring
from journal.models.agent_role import AgentRole
from journal.repositories.agents import Agents
from journal.repositories.entries import Entries
from journal.support.actor import Actor


class FitnessRecord(AgentListener[ToolFinished]):
    """After each tool use of the main agent, its fitness is scored as the status bar shows it and kept as a point of its timeline whenever the score, a gap or a measure differs from the point before."""

    def __init__(self, agents: Agents, scoring: FitnessScoring, entries: Entries) -> None:
        self.agents, self.scoring, self.entries = agents, scoring, entries

    def handle(self, event: ToolFinished) -> None:
        rows = [] if event.subagent else self.agents.session_rows(event.session)
        if not rows or rows[0].role != AgentRole.MAIN:
            return
        score = self.scoring.scored(rows[0])
        if score is None:
            return
        newest = self.entries.session_kind_newest(event.session, FitnessPoint.KIND, 1)
        if not newest:
            self.entries.save(FitnessPoint.first(score, event.time).entry(rows[0]), Actor.system())
            return
        before = FitnessPoint.parsed(newest[0].data)
        if not before.is_same(score):
            self.entries.save(before.following(score, event.time).entry(rows[0]), Actor.system())
