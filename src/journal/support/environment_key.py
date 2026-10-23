from uuid import uuid4


class EnvironmentKey:
    """A new environment's key: random, never reused, and never changed once it is made."""

    @staticmethod
    def random() -> str:
        return uuid4().hex
