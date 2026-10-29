from dataclasses import dataclass
from urllib.parse import parse_qs


@dataclass(frozen=True)
class ItemQuery:
    """What GET /items is asked to list: one type of item, and words its name or description holds, each absent when not given."""

    item_type: str | None
    search: str | None

    @classmethod
    def parsed(cls, query: str) -> "ItemQuery":
        fields = parse_qs(query)
        return cls(next(iter(fields.get("type", [])), None), next(iter(fields.get("search", [])), None))
