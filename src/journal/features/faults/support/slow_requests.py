from journal.support.card_outcome import CardOutcome
from pathlib import Path
import os
import re
import time
from journal.features.faults.support.request_timer import RequestTimer
from journal.features.faults.support.test_run_files import TestRunFiles

from journal.config import Config
from journal.events.announcer import Announcer
from journal.events.moments.slow_requests_reported import SlowRequestsReported
from journal.features.faults.support.slow_request_tally import SlowRequestTally
from journal.support.listener_queue import ListenerQueue
from journal.engine.clock import Clock
from journal.engine.lifecycle import Lifecycle
from journal.repositories.agents import Agents
from journal.repositories.environments import Environments
from journal.features.faults.support.developer_tally import DeveloperTally
from journal.models.timing import Timing
from journal.features.faults.support.developer_numbers import LOADS_PREFIX
from journal.features.faults.support.developer_tally import POINTS_GROUP
from journal.models.support.request_loads import RequestLoads
from journal.repositories.load_tally import LoadTally
from journal.repositories.setting_rows import SettingRows
from journal.engine.support.nudge_log import NudgeLog
from journal.support.timeout import Timeout
from journal.repositories.scope import Scope
from journal.features.faults.faults_nudges import FaultsNudges
from journal.features.faults.faults_options import FaultsOptions

CHECK_INTERVAL_SECONDS = 5.0
# an answer that spends this many points or more is written with what it read to runtime/costly-answers.log, which outlives a restart
COSTLY_POINTS = 300


HOOK = "HOOK"
# the route a hook is posted to, timed again by the receiver as the hook it carries
HOOK_ROUTE = "/hooks/"
# the Developer tab's own requests and the developer command, never timed or counted, so reading the numbers never adds to them
# the developer's own reports, and the sync service's doors
UNMEASURED_PATHS = ("/journal/developer", "/cli/developer", "/journal/sync/")
OUTWARD_ROUTES = ("/journal/plugins/preview", "/journal/plugins/{n}/remove", "/journal/plugins/{n}/upgrade", "/journal/plugins/{n}/enable", "/journal/plugins", "/journal/updates/install")
OUTWARD_COMMANDS = ("/cli/plugin install", "/cli/plugin upgrade", "/cli/plugin propose", "/cli/setup update", "/cli/update ", "/cli/worker dispatch", "/cli/check run", "/cli/mcp ")


class SlowRequests:
    """Measures each request against its budget, on its whole time from the moment its sender sent it, by the stamp every sender puts on it, to its answer, every wait included but a wait for the journal's boot, and never while it boots, where the journal develops itself, every one but a route's first since the boot, which loads its code and a cold cache once, with the rows it loaded while load counting is on, and counts one over it in memory, each route's worst time and count; once ten have gathered or thirty seconds passed without another, asked at most every five seconds as requests come, and again only once the set minutes have passed since the agent was last informed, it tells the agent in one line how many gathered and the worst, and writes the chat mark with the counts then, never at each slow request."""

    def __init__(self, config: Config, settings: SettingRows, announcer: Announcer, agents: Agents, environments: Environments, scope: Scope, nudges: NudgeLog, clock: Clock, deferred: ListenerQueue, tally: DeveloperTally, test_runs: TestRunFiles, lifecycle: Lifecycle) -> None:
        self.config, self.settings, self.announcer, self.agents, self.environments, self.scope, self.nudges, self.clock, self.deferred = config, settings, announcer, agents, environments, scope, nudges, clock, deferred
        self.tally = tally
        self.test_runs, self.lifecycle = test_runs, lifecycle
        self.measured_routes: set[str] = set()
        self.checked_at = 0.0
        self.slow_tally = SlowRequestTally()

    def begin(self, request_at: float) -> RequestTimer:
        if self.settings.option(FaultsOptions.LOADS):
            LoadTally.begin()
        return RequestTimer(request_at)

    def measured(self, method: str, path: str, ms: float) -> None:
        loads = LoadTally.ended() if self.settings.option(FaultsOptions.LOADS) else RequestLoads()
        if path.startswith(UNMEASURED_PATHS) or not self.settings.option(FaultsOptions.DEVELOPER):
            return
        self.counted(method, path, round(ms), loads)
        self.check_gathered(time.monotonic())
        route = self.route(path)
        if self.is_first(f"{method} {route}") or not self.judging() or self.is_outward(route):
            return
        budget = self.budget(method)
        if not budget or ms <= budget:
            return
        self.deferred.add(lambda: self.flagged(f"{method} {route}", round(ms)))

    @staticmethod
    def route(path: str) -> str:
        return re.sub(r"/\d+(?=/|$)", "/{n}", path)

    def counted(self, method: str, path: str, ms: int, loads: RequestLoads) -> None:
        self.tally.measured("developer.hooks" if method == HOOK else "developer.requests", ms)
        timing = Timing(method=method, route=path, ms=ms, time=self.clock.time(), loads=loads)
        if method == HOOK:
            self.windowed("developer.hooks", path.rsplit("/", 1)[-1], timing)
        elif not path.startswith(HOOK_ROUTE):
            self.windowed("developer.requests", f"{method} {self.route(path)}", timing)
        self.tally.logged(timing)
        for count in loads.counts:
            self.tally.added(f"{LOADS_PREFIX}{count.model}", count.rows)
        if method == HOOK:
            self.tally.measured(f"developer.hooks.{path.rsplit('/', 1)[-1]}", ms)

    def windowed(self, group: str, type_name: str, timing: Timing) -> None:
        self.tally.windowed(group, type_name, timing.ms)
        if self.settings.option(FaultsOptions.LOADS) and not self.is_outward(self.route(timing.route)):
            self.tally.windowed(POINTS_GROUP, type_name, timing.loads.points())
            self.tally.loaded(type_name, timing.loads)
        if timing.loads.points() >= COSTLY_POINTS:
            self.deferred.add(lambda: self.costly(type_name, timing))

    def costly(self, type_name: str, timing: Timing) -> None:
        with (self.config.home / "runtime" / "costly-answers.log").open("a") as log:
            log.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {type_name} {timing.loads.points()} points in {timing.ms} ms: {timing.loads.line()}\n")

    def is_first(self, route: str) -> bool:
        first = route not in self.measured_routes
        self.measured_routes.add(route)
        return first

    @staticmethod
    def is_outward(route: str) -> bool:
        return route.startswith(OUTWARD_COMMANDS) or route in OUTWARD_ROUTES

    def budget(self, method: str) -> int:
        return self.settings.integer(FaultsOptions.EDIT_BUDGET if method == "POST" else FaultsOptions.REQUEST)

    @staticmethod
    def is_busy() -> bool:
        return os.getloadavg()[0] > (os.cpu_count() or 1)

    def judging(self) -> bool:
        return bool(self.settings.option(FaultsOptions.REPORT)) and self.lifecycle.is_booted() and not self.is_busy() and not self.test_runs.is_testing()

    def environment_id(self) -> int:
        agent = self.agents.all_current()
        return agent.environment_id if agent else self.environments.all()[0].row_id

    def flagged(self, route: str, ms: int) -> None:
        self.slow_tally = self.slow_tally.flagged(route, ms, self.clock.time())

    def check_gathered(self, moment: float) -> None:
        if moment - self.checked_at < CHECK_INTERVAL_SECONDS or not self.settings.option(FaultsOptions.REPORT):
            return
        self.checked_at = moment
        self.deferred.add(lambda: self.report_gathered(self.clock.time()))

    def report_gathered(self, moment: float) -> None:
        tally = self.slow_tally
        if not tally.is_gathered(moment) or not self.is_reportable(tally.reported_at, moment):
            return
        with self.scope.environment(self.environment_id()):
            agent = self.agents.current()
            if agent is None:
                return
            self.nudges.type_line(agent, FaultsNudges.SLOW_REQUESTS.create(count=tally.gathered, route=tally.slowest_route, ms=tally.slowest_ms))
            self.slow_tally = tally.reported(moment)
            self.show(tally, self.budget("GET"), moment)

    def show(self, tally: SlowRequestTally, budget: int, moment: float) -> None:
        self.announcer.announce(SlowRequestsReported(environment_id=self.scope.id, total=tally.total(), data={"kind": "card", "outcome": str(CardOutcome.WARNED), "row": "", **tally.serialized()}, detail=tally.detail(budget), moment=moment))

    def is_reportable(self, reported_at: float, moment: float) -> bool:
        if not reported_at:
            return True
        minutes = self.settings.integer(FaultsOptions.REPEAT)
        return minutes > 0 and Timeout.minutes(minutes).started(reported_at).is_elapsed(moment)
