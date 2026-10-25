from journal.events.agent.agent_event import AgentEvent
from journal.models.agent_role import AgentRole
from collections.abc import Callable
from dataclasses import replace

from journal.events.event import Event
from journal.events.worker_merge_event import WorkerMergeEvent
from journal.features.plugins.support.linked_manifests import LinkedManifests
from journal.features.plugins.support.plugin_answers import PluginAnswers
from journal.features.plugins.support.plugin_fault import PluginFault
from journal.features.plugins.support.plugin_faults import PluginFaults
from journal.features.plugins.support.window_missed import WindowMissed
from journal.features.plugins.support.plugin_runner import PluginRunner
from journal.features.plugins.support.plugin_steps import PluginSteps
from journal.features.plugins.support.plugin_text import PluginText
from journal.features.plugins.support.protocol import Protocol
from journal.support.actor import Actor
from journal.models.entry import Entry
from journal.models.plugin import Plugin
from journal.features.plugins.support.plugin_answer import PluginAnswer
from journal.repositories.agents import Agents
from journal.repositories.entries import Entries
from journal.repositories.environments import Environments
from journal.repositories.plugins import Plugins
from journal.repositories.scope import Scope
from journal.support.listener_queue import ListenerQueue

LATER_SECONDS = 10
UNANSWERED = "plugin_unanswered"
WAITING = "plugin_line_waiting"
PLUGIN_LINE_KIND = "plugin_said"
CUT = "plugin_cut"
WARNING = "plugin_warning"
MERGE_CARDS = "plugin_merge_cards"


class PluginRelay:
    """Which plugins receive an event, and one plugin asked about it: the line built where the event happened, and a fault recorded, never raised."""

    def __init__(self, plugins: Plugins, runner: PluginRunner, protocol: Protocol, faults: PluginFaults, environments: Environments, agents: Agents, entries: Entries, answers: PluginAnswers, steps: PluginSteps, deferred: ListenerQueue, linked: LinkedManifests, text: PluginText, scope: Scope) -> None:
        self.plugins, self.runner, self.protocol, self.faults, self.answers, self.steps = plugins, runner, protocol, faults, answers, steps
        self.environments, self.agents, self.entries, self.deferred, self.linked = environments, agents, entries, deferred, linked
        self.text, self.scope = text, scope
        self.warnings: set[tuple[str, str]] = set()

    def listeners(self, event: Event, environment_id: int) -> list[Plugin]:
        name, actor = Protocol.published_name(event), getattr(event, "actor", None)
        hearers = self.plugins.hearers(name, actor)
        if hearers and self.is_worker(event):
            hearers = self.plugins.worker_hearers(name, actor)
        if hearers and self.steps.is_nested_deep():
            self.logged(environment_id, CUT, Actor.system(), {"event": Protocol.published_name(event), "by": getattr(event, "actor", Actor.system()).stamp, "plugins": [p.name for p in hearers]})
            return []
        return hearers

    def ask(self, plugin: Plugin, event: Event, environment_id: int, window: float, on_status: Callable[[str], None] | None = None) -> PluginAnswer:
        self.linked.notice(plugin, environment_id)
        environment = self.environments.find(environment_id).name if environment_id else ""
        try:
            answer = self.runner.ask(plugin, environment, self.protocol.event_line(event, environment, self.agent_state(event)), window, on_status)
        except WindowMissed as missed:
            self.unanswered(plugin, event, environment_id, str(missed))
            return PluginAnswer()
        except (PluginFault, OSError) as fault:
            self.faults.failed(plugin, environment_id, Protocol.published_name(event), str(fault))
            return PluginAnswer()
        self.faults.answered(plugin, environment_id)
        self.warned(plugin, answer, environment_id)
        self.applied(plugin, event, answer, environment, environment_id)
        return answer

    def warned(self, plugin: Plugin, answer: PluginAnswer, environment_id: int) -> None:
        keys = ", ".join(answer.ignored)
        if not keys or (plugin.name, keys) in self.warnings:
            return
        self.warnings.add((plugin.name, keys))
        self.logged(environment_id, WARNING, Actor.plugin(plugin.name), {"plugin": plugin.name, "warning": f"its answer has keys this journal does not know, ignored: {keys}"})

    def applied(self, plugin: Plugin, event: Event, answer: PluginAnswer, environment: str, environment_id: int) -> None:
        if isinstance(event, WorkerMergeEvent) and answer.cards:
            self.logged(environment_id, MERGE_CARDS, Actor.plugin(plugin.name), {"plugin": plugin.name, "worker": event.worker, "task": event.task, "cards": [{"kind": card.kind, "label": card.label, "detail": card.detail} for card in answer.cards]})
            answer = replace(answer, cards=())
        if answer.cards or answer.commands:
            self.deferred.add(lambda: self.answers.apply(plugin, answer, environment, environment_id))

    def postponed(self, plugin: Plugin, event: Event, environment_id: int) -> None:
        answer = self.ask(plugin, event, environment_id, LATER_SECONDS)
        if answer.answer == "refuse":
            self.unanswered(plugin, event, environment_id, answer.reason)
        elif answer.message:
            self.waiting(plugin, event, environment_id, answer.message)

    def waiting(self, plugin: Plugin, event: Event, environment_id: int, text: str) -> None:
        session = event.session if isinstance(event, AgentEvent) else self.current_session(environment_id)
        self.entries.save(Entry(environment_id=environment_id, kind=WAITING, actor=Actor.plugin(plugin.name), data={"plugin": plugin.name, "session": session, "event": Protocol.published_name(event), "line": self.text.line(plugin, text), "delivered": not session}), Actor.plugin(plugin.name))

    def queued_line(self, plugin: Plugin, environment_id: int, key: str, text: str) -> None:
        session = self.current_session(environment_id)
        self.entries.save(Entry(environment_id=environment_id, kind=WAITING, actor=Actor.plugin(plugin.name), data={"plugin": plugin.name, "session": session, "event": key, "line": self.text.line(plugin, text), "delivered": not session}), Actor.plugin(plugin.name))

    def current_session(self, environment_id: int) -> str:
        with self.scope.environment(environment_id):
            agent = self.agents.current()
        return agent.session if agent else ""

    def waiting_lines(self, session: str) -> list[str]:
        waiting = self.entries.undelivered_lines(WAITING, session)
        for entry in waiting:
            self.entries.save(entry.with_merged("data", {"delivered": True}), Actor.system())
        return [e.data["line"] for e in reversed(waiting)]

    def line(self, plugin: Plugin, event: Event, environment_id: int, manner: str, text: str) -> None:
        self.logged(environment_id, PLUGIN_LINE_KIND, Actor.plugin(plugin.name), {"plugin": plugin.name, "event": Protocol.published_name(event), "how": manner, "words": text})

    def unanswered(self, plugin: Plugin, event: Event, environment_id: int, reason: str) -> None:
        self.logged(environment_id, UNANSWERED, Actor.plugin(plugin.name), {"plugin": plugin.name, "event": Protocol.published_name(event), "reason": reason})

    def logged(self, environment_id: int, kind: str, actor: Actor, data: dict) -> None:
        self.entries.save(Entry(environment_id=environment_id, kind=kind, actor=actor, data=data), actor)

    def is_worker(self, event: Event) -> bool:
        if not isinstance(event, AgentEvent):
            return False
        agents = self.agents.matching(session=event.session)
        return bool(agents) and agents[0].role == AgentRole.WORKER

    def agent_state(self, event: Event) -> str:
        if not isinstance(event, AgentEvent):
            return ""
        agents = self.agents.matching(session=event.session)
        return agents[0].state if agents else ""
