from datetime import datetime
import json
from argparse import Namespace
from dataclasses import asdict
from datetime import datetime, timedelta
from pathlib import Path
from journal.console.support.chained_line import ChainedLine

from journal.console.command import Command
from journal.support.caller import Caller
from journal.support.worktree import Worktree
from journal.config import Config
from journal.features.shell.support.shell_record import ENDED, MOVED
from journal.support.environment_row import EnvironmentRow
from journal.support.agent_role import AgentRole
from journal.models.task_state import TaskState
from journal.providers.providers import Providers
from journal.repositories.agents import Agents
from journal.repositories.entries import Entries
from journal.repositories.environments import Environments
from journal.features.memory.support.memory_context import MemoryContext
from journal.features.briefing.support.overview_commands import OverviewCommands
from journal.features.tasks.active_task import ActiveTask
from journal.repositories.memories import Memories
from journal.repositories.messages import Messages
from journal.support.missing_row import MissingRow
from journal.support.rejection import Rejection
from journal.repositories.questions import Questions
from journal.repositories.reminders import Reminders
from journal.repositories.rules import Rules
from journal.repositories.scope import Scope
from journal.repositories.tasks import Tasks
from journal.repositories.workers import Workers
from journal.repositories.environment_owners import EnvironmentOwners
from journal.sync.team_account import TeamAccount
from journal.features.team.support.start_rule import StartRule
from journal.features.hydration.support.session_hydration import SessionHydration
from journal.features.team.support.environment_sharing import EnvironmentSharing
from journal.engine.support.launch_files import LaunchFiles
from journal.engine.states_catalogue import StatesCatalogue
from journal.support.time_source import TimeSource

TAKEOVER_WINDOW = timedelta(hours=12)
MEMORY_LINE = "your memories, heaviest first: {rows}. keep one where it was, or raise it, with `journal memory weigh <numbers> <weights>`"


class EnvironmentCommand(Command):
    noun = "environment"
    uncut_verbs = frozenset({"overview"})

    def __init__(self, environments: Environments, agents: Agents, tasks: Tasks, messages: Messages, questions: Questions, workers: Workers, entries: Entries, rules: Rules, memories: Memories, reminders: Reminders, providers: Providers, config: Config, scope: Scope, memory: MemoryContext, overview_commands: OverviewCommands, taking: ActiveTask, owners: EnvironmentOwners, account: TeamAccount, starts: StartRule, hydration: SessionHydration, sharing: EnvironmentSharing, launches: LaunchFiles, states: StatesCatalogue, time_source: TimeSource) -> None:
        self.time_source, self.states = time_source, states
        self.owners, self.account, self.starts, self.hydration, self.sharing = owners, account, starts, hydration, sharing
        self.environments, self.agents, self.tasks, self.messages, self.questions, self.workers, self.entries = environments, agents, tasks, messages, questions, workers, entries
        self.rules, self.memories, self.reminders, self.providers, self.config, self.scope = rules, memories, reminders, providers, config, scope
        self.memory, self.overview_commands, self.taking, self.launches = memory, overview_commands, taking, launches

    def arguments(self, verbs) -> None:
        self.verb(verbs, "overview", "everything in flight in this environment: the task in hand, open tasks, messages, questions, workers, background runs, and the rules and reminders, opening with the memories by weight, then each command the setting briefing.look_commands lists, under its heading; owed at every session start")
        self.verb(verbs, "list", "every environment and when it was last used")
        self.verb(verbs, "json", "the same, for the boot menu")
        creation = self.verb(verbs, "create", "a new line of work")
        creation.add_argument("name")
        creation.add_argument("--session", help="a kept conversation's session to fill the new environment's chat from, as journal environment sessions lists them")
        creation.add_argument("--provider", default="claude", help="the program that kept that session")
        self.verb(verbs, "sessions", "the project's kept conversations a new environment can carry on from, for the boot menu")
        self.verb(verbs, "filling", "how far a new environment's chat has been filled from its past session, in percent, for the boot menu").add_argument("name")
        branch = self.verb(verbs, "branch", "record the branch an environment's worktree works on, as the launcher does when it makes one")
        branch.add_argument("name")
        branch.add_argument("branch")
        self.verb(verbs, "delete", "an environment and everything recorded in it").add_argument("name")
        self.verb(verbs, "share", "show one of your environments in every team member's sidebar, its chat open to all").add_argument("name")
        self.verb(verbs, "unshare", "take an environment you shared back to your own sidebar").add_argument("name")
        rename = self.verb(verbs, "rename", "give an environment a new name; everything recorded in it stays")
        rename.add_argument("name")
        rename.add_argument("new")

    def rows(self) -> list[EnvironmentRow]:
        rows = []
        for environment in self.environments.all():
            agents = sorted(self.agents.global_matching(environment_id=environment.row_id, role=AgentRole.MAIN), key=lambda item: item.update_time)
            last = agents[-1] if agents else None
            resumable = [item for item in agents if item.session and self.providers.lookup(item.provider).transcript(self.config.root, item.session)]
            working = last is not None and not self.states.restored(last.state, last.data).final and not self.launches.is_abandoned(environment.name)
            rows.append(EnvironmentRow(environment.name, working, self.age(last.update_time) if last else "", {item.provider: item.session for item in resumable}, self.starts.refusal(environment, self.account.user_number()), environment.branch == Worktree(self.config.root, environment.name).branch))
        return rows

    def overview(self, args: Namespace, caller: Caller) -> int:
        for line in self.current_work(caller):
            print(line)
        self.overview_record(caller)
        self.memory.admit_all(caller.actor)
        return 0

    def overview_chain(self, args: Namespace, caller: Caller) -> list[ChainedLine]:
        return self.overview_commands.lines()

    def current_work(self, caller: Caller) -> list[str]:
        start = self.time_source.moment() - TAKEOVER_WINDOW
        peer = self.agents.recent_peer(caller.session, start)
        holder = self.taking.holder(caller)
        current = None if holder is None else self.tasks.holder_task(holder)
        peer_tasks = self.tasks.other_started_tasks(current)
        lines = [
            self.memory_lines(),
            f"taken over from another agent, last seen {peer.update_time.astimezone().strftime('%H:%M')}" if peer else "",
            f"task in hand: {current.id} {current.title}" if current else "no task in hand",
            self.matching_rows("started by other agents", [f"{t.id} {t.title}" for t in peer_tasks]),
            self.matching_rows("open tasks", [f"{t.id} {t.title}" for t in self.tasks.open_tasks()]),
            self.matching_rows("paused tasks", [f"{t.id} {t.title} ({t.pause_reason})" for t in self.tasks.with_state(TaskState.PAUSED)]),
            self.matching_rows("blocked tasks", [f"{t.id} {t.title} (waiting on: {self.tasks.reason(t)})" for t in self.tasks.blocked_tasks()]),
            self.matching_rows("unread messages", [str(m.id) for m in self.messages.unread()]),
            self.matching_rows("messages read and unanswered", [str(m.id) for m in self.messages.unanswered()]),
            self.matching_rows("questions waiting for the user", [f"{q.id} {q.text}" for q in self.questions.open()]),
            self.matching_rows("workers out", [f"{w.id} {w.name}" for w in self.workers.active()]),
            self.matching_rows("running in the background", self.background()),
            self.matching_rows("rules in force", [f"{r.id} {r.text}" for r in self.rules.all()]),
            self.matching_rows("reminders here", [f"{r.id} {r.text}" for r in self.reminders.standing()]),
        ]
        return [line for line in lines if line]

    def memory_lines(self) -> str:
        shown = self.memories.shown()
        if not shown:
            return "no memories yet: `journal memory add \"<what to keep in mind>\" --weight <1 to 10>`"
        weighed = "; ".join(f"{memory.id} (weight {memory.weight}) {memory.text}" for memory in shown)
        return MEMORY_LINE.format(rows=weighed)

    def background(self) -> list[str]:
        moved = self.entries.open_moves(MOVED, ENDED)
        return [f"{e.data['part']} (output in {e.data['file']})" for e in moved if Path(e.data["file"]).is_dir() and not (Path(e.data["file"]) / "done").is_file()]

    @staticmethod
    def matching_rows(subject: str, rows: list[str]) -> str:
        return f"{subject}: " + "; ".join(rows) if rows else ""

    def overview_record(self, caller: Caller) -> None:
        if caller.session is None:
            return
        try:
            self.agents.save(self.agents.session_agent(caller.session).overview_read(self.time_source.moment().timestamp()), caller.actor)
        except MissingRow:
            return

    def list(self, args: Namespace, caller: Caller) -> int:
        for row in self.rows():
            print(f"{row.name:<20} {row.last_used}")
        return 0

    def json(self, args: Namespace, caller: Caller) -> int:
        print(json.dumps([asdict(row) for row in self.rows()]))
        return 0

    def branch(self, args: Namespace, caller: Caller) -> int:
        host = self.account.device_name() if args.branch == Worktree(self.config.root, args.name).branch else ""
        environment = self.environments.save(self.environments.existing(args.name).with_(branch=args.branch, worktree_host=host), caller.actor)
        print(f"environment {environment.name} works on branch {environment.branch}")
        return 0

    def create(self, args: Namespace, caller: Caller) -> int:
        environment = self.hydration.created(args.name, args.provider, args.session, caller.actor) if args.session else self.environments.lookup(args.name)
        print(f"environment {environment.id}: {environment.name}")
        return 0

    def filling(self, args: Namespace, caller: Caller) -> int:
        print(self.hydration.filled_percent(args.name))
        return 0

    def sessions(self, args: Namespace, caller: Caller) -> int:
        print(json.dumps(self.hydration.past_sessions()))
        return 0

    def delete(self, args: Namespace, caller: Caller) -> int:
        rows = self.environments.matching(name=args.name)
        if not rows:
            print(f"no environment named {args.name}")
            return 1
        self.environments.wipe(rows[0], caller.actor)
        worktree_line = Worktree(self.config.root, rows[0].name).worktree_note()
        print(f"deleted environment {rows[0].id}: {rows[0].name}, with everything recorded in it" + (f"; {worktree_line}" if worktree_line else ""))
        return 0

    def share(self, args: Namespace, caller: Caller) -> int:
        environment = self.sharing.shared(self.environments.existing(args.name), caller.actor)
        print(f"environment {environment.name} is shared with the team: it shows in every member's sidebar, its chat open to all; journal environment unshare {environment.name} takes it back")
        return 0

    def unshare(self, args: Namespace, caller: Caller) -> int:
        environment = self.sharing.unshared(self.environments.existing(args.name), caller.actor)
        print(f"environment {environment.name} is yours alone again: it shows only in your sidebar, and colleagues comment in its chat")
        return 0

    def rename(self, args: Namespace, caller: Caller) -> int:
        rows = self.environments.existing(args.name)
        if self.environments.matching(name=args.new):
            raise Rejection(f"an environment named {args.new} exists already")
        with self.scope.environment(rows.row_id):
            if self.agents.current() is not None:
                raise Rejection(f"an agent works in {rows.name}: stop it first, then rename")
        tree = Worktree(self.config.root, rows.name)
        branch = tree.renamed(args.new).branch if rows.branch == tree.branch or tree.path.is_dir() else rows.branch
        renamed = self.environments.save(rows.with_(name=args.new, branch=branch), caller.actor)
        print(f"environment {renamed.id} renamed: {args.name} is now {renamed.name}")
        return 0

    def age(self, time: datetime) -> str:
        seconds = (self.time_source.moment() - time).total_seconds()
        for unit, span in (("day", 86400), ("hour", 3600), ("minute", 60)):
            if seconds >= span:
                n = int(seconds // span)
                return f"{n} {unit}{'s' if n != 1 else ''} ago"
        return "just now"
