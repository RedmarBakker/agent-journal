from collections import Counter
from dataclasses import dataclass, field


@dataclass
class LoadCounters:
    """The running counts of one request's loads: rows and their bytes per table, writes per table, and how many measurements share them, a measurement started inside another counting into the outer one."""

    rows: Counter = field(default_factory=Counter)
    sizes: Counter = field(default_factory=Counter)
    writes: Counter = field(default_factory=Counter)
    depth: int = 1
