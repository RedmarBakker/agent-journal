import re
from dataclasses import dataclass

LOOP = re.compile(r"^\s*(until|while)\s+(.+?)\s*[;\n]\s*do\s+sleep\s+\d+(?:\.\d+)?\s*[;\n]\s*done\s*$", re.DOTALL)
PROCESS_END = re.compile(r"^!\s*(?:pgrep\s+-f\s+(\S+)|kill\s+-0\s+(\S+))$")
NEGATION = "! "
COMPOUND = re.compile(r"&&|\|\||;")


@dataclass(frozen=True)
class SleepLoop:
    """A shell line that is a loop whose body is only a sleep: a wait on the script that ends it, and what the wait is called."""

    script: str
    title: str

    @staticmethod
    def matches(line: str) -> bool:
        return bool(LOOP.match(line))

    @classmethod
    def parsed(cls, line: str) -> "SleepLoop":
        keyword, condition = LOOP.match(line).groups()
        script = condition if keyword == "until" else cls.negated(condition)
        return cls(script, cls.wait_title(script))

    @staticmethod
    def negated(condition: str) -> str:
        if condition.startswith(NEGATION) and not COMPOUND.search(condition):
            return condition.removeprefix(NEGATION).strip()
        return f"{NEGATION}{{ {condition}; }}" if COMPOUND.search(condition) else f"{NEGATION}{condition}"

    @staticmethod
    def wait_title(script: str) -> str:
        process = PROCESS_END.match(script)
        if process:
            return f"{process[1]} ends" if process[1] else f"process {process[2]} ends"
        return f"`{script}` passes"
