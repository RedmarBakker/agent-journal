from functools import partial
import time

from journal.support.stage_times import StageTimes

from journal.engine.engine_nudges import EngineNudges
from journal.engine.nudger import Nudger
from journal.engine.support.session_agents import SessionAgents
from journal.events.moments.guard_failed import GuardFailed
from journal.events.moments.session_unbound import SessionUnbound
from journal.events.agent.agent_event import AgentEvent
from journal.events.agent.stop import Stop
from journal.events.agent.session_ended import SessionEnded
from journal.events.bus import Bus
from journal.events.listener import Listener
from journal.support.decision import Decision
from journal.support.listener_queue import ListenerQueue
from journal.support.hook import Hook
from journal.hooks.support.transcript_turns import TranscriptTurns
from journal.hooks.support.checker_hooks import CheckerHooks
from journal.helpers.helper_listeners import HelperListeners
from journal.hooks.support.worker_hooks import WorkerHooks
from journal.hooks.translation import Translation
from journal.support.actor import Actor
from journal.models.entry import Entry
from journal.repositories.agents import Agents
from journal.repositories.entries import Entries
from journal.repositories.environments import Environments
from journal.repositories.scope import Scope
from journal.features.faults.support.slow_requests import HOOK, SlowRequests
from journal.support.hook_kind import HookKind
from journal.engine.support.launch_files import LaunchFiles
from journal.models.environment import Environment
from journal.sync.environment_names import EnvironmentNames
from journal.support.time_source import TimeSource


GUARD_FAILED = "guard_failed"
UNBOUND_SESSION = "unbound_session"


class Receiver:
    """Translates a hook into its agent event, records it as an entry under the hook's key, a hook sent again being answered from that entry and reaching no listener, runs the blocking listeners at once and merges their decisions into the answer, and passes the rest to the deferred worker after the reply. A hook that does not include its environment's launch id, or that claims a worker, a verifier or a reviewer without that agent's proof, is recorded and reported, and reaches no listener; a verified worker's, verifier's or reviewer's hook is recorded and answered by the engine's listeners and those the helper's file allows, under that agent's own conduct, so none of the main agent's conduct blocks it and no recording listener posts it as the main agent's."""

    def __init__(self, environments: Environments, entries: Entries, translation: Translation, bus: Bus, deferred: ListenerQueue, scope: Scope, transcript: TranscriptTurns, agents: Agents, slow: SlowRequests, launches: LaunchFiles, worker_hooks: WorkerHooks, names: EnvironmentNames, stages: StageTimes, nudger: Nudger, sessions: SessionAgents, checker_hooks: CheckerHooks, helper_listeners: HelperListeners, time_source: TimeSource) -> None:
        self.time_source = time_source
        self.names, self.stages, self.nudger, self.sessions = names, stages, nudger, sessions
        self.environments, self.entries, self.translation, self.bus, self.deferred, self.scope = environments, entries, translation, bus, deferred, scope
        self.agents, self.launches = agents, launches
        self.transcript, self.slow = transcript, slow
        self.worker_hooks, self.checker_hooks, self.helper_listeners = worker_hooks, checker_hooks, helper_listeners

    def receive(self, raw_hook: Hook) -> Decision:
        self.slow.begin(self.time_source.seconds())
        hook = self.worker_hooks.attributed(raw_hook)
        environment = self.names.resolved(hook.environment)
        with self.scope.environment(environment.row_id):
            hook_entries = self.entries.keyed(hook.key())
            if hook_entries:
                return self.replayed(hook_entries[0])
            if not self.is_accepted(hook, environment):
                return self.unbound(hook, environment)
            self.worker_hooks.bind(hook, environment)
            self.checker_hooks.bind(hook, environment)
            if hook.is_sent():
                return self.sent_recorded(hook, environment)
            with self.stages.timed("hook transcript"):
                for saved in self.transcript.events(hook, environment):
                    self._immediate(saved)
            event = self.translation.event(hook, environment)
            with self.stages.timed("hook entry"):
                entry = self.recorded(hook, environment, event)
            if self.is_unknown_session_end(event):
                return Decision()
            decision = self._blocking(event, self._split(self.bus.listeners(type(event)))[0])
            self.entries.save(entry.with_merged("data", self.recorded_outcome(hook, decision)), Actor.agent(hook.session))
            self._defer(event)
        return decision

    def is_accepted(self, hook: Hook, environment: Environment) -> bool:
        if hook.is_sent():
            return self.worker_hooks.is_proven(hook) or self.checker_hooks.is_proven(hook)
        return self.launches.is_launch(environment.name, hook.launch)

    def sent_recorded(self, hook: Hook, environment: Environment) -> Decision:
        event = self.translation.event(hook, environment)
        self.recorded(hook, environment, event)
        blocking, deferred = self._split(self.helper_listeners.listeners(event))
        decision = self._blocking(event, blocking)
        for listener in deferred:
            self.deferred.add(partial(listener.handle, event))
        return decision

    def recorded(self, hook: Hook, environment: Environment, event: AgentEvent) -> Entry:
        return self.entries.recorded(Entry(environment_id=environment.row_id, kind=type(event).__name__, actor=Actor.agent(hook.session), data={**hook.stored(), **event.recorded()}, idempotency=hook.key()), Actor.agent(hook.session))

    @staticmethod
    def replayed(entry: Entry) -> Decision:
        return Decision.refuse(entry.data["refused"]) if entry.data.get("refused") else Decision()

    def unbound(self, hook: Hook, environment: Environment) -> Decision:
        self.entries.recorded(Entry(environment_id=environment.row_id, kind=UNBOUND_SESSION, actor=Actor.agent(hook.session), data={**hook.stored(), "launch": hook.launch}, idempotency=hook.key()), Actor.agent(hook.session))
        if hook.kind == HookKind.SESSION_START:
            self.bus.dispatch(SessionUnbound(environment_id=environment.row_id, session=hook.session, environment=environment.name))
        return Decision()

    def recorded_outcome(self, hook: Hook, decision: Decision) -> dict:
        recorded = {} if decision.allowed else {"refused": decision.reason}
        if not hook.started_ms:
            return recorded
        elapsed = int(self.time_source.seconds() * 1000) - hook.started_ms
        self.slow.measured(HOOK, f"/hooks/{hook.kind.value}", elapsed)
        boot_wait = {"boot_wait_ms": round(hook.boot_wait_seconds * 1000)} if hook.boot_wait_seconds else {}
        return {**recorded, "hook_ms": elapsed, **boot_wait}

    def is_unknown_session_end(self, event: AgentEvent) -> bool:
        return isinstance(event, SessionEnded) and not self.agents.matching(session=event.session)

    def _immediate(self, event: AgentEvent) -> None:
        blocking, deferred = self._split(self.bus.listeners(type(event)))
        for listener in [*blocking, *deferred]:
            listener.handle(event)

    def _blocking(self, event: AgentEvent, listeners: list[Listener]) -> Decision:
        decision = Decision()
        for listener in listeners:
            if not decision.allowed and getattr(listener, "asked_while_free", False):
                self.deferred.add(partial(listener.handle, event))
                continue
            with self.stages.timed(f"listener {type(listener).__name__}"):
                line_text = self._guarded(listener, event)
            if line_text is None:
                continue
            decision = decision.merged(Decision.allowed_with(line_text.reason) if not line_text.allowed and not decision.allowed else line_text)
        return decision

    def _guarded(self, listener: Listener, event: AgentEvent) -> Decision | None:
        try:
            answered = listener.handle(event)
            return answered if isinstance(answered, Decision) else None
        except Exception as fault:
            text = f"{type(listener).__name__} raised {type(fault).__name__}: {fault}"
            self.entries.save(Entry(environment_id=event.environment_id, kind=GUARD_FAILED, actor=Actor.system(), data={"session": event.session, "event": type(event).__name__, "listener": type(listener).__name__, "fault": f"{type(fault).__name__}: {fault}"}), Actor.system())
            self.bus.dispatch(GuardFailed(environment_id=event.environment_id, session=event.session, text=text))
            line = self.nudger.refuse_with(self.sessions.agent(event.session, event.environment_id), EngineNudges.GUARD_FAILED.create(text=text))
            return Decision.allowed_with(line) if line else None

    def _defer(self, event: AgentEvent) -> None:
        for listener in self._split(self.bus.listeners(type(event)))[1]:
            self.deferred.add(partial(self.timed_handle, listener, event))

    def timed_handle(self, listener: Listener, event: AgentEvent) -> None:
        with self.stages.timed(f"deferred {type(listener).__name__}"):
            listener.handle(event)

    @staticmethod
    def _split(listeners: list[Listener]) -> tuple[list[Listener], list[Listener]]:
        blocking = sorted((l for l in listeners if getattr(l, "blocking", False)), key=lambda l: getattr(l, "rank", 1))
        return blocking, [l for l in listeners if not getattr(l, "blocking", False)]
