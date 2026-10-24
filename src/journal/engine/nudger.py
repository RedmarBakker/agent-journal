from journal.support.moment import Moment
from journal.engine.clock import Clock
from journal.engine.nudge_registry import NudgeRegistry
from journal.events.agent.line_delivered import LineDelivered
from journal.events.bus import Bus
from journal.support.listener_queue import ListenerQueue
from journal.engine.support.feature_registry import FeatureRegistry
from journal.engine.nudge import Nudge
from journal.support.actor import Actor
from journal.models.agent import Agent
from journal.models.entry import Entry
from journal.repositories.entries import Entries
from journal.repositories.scope import Scope

NUDGE = "nudge"


class Nudger:
    """Sends a line to an agent, in the agent's environment: drops it when its feature is off or it was sent recently, writes the entry, announces on the bus that a line was sent once the reply has gone, and returns the words; a refusal's line is sent and recorded the same way but is never dropped for having been sent recently, since a hold lasts as long as its reason does. The caller picks the route: a hook's answer, or the supervisor."""

    def __init__(self, features: FeatureRegistry, entries: Entries, scope: Scope, bus: Bus, deferred: ListenerQueue, clock: Clock, registry: NudgeRegistry) -> None:
        self.features, self.entries, self.scope, self.bus, self.deferred, self.clock = features, entries, scope, bus, deferred, clock
        self.registry = registry

    def is_silenced(self, nudge: Nudge) -> bool:
        return self.features.silenced(nudge)

    def deliver(self, agent: Agent, nudge: Nudge) -> str | None:
        with self.scope.environment(agent.environment_id):
            return self._line_record(agent, nudge, repeated=True)

    def refuse_with(self, agent: Agent, nudge: Nudge) -> str | None:
        with self.scope.environment(agent.environment_id):
            return self._line_record(agent, nudge, repeated=False)

    def _line_record(self, agent: Agent, nudge: Nudge, repeated: bool) -> str | None:
        self.registry.lookup(nudge.key)
        if self.features.silenced(nudge) or repeated and self._repeat(agent, nudge):
            return None
        line = nudge.rendered()
        self.entries.save(Entry(environment_id=agent.environment_id, kind=NUDGE, actor=Actor.system(), data={"key": nudge.key, "session": agent.session, "line": line, "time": self.clock.time(), "tool_use": agent.tool_uses}), Actor.system())
        event = LineDelivered(nudge=nudge.key, values=dict(nudge.values)).placed(agent.session, agent.environment_id, agent.provider, None, self.clock.time())
        self.deferred.add(lambda: self.bus.dispatch(event))
        return line

    def _repeat(self, agent: Agent, nudge: Nudge) -> bool:
        if not nudge.repeat.amount:
            return False
        last = self.entries.last_key_moment(agent.session, nudge.key) if nudge.blocks_regardless else self.entries.last_line_moment(agent.session, nudge.key, nudge.rendered())
        return last is not None and not nudge.repeat.reset(last).has_passed(Moment(seconds=self.clock.time(), tool_uses=agent.tool_uses))
