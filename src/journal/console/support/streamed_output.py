import io
import queue


class StreamedOutput(io.StringIO):
    """A command's standard output that keeps what it printed, as any captured output does, and hands each piece on to a queue as it is printed, so a reply can stream it before the command ends."""

    def __init__(self, pieces: queue.Queue) -> None:
        super().__init__()
        self.pieces = pieces

    def write(self, text: str) -> int:
        self.pieces.put(text)
        return super().write(text)
