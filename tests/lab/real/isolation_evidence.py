from dataclasses import dataclass


@dataclass(frozen=True)
class IsolationEvidence:
    """The OS boundary and observer claims required to admit one isolated run."""

    run_id: str
    root: str
    writable_paths: tuple[str, ...]
    process_scope_id: str
    observer_id: str
    filesystem_boundary: bool
    process_boundary: bool
    write_observer_active: bool
    stop_on_escape: bool
    denied_writes: int = 0
    escaped_writes: int = 0

    def __post_init__(self) -> None:
        if not self.run_id or not self.process_scope_id or not self.observer_id:
            raise ValueError("isolation evidence needs run, process and observer identities")
        if any(not path.startswith("/") for path in (self.root, *self.writable_paths)):
            raise ValueError("isolation evidence paths must be absolute")
        if any(type(value) is not bool for value in (self.filesystem_boundary, self.process_boundary,
                                                      self.write_observer_active, self.stop_on_escape)):
            raise ValueError("isolation boundary claims must be explicit booleans")
        if type(self.denied_writes) is not int or self.denied_writes < 0 or type(self.escaped_writes) is not int or self.escaped_writes < 0:
            raise ValueError("write observer counts must be non-negative whole numbers")

    def to_document(self) -> dict[str, object]:
        return {"run_id": self.run_id, "root": self.root, "writable_paths": list(self.writable_paths),
                "process_scope_id": self.process_scope_id, "observer_id": self.observer_id,
                "filesystem_boundary": self.filesystem_boundary, "process_boundary": self.process_boundary,
                "write_observer_active": self.write_observer_active, "stop_on_escape": self.stop_on_escape,
                "denied_writes": self.denied_writes, "escaped_writes": self.escaped_writes}
