from journal.repositories.reader_reports import ReaderReports
from journal.features.shell.support.ended_output import EndedOutput
from journal.features.shell.support.output_reads import OutputReads
from journal.features.shell.support.output_view import OutputView
from journal.features.shell.support.output_process_card import OutputProcessCard
from journal.features.shell.support.readers import Readers
from journal.features.shell.support.reader_drafts import ReaderDrafts
from journal.features.shell.support.silent_runs import SilentRuns
from journal.engine.support.lazy_facts import LazyFacts
from journal.config import Config
from journal.features.registry import Registry
from journal.models.agent import Agent
from journal.repositories.aliases import Aliases
from journal.repositories.command_outputs import CommandOutputs
from journal.repositories.entries import Entries
from journal.repositories.environments import Environments
from journal.repositories.scope import Scope
from journal.support.stage_times import StageTimes
from journal.support.worktree import Worktree
from journal.support.moment import Moment
from journal.features.shell.shell_nudges import ShellNudges
from journal.features.tasks.tasks_nudges import TasksNudges

HISTORY_READS = 26


class ShellDataReader:
    """Reads the shell feature's part of the feature data for an agent, each fact the first time a listener asks for it, with the fields ShellData names."""

    def __init__(self, outputs: CommandOutputs, entries: Entries, readers: Readers, card: OutputProcessCard, aliases: Aliases, config: Config, environments: Environments, scope: Scope, stages: StageTimes, reports: ReaderReports, registry: Registry, silent: SilentRuns, drafts: ReaderDrafts) -> None:
        self.drafts = drafts
        self.reports, self.registry, self.silent = reports, registry, silent
        self.outputs, self.entries, self.readers, self.card, self.aliases, self.config, self.environments = outputs, entries, readers, card, aliases, config, environments
        self.scope, self.stages = scope, stages

    def read(self, agent: Agent) -> LazyFacts:
        return LazyFacts("shell", {
            "background": lambda: tuple(o.row_id for o in self.outputs.background(agent.session)),
            "backgrounded_at": lambda: min((o.creation_time.timestamp() for o in self.outputs.background(agent.session)), default=0.0),
            "unannounced": lambda: tuple(EndedOutput(o.row_id, o.ending(), o.summary) for o in self.outputs.unannounced(agent.session)),
            "unread": lambda: tuple(EndedOutput(o.row_id, o.ending(), o.summary) for o in self.outputs.unread(agent.session)),
            "tool_uses": lambda: agent.tool_uses,
            "last_ending_line": lambda: self.last_ending_line(agent),
            "output_reads": lambda: self.output_reads(agent),
            "readers": lambda: tuple(self.readers.all()),
            "tipped": lambda: self.tipped(agent),
            "silent_runs": lambda: self.silent.running(agent.session) if agent.session else (),
            "watch": lambda: self.watch(agent),
            "aliases": lambda: tuple(self.aliases.rows()),
            "reader_drafts": lambda: self.drafts.drafts(agent),
            "draft_count": lambda: len(self.entries.keyed_lines(agent.session, (ShellNudges.READER_DRAFT.key,))),
            "unread_reports": lambda: tuple(report.id for report in self.reports.unread(agent.session, self.readers.locked_names())),
            "unfixed_reports": lambda: tuple(report.id for report in self.reports.unrevised(agent.session, self.readers.open_revisions())),
            "refuted_reports": lambda: tuple(self.reports.refuted(agent.session, self.readers.open_revisions())),
            "uncut_verbs": lambda: self.registry.uncut_verbs(),
            "home": lambda: str(Worktree(self.config.root, self.environments.find(agent.environment_id).name).folder),
        }, lambda: self.scope.environment(agent.environment_id), self.stages)

    def output_reads(self, agent: Agent) -> tuple[str, ...]:
        commands = [command for e in self.entries.output_tool_starts(agent.session) if (command := e.recorded_call().command)]
        return tuple([OutputReads.shape(c) for c in commands if OutputReads.is_one(c)][:HISTORY_READS])

    def tipped(self, agent: Agent) -> tuple[str, ...]:
        tips = (ShellNudges.READER_HINT, ShellNudges.ALIAS_SUGGESTION, ShellNudges.SILENT_RUN_HINT, ShellNudges.REPORT_RAISED, ShellNudges.REPORT_REFUTED)
        return tuple(self.entries.keyed_lines(agent.session, tuple(nudge.key for nudge in tips)))

    def last_ending_line(self, agent: Agent) -> Moment:
        entry = self.entries.last_line_entry(agent.session, (ShellNudges.OUTPUTS_ENDED.key, ShellNudges.UNREAD_OUTPUT.key, TasksNudges.WAIT_END.key))
        return Moment(seconds=entry.data["time"], tool_uses=entry.data["tool_use"]) if entry else Moment()

    def watch(self, agent: Agent) -> OutputView:
        watched = self.outputs.watched(agent.session)
        return self.card.card_view(watched[0]) if watched else OutputView.empty()
