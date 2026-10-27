from dataclasses import dataclass

from journal.features.shell.support.ended_output import EndedOutput
from journal.features.shell.support.output_view import OutputView
from journal.features.shell.support.reader import Reader
from journal.features.shell.support.reader_draft import ReaderDraft
from journal.features.shell.support.titled_run import TitledRun
from journal.models.alias import Alias
from journal.models.reader_report import ReaderReport
from journal.support.moment import Moment


@dataclass(frozen=True)
class ShellData:
    """The shell feature's reading: the agent's commands running in the background and since when, those that ended there not yet reported, the readers drafted for the runs that ended and how many were said this session, those reported but not yet read with the agent's tool uses now and when it was last informed of an ending, the shapes of its last reads of outputs by hand, the project's readers, the reader and alias tips already sent, what the agent's watched output shows, the project's aliases, the folder its environment works in, and the reader reports whose dismissal a verifier found unsound, until their reader is written anew, its background runs that have printed nothing for a while, and the title each of its running cards shows."""

    background: tuple[int, ...]
    backgrounded_at: float
    unannounced: tuple[EndedOutput, ...]
    unread: tuple[EndedOutput, ...]
    tool_uses: int
    last_ending_line: Moment
    output_reads: tuple[str, ...]
    readers: tuple[Reader, ...]
    tipped: tuple[str, ...]
    watch: OutputView
    aliases: tuple[Alias, ...]
    home: str
    uncut_verbs: tuple[str, ...] = ()
    locked_readers: tuple[str, ...] = ()
    reader_drafts: tuple[ReaderDraft, ...] = ()
    draft_count: int = 0
    titled_runs: tuple[TitledRun, ...] = ()
    recent_runs: tuple[TitledRun, ...] = ()
