import time

# the most a fresh measure may differ from the one kept before it is taken
TOLERANCE_SECONDS = 1.0


class ClockOffset:
    """How far the team server's clock runs from this machine's, measured from the server's time in each answer the sync hands in and sent with each push; it moves only when a measure differs by more than a second, since one that jitters by the answer's latency would let two writes a few milliseconds apart swap order on the server."""

    def __init__(self) -> None:
        self.seconds = 0.0

    def measured(self, server_time: float) -> None:
        offset = server_time - time.time()
        if abs(offset - self.seconds) > TOLERANCE_SECONDS:
            self.seconds = offset
