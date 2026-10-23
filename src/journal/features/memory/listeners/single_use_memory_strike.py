from journal.events.agent.line_delivered import LineDelivered
from journal.events.agent_listener import AgentListener
from journal.repositories.facts import Facts
from journal.repositories.reminders import Reminders
from journal.repositories.rules import Rules
from journal.repositories.scope import Scope
from journal.support.actor import Actor


class SingleUseMemoryStrike(AgentListener[LineDelivered]):
    """A fact, rule or reminder made for one use is struck once its moment has brought it to the agent, so it is brought once."""

    def __init__(self, facts: Facts, rules: Rules, reminders: Reminders, scope: Scope) -> None:
        self.repositories, self.scope = {"fact": facts, "rule": rules, "reminder": reminders}, scope

    def handle(self, event: LineDelivered) -> None:
        from journal.features.memory.feature import Memory
        if event.nudge != Memory.MEMORY_TRIGGERED.key or not event.values.get("single_use"):
            return
        repository = self.repositories[event.values["noun"]]
        with self.scope.environment(event.environment_id):
            for row in repository.matching(id=int(event.values["n"])):
                repository.delete(row, Actor.system())
