from datetime import datetime, timezone
from pathlib import Path

from journal.features.aliases.support.alias_lines import AliasLines
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
from journal.repositories.reader_suggestions import ReaderSuggestions
from journal.support.chain import Chain
from journal.support.command_classifier import CommandClassifier
from journal.support.command_shape import CommandShape
from journal.support.command_part import CommandPart

# the keys of the reader lines the one draft replaced, each with the value that named its part, so a part suggested then is not suggested again
RETIRED_KEYS = {"shell.make_its_reader": "command", "shell.counting_reader_suggestion": "command", "shell.reader_needed": "commands", "shell.add_a_reader": "command"}
# how many reads of a run's output by a pattern, by hand, earn its part a reader whatever its kind
HAND_READS = 2
# the read of an output by hand that a reader could stand for
PATTERN_READ = "--grep"


class ReaderDrafts:
    """The readers the journal drafts for the runs that ended: a run that got a mark, whose part earns a reader by the kind its classification names or by two reads of its output by hand, that no reader reads well (a test run only by a reader that shows its progress, its failures and its summary, or one the journal ships) and no plugin alias runs, named by its part, filled from its own output, with whether the project was told of the part before, by the one line or the lines it replaced, and its runs since; never in a helper's session."""

    def __init__(self, outputs: CommandOutputs, entries: Entries, suggestions: ReaderSuggestions, readers: Readers, aliases: AliasLines, classifier: CommandClassifier, shapes: CommandShape, starting: StartingReaders, probes: ReaderProbes, labels: ActivityLabel) -> None:
        self.outputs, self.entries, self.suggestions, self.readers, self.aliases = outputs, entries, suggestions, readers, aliases
        self.classifier, self.shapes, self.starting, self.probes, self.labels = classifier, shapes, starting, probes, labels

    def drafts(self, agent: Agent) -> tuple[ReaderDraft, ...]:
        if not agent.is_main() or not agent.session:
            return ()
        suggestions = self.suggestion_times()
        ended = [output for output in [*self.outputs.unannounced(agent.session), *self.outputs.watched(agent.session)] if output.moved and output.ended]
        return tuple(draft for output in ended if (draft := self.draft(output, agent.session, suggestions)) is not None)

    def suggestion_times(self) -> dict[str, float]:
        retired = [self.entries.project_values(key, name) for key, name in RETIRED_KEYS.items()]
        return {part: seconds for record in [*retired, self.suggestions.suggestion_times()] for part, seconds in record.items()}

    def draft(self, output: CommandOutput, session: str, suggestions: dict[str, float]) -> ReaderDraft | None:
        hand_read = self.hand_reads(output, session) >= HAND_READS
        part = next((part for part in Chain.self_parts(output.command) if self.earns(part, hand_read)), "")
        if not part:
            return None
        name = self.shapes.command_name(part)
        files = OutputFiles(Path(output.folder))
        reader = self.starting.filled(CommandPart.plain(part, self.classifier).classification, name, files.lines() if files.is_stored() else [])
        if reader is not None and self.readers.plugin_aliases_read(reader):
            return None
        later_runs = self.outputs.part_run_count(name, datetime.fromtimestamp(suggestions[name], timezone.utc)) if name in suggestions else 0
        return ReaderDraft(output.row_id, name, self.reader_command(reader, name), name in suggestions, later_runs)

    def earns(self, part: str, hand_read: bool) -> bool:
        alias = self.aliases.running(part)
        if Chain.is_journal(part) or alias is not None and alias.plugin or self.is_read_well(part):
            return False
        return hand_read or StartingReaders.starting(CommandPart.plain(part, self.classifier).classification) is not None

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
