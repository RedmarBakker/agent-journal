from pathlib import Path
import os
import re
import time
from journal.features.faults.support.request_timer import RequestTimer
from journal.features.faults.support.test_run_files import TestRunFiles

from journal.config import Config
from journal.features.faults.support.slow_request_process_card import SlowRequestProcessCard
from journal.features.faults.support.slow_request_tally import SlowRequestTally
from journal.support.listener_queue import ListenerQueue
from journal.engine.clock import Clock
from journal.features.faults.feature import Faults
from journal.support.actor import Actor
from journal.repositories.agents import Agents
from journal.repositories.environments import Environments
from journal.repositories.messages import Messages
from journal.features.faults.support.developer_tally import DeveloperTally
from journal.models.timing import Timing
from journal.features.faults.support.developer_numbers import LOADS_PREFIX
from journal.models.support.request_loads import RequestLoads
from journal.repositories.load_tally import LoadTally
from journal.repositories.setting_rows import SettingRows
from journal.engine.support.nudge_log import NudgeLog
from journal.support.timeout import Timeout
from journal.repositories.scope import Scope

STARTUP_GRACE_SECONDS = 60.0
CHECK_INTERVAL_SECONDS = 5.0
STARTING = "journal.starting"


HOOK = "HOOK"
OUTWARD_ROUTES = ("/journal/plugins/preview", "/journal/plugins/{n}/remove", "/journal/plugins/{n}/upgrade", "/journal/plugins/{n}/enable", "/journal/plugins", "/journal/updates/install")
OUTWARD_COMMANDS = ("/cli/plugin install", "/cli/plugin upgrade", "/cli/plugin propose", "/cli/setup update", "/cli/update ", "/cli/worker dispatch", "/cli/check run", "/cli/mcp ")


class SlowRequests:
    """Measures each request against its budget, on its whole time from the moment its sender sent it, by the stamp every sender puts on it, to its answer, every wait included, where the journal develops itself, every one but a route's first since the boot, which loads its code and a cold cache once, with the rows it loaded while load counting is on, and reports one over it: one mark in the chat, settled in place with each route's worst time and count, and one line to the agent naming how many gathered and the worst, once ten have gathered or thirty seconds passed without another, asked at most every five seconds as requests come, and again only once the set minutes have passed since it was last told, the counts and the time it was told kept in the mark's data."""

    def __init__(self, config: Config, settings: SettingRows, card: SlowRequestProcessCard, messages: Messages, agents: Agents, environments: Environments, scope: Scope, nudges: NudgeLog, clock: Clock, deferred: ListenerQueue, tally: DeveloperTally, test_runs: TestRunFiles) -> None:
        self.config, self.settings, self.card, self.messages, self.agents, self.environments, self.scope, self.nudges, self.clock, self.deferred = config, settings, card, messages, agents, environments, scope, nudges, clock, deferred
        self.tally = tally
        self.test_runs = test_runs
        self.started = time.monotonic()
        self.measured_routes: set[str] = set()
        self.checked_at = 0.0

    def begin(self, request_at: float) -> RequestTimer:
        if self.settings.option(Faults.LOADS):
            LoadTally.begin()
        return RequestTimer(request_at)

    def measured(self, method: str, path: str, ms: float) -> None:
        loads = LoadTally.ended()
        self.counted(method, path, round(ms), loads)
        self.check_gathered(time.monotonic())
        route = re.sub(r"/\d+(?=/|$)", "/{n}", path)
        if self.is_first(f"{method} {route}") or not self.judging() or self.is_outward(route):
            return
        budget = self.budget(method)
        if not budget or ms <= budget:
            return
        self.deferred.add(lambda: self.reported(method, route, round(ms), budget))

    def counted(self, method: str, path: str, ms: int, loads: RequestLoads) -> None:
        self.tally.measured("developer.hooks" if method == HOOK else "developer.requests", ms)
        self.tally.logged(Timing(method=method, route=path, ms=ms, time=self.clock.time(), loads=loads))
        for count in loads.counts:
            self.tally.added(f"{LOADS_PREFIX}{count.model}", count.rows)
        if method == HOOK:
            self.tally.measured(f"developer.hooks.{path.rsplit('/', 1)[-1]}", ms)

    def is_first(self, route: str) -> bool:
        first = route not in self.measured_routes
        self.measured_routes.add(route)
        return first

    @staticmethod
    def is_outward(route: str) -> bool:
        return route.startswith(OUTWARD_COMMANDS) or route in OUTWARD_ROUTES

    def budget(self, method: str) -> int:
        return self.settings.integer(Faults.EDIT_BUDGET if method == "POST" else Faults.REQUEST)

    def judging(self) -> bool:
        starting = self.config.home / "runtime" / STARTING
        if starting.is_file():
            self.started = time.monotonic()
            return False
        resolved = time.monotonic() - self.started > STARTUP_GRACE_SECONDS
        busy = os.getloadavg()[0] > (os.cpu_count() or 1)
        return bool(self.settings.option(Faults.REPORT)) and resolved and not busy and not self.test_runs.is_testing()

    def reported(self, method: str, route: str, ms: int, budget: int) -> None:
        with self.scope.environment(self.environment_id()):
            self.flagged(f"{method} {route}", ms, budget)

    def environment_id(self) -> int:
        agent = self.agents.all_current()
        return agent.environment_id if agent else self.environments.all()[0].row_id

    def flagged(self, route: str, ms: int, budget: int) -> None:
        self.show(self.card_tally().flagged(route, ms, self.clock.time()), budget)

    def check_gathered(self, moment: float) -> None:
        if moment - self.checked_at < CHECK_INTERVAL_SECONDS or not self.settings.option(Faults.REPORT):
            return
        self.checked_at = moment
        self.deferred.add(lambda: self.report_gathered(self.clock.time()))

    def report_gathered(self, moment: float) -> None:
        with self.scope.environment(self.environment_id()):
            tally, agent = self.card_tally(), self.agents.current()
            if agent is None or not tally.is_gathered(moment) or not self.is_reportable(tally.reported_at, moment):
                return
            self.nudges.type_line(agent, Faults.SLOW_REQUESTS.create(count=tally.gathered, route=tally.slowest_route, ms=tally.slowest_ms))
            self.show(tally.reported(moment), self.budget("GET"))

    def card_tally(self) -> SlowRequestTally:
        older = self.messages.keyed(SlowRequestProcessCard.KEY, Actor.system())
        return SlowRequestTally.parsed(older[0].data) if older else SlowRequestTally()

    def show(self, tally: SlowRequestTally, budget: int) -> None:
        self.card.show(tally.total(), {"kind": "card", "icon": "gauge", "tone": "bad", "row": "", **tally.serialized()}, tally.detail(budget))

    def is_reportable(self, reported_at: float, moment: float) -> bool:
        if not reported_at:
            return True
        minutes = self.settings.integer(Faults.REPEAT)
        return minutes > 0 and Timeout.minutes(minutes).started(reported_at).is_elapsed(moment)
