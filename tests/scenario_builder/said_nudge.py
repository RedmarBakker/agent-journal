from dataclasses import dataclass


@dataclass(frozen=True)
class SaidNudge:
    """One line the nudger gave the agent, by its registry key and the values it was made with."""

    key: str
    values: dict

    def matches(self, key: str, values: dict) -> bool:
        return self.key == key and {name: str(value) for name, value in values.items()}.items() <= self.values.items()
