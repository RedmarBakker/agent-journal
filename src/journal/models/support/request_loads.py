from collections import Counter
from dataclasses import dataclass

from journal.models.support.model_load import ModelLoad


@dataclass(frozen=True)
class RequestLoads:
    """The rows one request or hook turned into models, the bytes they held and the writes it made, counted per model, the costliest first; empty while load counting is off. A row loaded, a write and a started kilobyte loaded are a point each."""

    counts: tuple[ModelLoad, ...] = ()

    @classmethod
    def tallied(cls, rows: Counter) -> "RequestLoads":
        return cls.measured(rows, Counter(), Counter())

    @classmethod
    def measured(cls, rows: Counter, sizes: Counter, writes: Counter) -> "RequestLoads":
        model_loads = [ModelLoad(table, rows[table], sizes[table], writes[table]) for table in {*rows, *writes}]
        return cls(tuple(sorted(model_loads, key=lambda model_load: (-model_load.points(), model_load.model))))

    @classmethod
    def parsed(cls, data: dict) -> "RequestLoads":
        return cls(tuple(ModelLoad(model=stored["model"], rows=stored["rows"], bytes=stored.get("bytes", 0), writes=stored.get("writes", 0)) for stored in data.get("counts", ())))

    def points(self) -> int:
        return sum(load.points() for load in self.counts)

    def line(self) -> str:
        return ", ".join(f"{count.model} {count.points()} points: {count.rows} rows, {count.bytes} bytes, {count.writes} writes" for count in self.counts)
