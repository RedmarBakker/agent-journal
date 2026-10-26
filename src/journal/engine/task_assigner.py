from typing import Protocol

from journal.engine.support.assignment import Assignment
from journal.events.agent.agent_event import AgentEvent
from journal.events.rows.row_event import RowEvent
from journal.models.agent import Agent


class TaskAssigner(Protocol):
    """Which task an agent takes next, asked by the engine at every event: the assigner decides whether the event is its moment, and starts the task it hands, or hands none."""

    def next_task(self, agent: Agent, event: AgentEvent | RowEvent) -> Assignment: ...
