import re
import subprocess
from journal.models.support.worker_task import WorkerTask
from pathlib import Path

from journal.config import Config
from journal.console.console import Console
from journal.support.caller import Caller
from journal.events.agent.commit_detected import CommitDetected
from journal.events.agent.tool_finished import ToolFinished
from journal.hooks.agent_event_post import AgentEventPost
from journal.features.git.support.head_commit import FORMAT, HeadCommit
from journal.events.agent_listener import AgentListener
from journal.repositories.tasks import Tasks as TaskRows
from journal.repositories.entries import Entries
from journal.repositories.environments import Environments
from journal.support.worktree import Worktree
from journal.events.announcer import Announcer
from journal.features.git.support.git_facts import GitFacts
from journal.features.tasks.support.next_task_reader import NextTaskReader
from journal.support.decision import Decision
from journal.support.time_source import TimeSource
from journal.events.blocking import Blocking

COMMIT_WINDOW_SECONDS = 60
RECENT_TOOL_STARTS = 3
TRAILER = re.compile(r"^Journal: (?:tasks|todos) done ((?:\d+(?:[ ,]+(?:and +)?)?)+)\s*(.*)$", re.MULTILINE)


class CommitDetection(AgentListener[ToolFinished]):
    """A shell command that committed is followed by a read of the head: the commit becomes a card in the chat, once, a Journal: tasks done line in its message finishes those tasks, and the bus is informed a commit was made with what it closed; what the agent is informed about it is the git conduct's, returned with the command's own answer. A commit whose own hook never arrived, lost to an install or a restart in the same line, is found at the next tool use because the head's log has changed, the first read after the journal starts counting as changed, and its tasks close when one of the session's last tool starts contained the commit."""

    blocking = Blocking.ANSWER

    def __init__(self, config: Config, console: Console, environments: Environments, tasks: TaskRows, events: AgentEventPost, next_tasks: NextTaskReader, entries: Entries, announcer: Announcer, time_source: TimeSource) -> None:
        self.time_source = time_source
        self.announcer = announcer
        self.config, self.console, self.environments, self.tasks, self.events = config, console, environments, tasks, events
        self.next_tasks, self.entries = next_tasks, entries
        self._head_log_times: dict[Path, float] = {}
        self.detected: set[str] = set()

    def handle(self, event: ToolFinished) -> Decision | None:
        texts = [part.text for part in event.call.parts]
        if any(text.startswith("git merge") for text in texts):
            return self.merged(event)
        folder, commit_call = self.folder(event), any(text.startswith("git commit") for text in texts)
        if not commit_call and not self.head_moved(folder):
            return None
        head = self.head(folder)
        if not head or not (commit_call or self.is_agents(event, head)) or not self.is_new(head.sha):
            return None
        committed = GitFacts.commit(folder, event.environment_id, event.session)
        if committed is not None:
            self.announcer.announce(committed)
        return self.commit(event, head.sha, head.body if self.is_agents(event, head) else "")

    def is_agents(self, event: ToolFinished, head: HeadCommit) -> bool:
        if self.time_source.seconds() - head.committed <= COMMIT_WINDOW_SECONDS:
            return True
        starts = self.entries.tool_starts(event.session, last=RECENT_TOOL_STARTS)
        return any(part.text.startswith("git commit") for start in starts for part in start.recorded_call().parts)

    def head_moved(self, folder: Path) -> bool:
        log = self.head_log(folder)
        try:
            moment = log.stat().st_mtime
        except OSError:
            return False
        existing = self._head_log_times.get(folder)
        self._head_log_times[folder] = moment
        return existing != moment

    @staticmethod
    def head_log(folder: Path) -> Path:
        git = folder / ".git"
        if git.is_file():
            return Path(git.read_text().strip().removeprefix("gitdir:").strip()) / "logs" / "HEAD"
        return git / "logs" / "HEAD"

    def commit(self, event: ToolFinished, sha: str, body: str) -> Decision | None:
        numbers, owners = self.trailer_tasks(body), self.tasks.worker_holdings()
        worker_tasks = tuple(WorkerTask(n, owners[n]) for n in numbers if n in owners)
        completions = self.completions(event, sha, [n for n in numbers if n not in owners])
        next_task = self.next_tasks.holder_task(self.tasks.find(completions[-1])) if completions else None
        commit = CommitDetected(sha=sha, closed=tuple(completions), next_task=next_task, worker_tasks=worker_tasks).placed(event.session, event.environment_id, event.provider, event.context, event.time)
        return next((answer for answer in self.events.post(commit) if isinstance(answer, Decision)), None)

    def folder(self, event: ToolFinished) -> Path:
        return Worktree(self.config.root, self.environments.find(event.environment_id).name).folder

    def merged(self, event: ToolFinished) -> Decision | None:
        delivered = subprocess.run(["git", "log", "--format=%H%x00%B%x01", "ORIG_HEAD..HEAD"], cwd=self.config.root, capture_output=True, text=True, timeout=5)
        if delivered.returncode != 0:
            return None
        delivered_commits = (entry.strip().partition("\0") for entry in delivered.stdout.split("\x01") if entry.strip())
        decisions = [self.commit(event, sha, body) for sha, _, body in delivered_commits if self.trailer_tasks(body) and self.is_new(sha)]
        return next((decision for decision in decisions if decision), None)

    def is_new(self, sha: str) -> bool:
        if sha in self.detected:
            return False
        self.detected.add(sha)
        return True

    def trailer_tasks(self, body: str) -> list[int]:
        numbers = [int(n) for rows in TRAILER.finditer(body) for n in re.findall(r"\d+", rows.group(1))]
        return self.tasks.unfinished_ids(numbers)

    def completions(self, event: ToolFinished, sha: str, numbers: list[int]) -> list[int]:
        caller = Caller.agent(self.environments.find(event.environment_id).name, event.session, event.provider)
        return [n for n in numbers if self.console.run(["task", "complete", str(n), "--how", f"commit {sha[:8]}"], caller).code == 0]

    def head(self, folder: Path) -> HeadCommit | None:
        try:
            output = subprocess.run(["git", "log", "-1", f"--format={FORMAT}"], cwd=folder, capture_output=True, text=True, timeout=5)
        except (OSError, subprocess.TimeoutExpired):
            return None
        if output.returncode != 0 or not output.stdout.strip():
            return None
        return HeadCommit.parsed(output.stdout)
