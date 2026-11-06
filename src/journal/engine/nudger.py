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
from journal.repositories.entries import CUT_KEY, Entries
from journal.repositories.scope import Scope

NUDGE = "nudge"


class Nudger:
    """Sends a line to an agent, in the agent's environment: drops it when its feature is off or it was sent recently, writes the entry with its key, its values and its line, cut to the line's longest with the length it was cut from, announces on the bus that a line was sent once the reply has gone, and returns the words; a refusal's line, and a line that answers a command the agent ran, is sent and recorded the same way but is never dropped for having been sent recently, since a hold lasts as long as its reason does and an answer is always wanted. The caller picks the route: a hook's answer, or the supervisor."""

    def __init__(self, features: FeatureRegistry, entries: Entries, scope: Scope, bus: Bus, deferred: ListenerQueue, clock: Clock, registry: NudgeRegistry) -> None:
        self.features, self.entries, self.scope, self.bus, self.deferred, self.clock = features, entries, scope, bus, deferred, clock
        self.registry = registry

    def is_silenced(self, nudge: Nudge) -> bool:
        return self.features.silenced(nudge)

    def deliver(self, agent: Agent, nudge: Nudge) -> str | None:
        with self.scope.environment(agent.environment_id):
            return self._line_record(agent, nudge, self._repeat_moment(agent, nudge), {})

    def deliver_in_prompt(self, agent: Agent, nudge: Nudge) -> str | None:
        with self.scope.environment(agent.environment_id):
            return self._line_record(agent, nudge, self._hook_repeat_moment(agent, nudge), {})

    def deliver_to_terminal(self, agent: Agent, nudge: Nudge) -> str | None:
        with self.scope.environment(agent.environment_id):
            return self._line_record(agent, nudge, self._repeat_moment(agent, nudge), {"delivery": "terminal"})

    def answer(self, agent: Agent, nudge: Nudge) -> str | None:
        with self.scope.environment(agent.environment_id):
            return self._line_record(agent, nudge, None, {})

    def refuse_with(self, agent: Agent, nudge: Nudge) -> str | None:
        return self.answer(agent, nudge)

    def _line_record(self, agent: Agent, nudge: Nudge, last: Moment | None, delivery: dict[str, str]) -> str | None:
        self.registry.lookup(nudge.key)
        if self.features.silenced(nudge) or self._repeated(agent, nudge, last):
            return None
        rendered = nudge.rendered()
        line = nudge.cut(rendered)
        cut = {CUT_KEY: len(rendered)} if nudge.is_overlong(rendered) else {}
        self.entries.save(Entry(environment_id=agent.environment_id, entry_type=NUDGE, actor=Actor.system(), data={"key": nudge.key, "values": {name: str(value) for name, value in nudge.values.items()}, "session": agent.session, "line": line, "time": self.clock.time(), "tool_use": agent.tool_uses, **delivery, **cut}), Actor.system())
        event = LineDelivered(nudge=nudge.key, values=dict(nudge.values), agent=agent).placed(agent, None, self.clock.time())
        self.deferred.add(lambda: self.bus.dispatch(event))
        return line

    def _repeat_moment(self, agent: Agent, nudge: Nudge) -> Moment | None:
        if nudge.blocks_regardless:
            return self.entries.last_key_moment(agent.session, nudge.key)
        return self.entries.last_line_moment(agent.session, nudge.key, nudge.cut(nudge.rendered()))

    def _hook_repeat_moment(self, agent: Agent, nudge: Nudge) -> Moment | None:
        if nudge.blocks_regardless:
            return self.entries.last_hook_key_moment(agent.session, nudge.key)
        return self.entries.last_hook_line_moment(agent.session, nudge.key, nudge.cut(nudge.rendered()))

    def _repeated(self, agent: Agent, nudge: Nudge, last: Moment | None) -> bool:
        if not nudge.repeat.amount or last is None:
            return False
        return not nudge.repeat.reset(last).has_passed(Moment(seconds=self.clock.time(), tool_uses=agent.tool_uses))
