import io
import queue


class StreamedOutput(io.StringIO):
    """A command's standard output that keeps what it printed, as any captured output does, and hands each piece on to a queue as it is printed, so a reply can stream it before the command ends."""

    def __init__(self, output_queue: queue.Queue) -> None:
        super().__init__()
        self.output_queue = output_queue

    def write(self, text: str) -> int:
        self.output_queue.put(text)
        return super().write(text)
