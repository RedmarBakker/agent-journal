from dataclasses import dataclass

from journal.features.messages.support.peer_question import PeerQuestion


@dataclass(frozen=True)
class MessagesData:
    """The messages feature's reading: the unread messages, the read ones not answered and the folders of their files, the questions other agents asked it that it has not answered, the colleagues' comments it has not read, and the messages it read in the tool use in hand and has not answered."""

    unread: tuple[int, ...]
    unanswered: tuple[int, ...]
    unanswered_files: tuple[str, ...]
    peer_questions: tuple[PeerQuestion, ...]
    unread_comments: tuple[int, ...] = ()
    tool_use_reads: tuple[int, ...] = ()
