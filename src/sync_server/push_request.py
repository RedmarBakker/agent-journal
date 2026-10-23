from dataclasses import dataclass

from sync_server.pushed_change import PushedChange


@dataclass(frozen=True)
class PushRequest:
    """A device's push: its queued changes in order, how far the server's clock is ahead of the device's, which the device measured from the server's time in its last answer, and what its pull, answered with the push, goes on from: the sequence it holds and the keys of the environments it hosts."""

    clock_offset: float
    changes: tuple[PushedChange, ...]
    sequence: int
    environment_keys: tuple[str, ...]

    @classmethod
    def parsed(cls, changes: list, clock_offset: float = 0.0, sequence: int = 0, environment_keys: tuple = ()) -> "PushRequest":
        return cls(float(clock_offset), tuple(PushedChange(**change) for change in changes), int(sequence), tuple(environment_keys))
