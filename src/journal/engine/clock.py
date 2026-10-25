import threading

from journal.engine.job import Job
from journal.events.agent.ticked import Ticked
from journal.events.clock_ticked import ClockTicked
from journal.events.bus import Bus
from journal.support.decision import Decision
from journal.models.agent import Agent
from journal.repositories.agents import Agents
from journal.repositories.scope import Scope
from journal.supervisor_link import SupervisorLink
from journal.support.time_source import TimeSource


class Clock(Job):
    """The journal's time, and a job that tells the bus Ticked for every live agent every five seconds, in that agent's environment, each listener heard on its own so one that fails stops no other, and one tick at a time, each at the moment it takes its turn, so what a tick decides and records is settled before the next reads it and no tick carries a moment older than one already heard; what the machine says to a tick is typed in through the supervisor."""

    interval_seconds = 5.0

    def __init__(self, agents: Agents, bus: Bus, supervisor: SupervisorLink, scope: Scope, time_source: TimeSource) -> None:
        self.agents, self.bus, self.supervisor, self.scope, self.time_source = agents, bus, supervisor, scope, time_source
        self.tick_lock = threading.RLock()

    def time(self) -> float:
        return self.time_source.seconds()

    def tick(self, time: float) -> None:
        self.bus.dispatch_guarded(ClockTicked(time=time))
        for agent in self.agents.active_main_agents():
            with self.scope.environment(agent.environment_id):
                self._tick(agent)

    def _tick(self, agent: Agent) -> None:
        with self.tick_lock:
            time = self.time()
            self.ticked(Ticked(session=agent.session, environment_id=agent.environment_id, time=time, silence_seconds=time - agent.update_time.timestamp()))

    def ticked(self, event: Ticked) -> list[object]:
        with self.tick_lock:
            return self.bus.dispatch_guarded(event)
