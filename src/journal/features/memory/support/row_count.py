from dataclasses import dataclass

from journal.repositories.row_counts import RowCounts
from journal.support.rejection import Rejection

COMPARISONS = {"is": lambda count, number: count == number, "at_least": lambda count, number: count >= number, "at_most": lambda count, number: count <= number}
FORM = 'a condition is {"count": "<table>", "where": {"<field>": <value or [values]>}, "is" | "at_least" | "at_most": <number>}, or {"all": [...]} or {"any": [...]} of them'


@dataclass(frozen=True)
class RowCount:
    """One count a memory row's condition makes: the rows of a table whose fields have one of the values named for each, compared with a number."""

    table: str
    values: tuple[tuple[str, tuple], ...]
    comparison: str
    number: int

    @classmethod
    def read(cls, payload: dict) -> "RowCount":
        comparison_names = [name for name in COMPARISONS if name in payload]
        field_values = payload.get("where", {})
        if "count" not in payload or len(comparison_names) != 1 or not isinstance(payload[comparison_names[0]], int) or not isinstance(field_values, dict):
            raise Rejection(FORM)
        allowed_values = tuple((name, tuple(value) if isinstance(value, list) else (value,)) for name, value in field_values.items())
        RowCounts.checked(payload["count"], allowed_values)
        return cls(payload["count"], allowed_values, comparison_names[0], payload[comparison_names[0]])

    def is_true(self, counts: RowCounts) -> bool:
        return COMPARISONS[self.comparison](counts.counted(self.table, self.values), self.number)
