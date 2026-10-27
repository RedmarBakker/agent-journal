import json
from dataclasses import dataclass

PLACEHOLDER_MARK = "<"


@dataclass(frozen=True)
class HealthCheck:
    """A plugin manifest's health block: the variable that hands each service the path of its own health socket, the line written to it, and the answer it gives, a value in angle brackets standing for anything; none declared when the variable is empty."""

    socket_env: str = ""
    request: str = ""
    answer: str = ""

    @classmethod
    def parsed(cls, data: dict) -> "HealthCheck":
        return cls(**data)

    @property
    def is_declared(self) -> bool:
        return bool(self.socket_env)

    def is_answer(self, line: str) -> bool:
        try:
            given = json.loads(line)
        except json.JSONDecodeError:
            return False
        wanted = json.loads(self.answer)
        return isinstance(given, dict) and all(given.get(key) == value for key, value in wanted.items() if not str(value).startswith(PLACEHOLDER_MARK))
