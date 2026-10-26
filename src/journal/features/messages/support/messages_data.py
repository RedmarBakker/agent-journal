from dataclasses import dataclass

from journal.features.messages.support.peer_question import PeerQuestion


@dataclass(frozen=True)
class MessagesData:
    """The messages feature's reading: the oldest few unread messages and how many are unread, the read ones not answered and the folders of their files, the questions other agents asked it that it has not answered, the colleagues' comments it has not read, the messages it read in the tool use in hand and has not answered, and its last message's numbers that name a row without its kind before them, each as the row it most likely is, and the rows it names with their kind that do not exist."""

    unread: tuple[int, ...]
    unanswered: tuple[int, ...]
    unanswered_files: tuple[str, ...]
    peer_questions: tuple[PeerQuestion, ...]
    unread_comments: tuple[int, ...] = ()
    unread_count: int = 0
    tool_use_reads: tuple[int, ...] = ()
    unlinked_message: int = 0
    unlinked_numbers: tuple[str, ...] = ()
    missing_message: int = 0
    missing_rows: tuple[str, ...] = ()
