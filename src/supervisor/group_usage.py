import os
import subprocess
from dataclasses import dataclass

# every process with its group, its resident memory in kilobytes and its share of a processor
PS_COMMAND = ["ps", "-A", "-o", "pgid=,rss=,%cpu="]
PS_TIMEOUT_SECONDS = 5
KILOBYTE = 1024


@dataclass(frozen=True)
class GroupUsage:
    """What one process group takes of the machine: the processor share of its processes summed, in percent of one processor, and their resident memory in bytes, as ps reports them."""

    cpu_percent: float
    resident_bytes: int

    @classmethod
    def sampled(cls, groups: set[int]) -> dict[int, "GroupUsage"]:
        listing = subprocess.run(PS_COMMAND, capture_output=True, text=True, timeout=PS_TIMEOUT_SECONDS, env={**os.environ, "LC_ALL": "C"}).stdout
        return cls.parsed(listing, groups)

    @classmethod
    def parsed(cls, listing: str, groups: set[int]) -> dict[int, "GroupUsage"]:
        totals = dict.fromkeys(groups, cls(0.0, 0))
        for group, kilobytes, cpu in (line.split() for line in listing.splitlines() if line.strip()):
            if int(group) in totals:
                totals[int(group)] = totals[int(group)].plus(cls(float(cpu), int(kilobytes) * KILOBYTE))
        return totals

    def plus(self, usage: "GroupUsage") -> "GroupUsage":
        return GroupUsage(self.cpu_percent + usage.cpu_percent, self.resident_bytes + usage.resident_bytes)

    def fields(self) -> dict:
        return {"cpu_percent": round(self.cpu_percent, 1), "resident_bytes": self.resident_bytes}
