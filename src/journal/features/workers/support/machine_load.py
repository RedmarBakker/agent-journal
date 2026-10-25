import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

MEGABYTE = 1024 * 1024
VM_STAT_SECONDS = 5
# the pages macOS can hand out at once: free, inactive and speculative (vm_stat)
FREE_PAGES = ("Pages free", "Pages inactive", "Pages speculative")


@dataclass(frozen=True)
class MachineLoad:
    """The machine's load as the orchestrator reads it: its load averages over one, five and fifteen minutes, its cores, and the memory it can hand out at once, in megabytes, read from vm_stat on macOS and MemAvailable elsewhere, 0 where neither tells it; and the load beyond what the test runs going explain, one each."""

    averages: tuple[float, float, float]
    cores: int
    free_megabytes: int

    @classmethod
    def read(cls) -> "MachineLoad":
        return cls(tuple(round(average, 1) for average in os.getloadavg()), os.cpu_count() or 1, cls.vm_free() if sys.platform == "darwin" else cls.meminfo_free())

    @staticmethod
    def vm_free() -> int:
        shown = subprocess.run(["vm_stat"], capture_output=True, text=True, timeout=VM_STAT_SECONDS).stdout
        page = re.search(r"page size of (\d+) bytes", shown)
        pages = sum(int(found[1]) for name in FREE_PAGES if (found := re.search(rf"{name}:\s+(\d+)", shown)))
        return pages * int(page[1]) // MEGABYTE if page else 0

    @staticmethod
    def meminfo_free() -> int:
        info = Path("/proc/meminfo")
        found = re.search(r"MemAvailable:\s+(\d+) kB", info.read_text()) if info.is_file() else None
        return int(found[1]) // 1024 if found else 0

    def beyond(self, runs: int) -> float:
        return round(max(self.averages[0] - runs, 0.0), 1)
