from dataclasses import dataclass

from journal.features.shell.support.ended_output import EndedOutput
from journal.features.shell.support.output_view import OutputView
from journal.features.shell.support.reader import Reader
from journal.models.alias import Alias
from journal.support.moment import Moment


@dataclass(frozen=True)
class ShellData:
    """The shell feature's reading: the agent's commands running in the background and since when, those that ended there not yet reported, the readers asked to read better since each was last written, one name per ask, those reported but not yet read with the agent's tool uses now and when it was last informed of an ending, the shapes of its last reads of outputs by hand, the project's readers, the reader and alias tips already sent, what the agent's watched output shows, the project's aliases, and the folder its environment works in."""

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
    unwatched_commands: tuple[str, ...] = ()
    watch_command: str = ""
    unread_reports: tuple[int, ...] = ()
    unfixed_reports: tuple[int, ...] = ()
