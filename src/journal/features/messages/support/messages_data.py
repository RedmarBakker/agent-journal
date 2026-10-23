from dataclasses import dataclass

from journal.features.messages.support.peer_question import PeerQuestion


@dataclass(frozen=True)
class MessagesData:
    """The messages feature's reading: the unread messages, the read ones not answered and the folders of their files, the tool use the inbox reminder counts from, the newest message's coming or the inbox last named since, how often the unread were named since the newest arrived, its own tool uses while a read message stays unanswered, the questions other agents asked it that it has not answered, the colleagues' comments it has not read, and the messages it read in the tool use in hand and has not answered."""

    unread: tuple[int, ...]
    unanswered: tuple[int, ...]
    unanswered_files: tuple[str, ...]
    inbox_tool_uses: int
    uses_unanswered: int
    peer_questions: tuple[PeerQuestion, ...]
    unread_comments: tuple[int, ...] = ()
    tool_use_reads: tuple[int, ...] = ()
