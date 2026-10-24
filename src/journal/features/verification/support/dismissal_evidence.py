from pathlib import Path

from journal.features.shell.support.output_files import OutputFiles
from journal.features.shell.support.readers import Readers
from journal.models.reader_report import ReaderReport
from journal.repositories.command_outputs import CommandOutputs

# the last lines of the run's output a verifier is handed: every line a reader report's findings rest on, never a whole log
OUTPUT_LINES = 400
NO_OUTPUT = "(the run's output is not kept)"


class DismissalEvidence:
    """The brief a verifier of a reader report's dismissal is handed: all the evidence and nothing else, the report, the agent's reason, the reader as it is written and the run's output, with the one answer it gives."""

    def __init__(self, readers: Readers, outputs: CommandOutputs) -> None:
        self.readers, self.outputs = readers, outputs

    def brief(self, report: ReaderReport) -> str:
        return "\n\n".join((
            "You are a verifier the journal sent. An agent dismissed the reader report below as wrong instead of writing its reader anew. "
            "Judge, on this evidence alone, whether the agent's reason holds against the run's own output. Answer with one command and nothing else: "
            "journal verdict yes \"<reason>\" when the dismissal is sound and the report is wrong, or journal verdict no \"<reason>\" when the output contradicts the agent's reason. "
            "Every other tool is refused, and your verdict ends your session.",
            f"## The report\n\n{report.evidence()}",
            f"## The agent's reason for dismissing it\n\n{report.dismissal}",
            f"## The reader {report.reader}, as it is written\n\n{self.readers.definition(report.reader)}",
            f"## The run's output, its last {OUTPUT_LINES} lines\n\n{self.output_text(report)}",
        ))

    def output_text(self, report: ReaderReport) -> str:
        stored = self.outputs.matching(id=report.output)
        files = OutputFiles(Path(stored[0].folder)) if stored else None
        return "\n".join(files.lines()[-OUTPUT_LINES:]) if files and files.is_stored() else NO_OUTPUT
