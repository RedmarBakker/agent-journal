from dataclasses import dataclass


@dataclass(frozen=True)
class Index:
    """An index of one table: its name, the columns it orders by, and whether each value may stand once only."""

    name: str
    table: str
    columns: str
    unique: bool = False

    def sql(self) -> str:
        type_name = "UNIQUE INDEX" if self.unique else "INDEX"
        return f"CREATE {type_name} {self.name} ON {self.table} ({self.columns})"
