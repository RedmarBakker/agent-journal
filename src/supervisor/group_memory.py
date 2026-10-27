import subprocess

# every process with its group and its resident memory in kilobytes
PS_COMMAND = ["ps", "-A", "-o", "pgid=,rss="]
PS_TIMEOUT_SECONDS = 5
KILOBYTE = 1024


class GroupMemory:
    """The resident memory of process groups in bytes, each the sum of its processes' as ps reports them."""

    @staticmethod
    def resident(groups: set[int]) -> dict[int, int]:
        totals = dict.fromkeys(groups, 0)
        listing = subprocess.run(PS_COMMAND, capture_output=True, text=True, timeout=PS_TIMEOUT_SECONDS).stdout
        for line in listing.splitlines():
            group, kilobytes = (int(word) for word in line.split())
            if group in totals:
                totals[group] += kilobytes * KILOBYTE
        return totals
