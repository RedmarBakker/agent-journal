from journal.events.agent.line_delivered import LineDelivered
from journal.events.agent_listener import AgentListener
from journal.repositories.agents import Agents
from journal.repositories.reminders import Reminders
from journal.repositories.scope import Scope
from journal.support.actor import Actor
from journal.features.memory.memory_nudges import MemoryNudges


class RepeatedReminderRecord(AgentListener[LineDelivered]):
    """A reminder with an interval records the moment and tool use it was sent, so its interval starts again from there."""

    def __init__(self, reminders: Reminders, agents: Agents, scope: Scope) -> None:
        self.reminders, self.agents, self.scope = reminders, agents, scope

    def handle(self, event: LineDelivered) -> None:
        if event.nudge != MemoryNudges.REMINDER_REPEATED.key:
            return
        tool_uses = self.agents.session_agent(event.session).tool_uses
        with self.scope.environment(event.environment_id):
            for reminder in self.reminders.matching(id=int(event.values["n"])):
                self.reminders.save(reminder.sent(event.time, tool_uses), Actor.system())
