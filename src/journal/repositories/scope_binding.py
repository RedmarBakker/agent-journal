from contextvars import ContextVar

from journal.repositories.origin import Origin

CURRENT: ContextVar[Origin] = ContextVar("origin")


class ScopeBinding:
    """The origin a block of work is in, set as the block is entered and put back as it is left."""

    def __init__(self, origin: Origin) -> None:
        self.origin = origin

    def __enter__(self) -> None:
        self.token = CURRENT.set(self.origin)

    def __exit__(self, *raised: object) -> None:
        CURRENT.reset(self.token)
