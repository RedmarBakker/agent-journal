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
from journal.hooks.support.verifier_hooks import VerifierHooks
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


GUARD_FAILED = "guard_failed"
UNBOUND_SESSION = "unbound_session"


class Receiver:
    """Translates a hook into its agent event, records it as an entry, runs the blocking listeners at once and merges their decisions into the answer, and passes the rest to the deferred worker after the reply. A hook that does not include its environment's launch id, or that claims a worker or a verifier without that agent's proof, is recorded and reported, and reaches no listener; a verified worker's or verifier's hook is recorded and answered by the listeners that receive sent agents' events, the state machine alone, under that agent's own conduct, so none of the main agent's conduct blocks it and no recording listener posts it as the main agent's."""

    def __init__(self, environments: Environments, entries: Entries, translation: Translation, bus: Bus, deferred: ListenerQueue, scope: Scope, transcript: TranscriptTurns, agents: Agents, slow: SlowRequests, launches: LaunchFiles, worker_hooks: WorkerHooks, names: EnvironmentNames, stages: StageTimes, nudger: Nudger, sessions: SessionAgents, verifier_hooks: VerifierHooks) -> None:
        self.names, self.stages, self.nudger, self.sessions = names, stages, nudger, sessions
        self.environments, self.entries, self.translation, self.bus, self.deferred, self.scope = environments, entries, translation, bus, deferred, scope
        self.agents, self.launches = agents, launches
        self.transcript, self.slow = transcript, slow
        self.worker_hooks, self.verifier_hooks = worker_hooks, verifier_hooks

    def receive(self, raw_hook: Hook) -> Decision:
        self.slow.begin(time.time())
        hook = self.worker_hooks.attributed(raw_hook)
        environment = self.names.resolved(hook.environment)
        with self.scope.environment(environment.row_id):
            if not self.is_accepted(hook, environment):
                return self.unbound(hook, environment)
            self.worker_hooks.bind(hook, environment)
            self.verifier_hooks.bind(hook, environment)
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
            return self.worker_hooks.is_proven(hook) or self.verifier_hooks.is_proven(hook)
        return self.launches.is_launch(environment.name, hook.launch)

    def sent_recorded(self, hook: Hook, environment: Environment) -> Decision:
        event = self.translation.event(hook, environment)
        self.recorded(hook, environment, event)
        blocking, deferred = self._split([listener for listener in self.bus.listeners(type(event)) if listener.is_worker_listener])
        decision = self._blocking(event, blocking)
        for listener in deferred:
            self.deferred.add(partial(listener.handle, event))
        return decision

    def recorded(self, hook: Hook, environment: Environment, event: AgentEvent) -> Entry:
        return self.entries.save(Entry(environment_id=environment.row_id, kind=type(event).__name__, actor=Actor.agent(hook.session), data={**hook.stored(), **event.recorded()}), Actor.agent(hook.session))

    def unbound(self, hook: Hook, environment: Environment) -> Decision:
        self.entries.save(Entry(environment_id=environment.row_id, kind=UNBOUND_SESSION, actor=Actor.agent(hook.session), data={**hook.stored(), "launch": hook.launch}), Actor.agent(hook.session))
        if hook.kind == HookKind.SESSION_START:
            self.bus.dispatch(SessionUnbound(environment_id=environment.row_id, session=hook.session, environment=environment.name))
        return Decision()

    def recorded_outcome(self, hook: Hook, decision: Decision) -> dict:
        recorded = {} if decision.allowed else {"refused": decision.reason}
        if not hook.started_ms:
            return recorded
        elapsed = int(time.time() * 1000) - hook.started_ms
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
