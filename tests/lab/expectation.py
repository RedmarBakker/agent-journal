from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum

from tests.lab.business_type import freeze


@dataclass(frozen=True)
class Expectation:
    id: str
    description: str
    table: str
    target: str
    field: str
    equals: object

    @classmethod
    def read(cls, data: Mapping[str, object]) -> "Expectation":
        fields = tuple(data.get(key) for key in ("id", "description", "table", "target", "field"))
        if not all(isinstance(value, str) and value.strip() for value in fields) or "equals" not in data:
            raise ValueError("an expectation needs id, description, table, target, field and equals")
        return cls(*fields, freeze(data["equals"]))

    def matches(self, row: object | None) -> bool:
        if row is None:
            return False
        value = getattr(row, self.field)
        return getattr(value, "value", value) == self.equals
