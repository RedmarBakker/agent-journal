from pathlib import Path

from journal.models.message import Message
from journal.repositories.messages import Messages
from journal.support.actor import Actor
from journal.support.rejection import Rejection
from journal.sync.attachments import Attachments


class MessageFiles:
    """The files an agent sends with a message: each is read before anything is written, then copied into the message's files folder as a user's attachment is, and the message lists it."""

    def __init__(self, messages: Messages, attachments: Attachments) -> None:
        self.messages, self.attachments = messages, attachments

    @staticmethod
    def read(paths: list[str]) -> dict[str, bytes]:
        files: dict[str, bytes] = {}
        for path in paths:
            file = Path(path).expanduser()
            if not file.is_file():
                raise Rejection(f"{path} is not a file: nothing was sent")
            files[file.name] = file.read_bytes()
        return files

    def attached(self, message: Message, files: dict[str, bytes], actor: Actor) -> Message:
        names = tuple(self.attachments.store(Message.table(), message.row_id, name, data) for name, data in files.items())
        return self.messages.save(message.with_(files=(*message.files, *names)), actor) if names else message
