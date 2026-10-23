from dataclasses import dataclass

ORPHAN_PARENT = 1


@dataclass(frozen=True)
class JournalIdentity:
    """What a running journal says of itself at /journal/identity: its project's folder, its version, its process and the process that started it."""

    root: str
    version: str
    pid: int
    parent: int

    @classmethod
    def parsed(cls, data: dict) -> "JournalIdentity":
        return cls(str(data.get("root", "")), str(data.get("version", "")), int(data.get("pid", 0)), int(data.get("parent", 0)))

    def is_replaceable(self, version: str, parent: int) -> bool:
        replaced = self.version != version or self.parent in (parent, ORPHAN_PARENT)
        return self.pid > 0 and replaced
