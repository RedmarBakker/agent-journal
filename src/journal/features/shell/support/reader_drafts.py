from pathlib import Path

from journal.features.aliases.support.alias_lines import AliasLines
from journal.features.shell.shell_nudges import ShellNudges
from journal.features.shell.support.activity_label import ActivityLabel
from journal.features.shell.support.output_files import OutputFiles
from journal.features.shell.support.reader import Reader
from journal.features.shell.support.reader_draft import ReaderDraft
from journal.features.shell.support.reader_probes import TESTING, ReaderProbes
from journal.features.shell.support.readers import SHIPPED_READERS, Readers
from journal.features.shell.support.starting_readers import StartingReaders
from journal.models.agent import Agent
from journal.models.command_output import CommandOutput
from journal.repositories.command_outputs import CommandOutputs
from journal.repositories.entries import Entries
from journal.support.agent_role import AgentRole
from journal.support.chain import Chain
from journal.support.command_classifier import CommandClassifier
from journal.support.command_shape import CommandShape

# how many readers the journal drafts in one session at most, so the agent is never buried in them
SESSION_DRAFTS = 3
# how many reads of a run's output by a pattern, by hand, earn its part a reader whatever its kind
HAND_READS = 2
# the read of an output by hand that a reader could stand for
PATTERN_READ = "--grep"


class ReaderDrafts:
    """The readers the journal drafts for the runs that ended: a run that got a mark, whose part earns a reader by the kind its classification names or by two reads of its output by hand, that no reader reads well (a test run only by a reader that shows its progress, its failures and its summary, or one the journal ships) and no plugin alias runs, named by its part and said once in the environment, filled from its own output; never in a worker's session, at most one per run and a few per session."""

    def __init__(self, outputs: CommandOutputs, entries: Entries, readers: Readers, aliases: AliasLines, classifier: CommandClassifier, shapes: CommandShape, starting: StartingReaders, probes: ReaderProbes, labels: ActivityLabel) -> None:
        self.outputs, self.entries, self.readers, self.aliases = outputs, entries, readers, aliases
        self.classifier, self.shapes, self.starting, self.probes, self.labels = classifier, shapes, starting, probes, labels

    def drafts(self, agent: Agent) -> tuple[ReaderDraft, ...]:
        if agent.role != AgentRole.MAIN or not agent.session or len(self.entries.keyed_lines(agent.session, (ShellNudges.READER_DRAFT.key,))) >= SESSION_DRAFTS:
            return ()
        lines = "\n".join(self.entries.environment_lines(ShellNudges.READER_DRAFT.key))
        ended = [output for output in [*self.outputs.unannounced(agent.session), *self.outputs.watched(agent.session)] if output.moved and output.ended]
        return tuple(draft for output in ended if (draft := self.draft(output, agent.session)) is not None and f"reads {draft.part} yet" not in lines)

    def draft(self, output: CommandOutput, session: str) -> ReaderDraft | None:
        hand_read = self.hand_reads(output, session) >= HAND_READS
        part = next((part for part in Chain.self_parts(output.command) if self.earns(part, hand_read)), "")
        if not part:
            return None
        name = self.shapes.command_name(part)
        files = OutputFiles(Path(output.folder))
        reader = self.starting.filled(self.classifier.classify(part), name, files.lines() if files.is_stored() else [])
        if reader is not None and self.readers.plugin_aliases_read(reader):
            return None
        return ReaderDraft(output.row_id, name, self.reader_command(reader, name))

    def earns(self, part: str, hand_read: bool) -> bool:
        alias = self.aliases.running(part)
        if Chain.is_journal(part) or alias is not None and alias.plugin or self.is_read_well(part):
            return False
        return hand_read or StartingReaders.starting(self.classifier.classify(part)) is not None

    def is_read_well(self, command: str) -> bool:
        reader = self.readers.reading(command)
        if reader is None or self.labels.line_label(command) != TESTING:
            return reader is not None
        return reader.name in SHIPPED_READERS or self.probes.reads_test_runs(reader)

    def hand_reads(self, output: CommandOutput, session: str) -> int:
        return self.entries.output_reads(session, output.row_id, PATTERN_READ)

    @staticmethod
    def reader_command(reader: Reader | None, name: str) -> str:
        if reader is None:
            return f"journal reader add <name> --commands \"{name}\" --pattern '<the lines worth seeing>' --label '<what it does>'"
        flags = (("--pattern", reader.pattern), ("--progress", reader.progress_pattern), ("--finished", reader.finished_pattern), ("--failed", reader.failed_pattern), ("--label", reader.label))
        return f"journal reader add {reader.name} --commands \"{name}\" " + " ".join(f"{flag} '{value}'" for flag, value in flags if value)
