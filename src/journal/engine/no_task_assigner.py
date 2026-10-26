from journal.engine.support.assignment import Assignment
from journal.events.agent.agent_event import AgentEvent
from journal.events.rows.row_event import RowEvent
from journal.models.agent import Agent


class NoTaskAssigner:
    """The assigner of a state that hands out nothing: a wait, the user's pause, a compaction, an ended session, a helper's floor."""

    def next_task(self, agent: Agent, event: AgentEvent | RowEvent) -> Assignment:
        return Assignment()
