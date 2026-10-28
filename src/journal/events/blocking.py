import inspect
from enum import Enum


class Blocking(Enum):
    """Why a listener runs before the hook answers, when it does: its result is part of the answer, or it writes a row the agent's next decision reads. A listener declares it, or a property that answers it, or leaves it out and runs after the answer."""

    ANSWER = "answer"
    NEXT_DECISION = "next decision"

    @classmethod
    def check(cls, listener_class: type) -> None:
        declared = inspect.getattr_static(listener_class, "blocking", None)
        if declared is not None and not isinstance(declared, (cls, property)):
            raise TypeError(f"{listener_class.__name__}.blocking is {declared!r}: a listener that runs before the answer says why with a Blocking, and one that does not leaves it out")
