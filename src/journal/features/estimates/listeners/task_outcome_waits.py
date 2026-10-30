from journal.events.agent.agent_event import AgentEvent
from journal.events.agent.wait_cleared import WaitCleared
from journal.events.agent.wait_request import WaitRequest
from journal.events.listener import Listener
from journal.repositories.scope import Scope
from journal.repositories.task_outcomes import TaskOutcomes


class TaskOutcomeWaits(Listener[AgentEvent]):
    """Records user waits that begin and end while an agent holds a task."""

    def __init__(self, outcomes: TaskOutcomes, scope: Scope) -> None:
        self.outcomes, self.scope = outcomes, scope

    def handle(self, event: AgentEvent) -> None:
        with self.scope.environment(event.environment_id):
            if isinstance(event, WaitRequest):
                self.outcomes.record_wait_request(event)
            elif isinstance(event, WaitCleared):
                self.outcomes.record_wait_cleared(event)
