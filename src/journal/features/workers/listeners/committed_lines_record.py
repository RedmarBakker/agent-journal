from journal.events.listener import Listener
from journal.events.moments.git_committed import GitCommitted
from journal.features.workers.support.worker_branch import REBUILD_SUBJECT, WorkerBranch
from journal.features.workers.workers_options import WorkersOptions
from journal.repositories.agents import Agents
from journal.repositories.setting_rows import SettingRows
from journal.support.actor import Actor
from journal.support.time_source import TimeSource


class CommittedLinesRecord(Listener[GitCommitted]):
    """The lines a commit of the main agent's own session added are kept on its row as its committed lines, once per sha however many announce it, the built paths left out and a commit capped at the setting; a sha a worker's merge brought in or the journal's own rebuild commit counts nothing."""

    def __init__(self, agents: Agents, branch: WorkerBranch, settings: SettingRows, time_source: TimeSource) -> None:
        self.agents, self.branch, self.settings, self.time_source = agents, branch, settings, time_source

    def handle(self, event: GitCommitted) -> None:
        agent = self.agents.active_main_agent(event.session) if event.session else None
        if agent is None or agent.is_sha_counted(event.sha) or event.subject == REBUILD_SUBJECT:
            return
        lines, time = min(self.unbuilt_lines(event), self.settings.integer(WorkersOptions.COMMIT_LINE_CAP)), self.time_source.seconds()
        cutoff = time - self.settings.decimal(WorkersOptions.SERIES_HOURS) * 3600
        self.agents.rewritten(agent, Actor.system(), lambda current: current if current.is_sha_counted(event.sha) else current.lines_committed(event.sha, lines, time, cutoff))

    def unbuilt_lines(self, event: GitCommitted) -> int:
        return sum(added for path, added in event.lines if not self.branch.is_built(path))
