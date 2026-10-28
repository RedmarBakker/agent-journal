from dataclasses import dataclass


@dataclass(frozen=True)
class NudgeRecord:
    """One line the nudger gave an agent, by its registry key, the values it was made with and the session it went to."""

    key: str
    values: dict
    session: str

    def matches(self, key: str, values: dict) -> bool:
        return self.key == key and {name: str(value) for name, value in values.items()}.items() <= self.values.items()
