from dataclasses import dataclass, field


@dataclass(frozen=True)
class TableRow:
    """One row of the command table, a program, a subcommand or an option: the kind it gives (none keeps the kind above it), the effects it adds, whether it leaves the meaning uncertain, the rows below it and the flags that take the word after them."""

    kind: str = ""
    effects: tuple[str, ...] = ()
    uncertain: bool = False
    subcommands: dict[str, "TableRow"] = field(default_factory=dict)
    modifiers: dict[str, "TableRow"] = field(default_factory=dict)
    value_flags: frozenset[str] = frozenset()

    @classmethod
    def parsed(cls, rows: dict, name: str) -> "TableRow":
        data = rows[name]
        while "same_as" in data:
            data = rows[data["same_as"]]
        base = data.get("base", data)
        subcommand_rows = data.get("subcommands", {})
        option_rows = data.get("modifiers", {})
        return cls(kind=base.get("kind", ""), effects=tuple(base.get("effects", ())), uncertain=bool(base.get("uncertain")),
                   subcommands={word: cls.parsed(subcommand_rows, word) for word in subcommand_rows}, modifiers={flag: cls.parsed(option_rows, flag) for flag in option_rows},
                   value_flags=frozenset(data.get("value_flags", ())))
