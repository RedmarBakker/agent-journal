from dataclasses import dataclass


@dataclass(frozen=True)
class Wrapper:
    """A command that runs the command after it, as timeout or uv run do: the subcommand it needs, the flags that take a value, the values it takes before the command, whether it takes NAME=value assignments, and the word that ends its own options."""

    subcommand: str = ""
    value_flags: frozenset[str] = frozenset()
    leading_values: int = 0
    assignments: bool = False
    until: str = ""

    @classmethod
    def parsed(cls, rows: dict, name: str) -> "Wrapper":
        data = rows[name]
        while "same_as" in data:
            data = rows[data["same_as"]]
        return cls(subcommand=data.get("subcommand", ""), value_flags=frozenset(data.get("value_flags", ())), leading_values=data.get("leading_values", 0),
                   assignments=bool(data.get("assignments")), until=data.get("until", ""))

    def is_wrapping(self, tokens: list[str]) -> bool:
        return not self.subcommand or tokens[1:2] == [self.subcommand]

    def wrapped(self, tokens: list[str]) -> list[str]:
        tokens = tokens[2:] if self.subcommand else tokens[1:]
        while tokens and tokens[0].startswith("-") and tokens[0] != self.until:
            tokens = tokens[2:] if tokens[0] in self.value_flags else tokens[1:]
        tokens = tokens[1:] if self.until and tokens[:1] == [self.until] else tokens
        while tokens and self.assignments and "=" in tokens[0]:
            tokens = tokens[1:]
        return tokens[self.leading_values:]
