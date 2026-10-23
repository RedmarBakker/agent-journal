from journal.features.shell.support.ended_output import EndedOutput
from journal.features.shell.support.output_reads import OutputReads
from journal.features.shell.support.output_view import OutputView
from journal.features.shell.support.output_process_card import OutputProcessCard
from journal.features.shell.support.readers import Readers
from journal.engine.support.lazy_facts import LazyFacts
from journal.config import Config
from journal.models.agent import Agent
from journal.repositories.aliases import Aliases
from journal.repositories.command_outputs import CommandOutputs
from journal.repositories.entries import Entries
from journal.repositories.environments import Environments
from journal.repositories.scope import Scope
from journal.support.stage_times import StageTimes
from journal.support.worktree import Worktree
from journal.support.moment import Moment

HISTORY_READS = 26


class ShellDataReader:
    """Reads the shell feature's part of the feature data for an agent, each fact the first time a listener asks for it, with the fields ShellData names."""

    def __init__(self, outputs: CommandOutputs, entries: Entries, readers: Readers, card: OutputProcessCard, aliases: Aliases, config: Config, environments: Environments, scope: Scope, stages: StageTimes) -> None:
        self.outputs, self.entries, self.readers, self.card, self.aliases, self.config, self.environments = outputs, entries, readers, card, aliases, config, environments
        self.scope, self.stages = scope, stages

    def read(self, agent: Agent) -> LazyFacts:
        return LazyFacts("shell", {
            "background": lambda: tuple(o.row_id for o in self.outputs.background(agent.session)),
            "backgrounded_at": lambda: min((o.creation_time.timestamp() for o in self.outputs.background(agent.session)), default=0.0),
            "unannounced": lambda: tuple(EndedOutput(o.row_id, o.ending()) for o in self.outputs.unannounced(agent.session)),
            "unread": lambda: tuple(EndedOutput(o.row_id, o.ending()) for o in self.outputs.unread(agent.session)),
            "reader_requests": lambda: self.reader_requests(agent),
            "tool_uses": lambda: agent.tool_uses,
            "last_ending_line": lambda: self.last_ending_line(agent),
            "output_reads": lambda: self.output_reads(agent),
            "readers": lambda: tuple(self.readers.all()),
            "tipped": lambda: self.tipped(agent),
            "watch": lambda: self.watch(agent),
            "aliases": lambda: tuple(self.aliases.rows()),
            "home": lambda: str(Worktree(self.config.root, self.environments.find(agent.environment_id).name).folder),
        }, lambda: self.scope.environment(agent.environment_id), self.stages)

    def output_reads(self, agent: Agent) -> tuple[str, ...]:
        commands = [command for e in self.entries.output_tool_starts(agent.session) if (command := e.recorded_call().command)]
        return tuple([OutputReads.shape(c) for c in commands if OutputReads.is_one(c)][:HISTORY_READS])

    def tipped(self, agent: Agent) -> tuple[str, ...]:
        from journal.features.shell.feature import Shell
        return tuple(line for nudge in (Shell.READER_HINT, Shell.READER_SUGGESTION, Shell.ALIAS_SUGGESTION, Shell.NEW_READER_SUGGESTION, Shell.READER_FIX, Shell.READER_DETAIL, Shell.SILENT_CARD, Shell.SUMMARY_REQUEST) for line in self.entries.recent_lines(agent.session, nudge.key, 0))

    def reader_requests(self, agent: Agent) -> tuple[str, ...]:
        from journal.features.shell.feature import Shell
        requests = self.entries.line_entries(agent.session, (Shell.READER_FIX.key, Shell.READER_DETAIL.key))
        return tuple(reader.name for reader in self.readers.all() for entry in requests if f"the reader {reader.name} " in entry.data["line"] and entry.creation_time.timestamp() > self.readers.file_stamp(reader.name))

    def last_ending_line(self, agent: Agent) -> Moment:
        from journal.features.shell.feature import Shell
        from journal.features.tasks.feature import Tasks
        entry = self.entries.last_line_entry(agent.session, (Shell.OUTPUTS_ENDED.key, Shell.UNREAD_OUTPUT.key, Tasks.WAIT_END.key))
        return Moment(seconds=entry.data["time"], tool_uses=entry.data["tool_use"]) if entry else Moment()

    def watch(self, agent: Agent) -> OutputView:
        watched = self.outputs.watched(agent.session)
        return self.card.card_view(watched[0]) if watched else OutputView.empty()
