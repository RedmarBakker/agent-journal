import re

WRAPPER = re.compile(r"^\s*(?:perl -e ['\"](?:alarm \d+; ?)exec @ARGV['\"]|g?timeout(?: --?[a-z-]+(?:=\S+| \S+)?)* \d+[smhd]?)\s+")


class TimeLimitWrapper:
    """The time limit a command line wraps itself in, perl's alarm or timeout, which a run the journal watches needs not: the line as it reads without it."""

    @staticmethod
    def unwrapped(line: str) -> str:
        return WRAPPER.sub("", line, count=1)
