from dataclasses import dataclass


@dataclass(frozen=True)
class Wrapper:
    """A command that runs the command after it, as timeout or uv run do: the subcommands it needs, a word or two each, the flags that take a value, before its subcommand or after it, the values it takes before the command, whether it takes NAME=value assignments, the word that ends its own options, the flags that make it look a command up instead of running it, as command -v does, the text its first value must hold when that value is code, as perl -e 'alarm 60; exec @ARGV' is, and whether all it does is limit the time of the command it runs."""

    subcommands: tuple[str, ...] = ()
    value_flags: frozenset[str] = frozenset()
    leading_values: int = 0
    assignments: bool = False
    options_end: str = ""
    code_contains: str = ""
    lookup_flags: frozenset[str] = frozenset()
    limits_time: bool = False

    @classmethod
    def parsed(cls, rows: dict, name: str) -> "Wrapper":
        data = rows[name]
        while "same_as" in data:
            data = rows[data["same_as"]]
        return cls(subcommands=tuple(data.get("subcommands", ())), value_flags=frozenset(data.get("value_flags", ())), leading_values=data.get("leading_values", 0),
                   assignments=bool(data.get("assignments")), options_end=data.get("until", ""), code_contains=data.get("code_contains", ""),
                   lookup_flags=frozenset(data.get("lookup_flags", ())), limits_time=bool(data.get("limits_time")))

    def wrapped(self, tokens: list[str]) -> list[str]:
        if tokens[1:2] and tokens[1] in self.lookup_flags:
            return []
        tokens = self.past_options(tokens[1:])
        subcommand_tokens = next((split for split in (subcommand.split() for subcommand in self.subcommands) if tokens[:len(split)] == split), None)
        if self.subcommands and subcommand_tokens is None:
            return []
        tokens = self.past_options(tokens[len(subcommand_tokens or ()):])
        if self.options_end and self.options_end in tokens:
            tokens = tokens[tokens.index(self.options_end) + 1:]
        while tokens and self.assignments and "=" in tokens[0]:
            tokens = tokens[1:]
        if self.code_contains and not (tokens and self.code_contains in tokens[0]):
            return []
        return tokens[self.leading_values:]

    def is_wrapper_flag(self, token: str) -> bool:
        return token.startswith("-") and token != self.options_end and token not in self.subcommands

    def past_options(self, tokens: list[str]) -> list[str]:
        while tokens and self.is_wrapper_flag(tokens[0]):
            tokens = tokens[2:] if tokens[0] in self.value_flags else tokens[1:]
        return tokens
