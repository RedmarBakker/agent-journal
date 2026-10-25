import os
import time as timing

from journal.config import Config
from journal.engine.lifecycle import Lifecycle
from journal.features.faults.support.developer_numbers import DeveloperNumbers
from journal.features.updates.support.update_card import UpdateCard
from journal.hooks.hook_arrivals import HookArrivals
from journal.http.agents.agent_activity import AgentActivity
from journal.http.agents.bar_row import PARTS, TOOLS, BarRow
from journal.http.agents.current_work import CurrentWork
from journal.http.journal.environment_data import EnvironmentData
from journal.http.journal.task_block import TaskBlock
from journal.http.journal.manifest import Manifest
from journal.http.support.request import Request
from journal.support.response import Response
from journal.models.environment import Environment
from journal.repositories.agents import Agents
from journal.repositories.entries import Entries
from journal.repositories.environments import Environments
from journal.repositories.messages import Messages
from journal.repositories.questions import Questions
from journal.repositories.scope import Scope
from journal.repositories.tasks import Tasks
from journal.version import VERSION
from journal.repositories.environment_owners import EnvironmentOwners

COLOR = "#5e64c9"
STARTED = timing.time()
SILENCE_LIMIT_SECONDS = 900.0
ACTIVITY_ENTRIES = 8
# each item of the bar opens with one entry and closes with another
ACTIVITY_ENTRY_ROWS = 2 * ACTIVITY_ENTRIES


class JournalController:
    """The journal as a whole: what the viewer starts from, who and where it is, the state of each environment, and what the current agent is doing now."""

    def __init__(self, config: Config, manifest: Manifest, environments: Environments, agents: Agents, activity: AgentActivity, current: CurrentWork,
                 entries: Entries, messages: Messages, questions: Questions, tasks: Tasks, scope: Scope, threshold: UpdateCard, numbers: DeveloperNumbers, owners: EnvironmentOwners, lifecycle: Lifecycle, arrivals: HookArrivals) -> None:
        self.numbers, self.owners, self.lifecycle, self.arrivals = numbers, owners, lifecycle, arrivals
        self.config, self.boot, self.environments, self.agents, self.activity, self.current = config, manifest, environments, agents, activity, current
        self.entries, self.messages, self.questions, self.tasks, self.scope, self.mark = entries, messages, questions, tasks, scope, threshold

    def manifest(self, request: Request) -> Response:
        return Response.json(self.boot.assembled(next((environment.name for environment in self.environments.all()), "")))

    def identity(self, request: Request) -> Response:
        return Response.json({"project": self.config.root.name, "color": COLOR, "root": str(self.config.home), "version": VERSION, "pid": os.getpid(), "parent": os.getppid(),
                              "environments": [e.name for e in self.environments.all()] or ["main"]})

    # the server answers, and answers unwell while an environment's hooks fire without reaching it or while it cannot open a file or read
    # its database, as when it has run out of descriptors, so its supervisor starts it again
    def health(self, request: Request) -> Response:
        self.config.port_file.read_text()
        self.environments.total()
        missing_hooks = self.arrivals.lost()
        return Response.json({"answering": True, "phase": self.lifecycle.phase.value, "hooks_lost": missing_hooks}, 503 if missing_hooks else 200)

    def journals(self, request: Request) -> Response:
        return Response.json([{"port": self.config.port, "project": self.config.root.name, "version": VERSION, "root": str(self.config.home), "current": True}])

    def developer(self, request: Request) -> Response:
        as_rows = lambda timings: [{"method": t.method, "route": t.route, "ms": t.ms, "time": t.time} for t in timings]
        return Response.json({"hooks": self.numbers.hook_time().as_data(), "requests": self.numbers.request_time().as_data(),
                              "by_kind": {kind: answer.as_data() for kind, answer in self.numbers.hook_averages().items()},
                              "recent": as_rows(self.numbers.recent()), "slowest": as_rows(self.numbers.slowest()),
                              "loads": [{"time": t.time, "label": t.label(), "ms": t.ms, "loads": t.loads.line()} for t in self.numbers.loaded()],
                              "models": [{"model": total.model, "rows": total.rows} for total in self.numbers.model_totals()]})

    def developer_reset(self, request: Request) -> Response:
        self.numbers.reset()
        return self.developer(request)

    def summary(self, request: Request) -> Response:
        blocked = self.mark.running()
        return Response.json({"project": self.config.root.name, "root": str(self.config.home), "version": VERSION, "started": STARTED, "color": COLOR,
                              "updating": blocked.target if blocked else "", "step": blocked.step if blocked else "",
                              "environments": [self.data(e) for e in self.environments.all()]})

    def data(self, environment: Environment) -> EnvironmentData:
        with self.scope.environment(environment.row_id):
            agent = self.agents.current()
            activity = self.activity.page([agent])[0] if agent else None
            work = self.current.work(agent) if agent else None
            task = TaskBlock(work.task.row_id, work.task.title, work.wait_text) if work else None
            silent = activity is not None and activity["status"] in ("busy", "working") and timing.time() - activity["heard_at"].timestamp() > SILENCE_LIMIT_SECONDS
            return EnvironmentData(environment, activity, task, self.questions.open_count(), self.messages.unread_count(), self.tasks.unfinished_count(), silent, self.owners.owner_name(environment.row_id))

    def bar(self, request: Request) -> Response:
        agent = self.agents.current()
        if not agent:
            return Response.json([])
        recent = BarRow.shown(self.entries.session_activity(agent.session, PARTS, TOOLS, ACTIVITY_ENTRY_ROWS))
        queue, open_ = [], {}
        for row in (BarRow.build(entry).relative(str(self.config.root)) for entry in recent):
            if not row.ended:
                open_[row.key] = row.item()
                queue.append(open_[row.key])
            elif row.key in open_:
                open_[row.key].update(done=True, parts=[*open_[row.key]["parts"], *row.counts()], hold=max(open_[row.key]["hold"], row.display_seconds()), **{"for": max(0.0, row.time - open_[row.key]["time"])})
                queue.extend(row.file_items())
        return Response.json(queue[-ACTIVITY_ENTRIES:])
