from dataclasses import asdict, dataclass, fields
from typing import ClassVar


@dataclass(frozen=True)
class Operation:
    """What a tool call does, as its provider decoded it from the program's own tool and input: the journal reads the operation, never the tool's name."""

    operation_type: ClassVar[str]

    def line(self) -> str:
        return ""

    def shell_program(self) -> str:
        return ""

    def line_with_shell(self) -> str:
        return self.line()

    def writes(self) -> bool:
        return False

    def target_paths(self) -> tuple[str, ...]:
        return ()

    def read_paths(self) -> tuple[str, ...]:
        return ()

    def file_lines(self) -> int:
        return 0

    def changed_lines(self) -> tuple[int, int]:
        return (0, 0)

    def activity(self) -> str:
        return ""

    def loaded_skill(self) -> str:
        return ""

    def as_data(self) -> dict:
        return {"kind": self.operation_type, **asdict(self)}

    @classmethod
    def parsed(cls, data: dict) -> "Operation":
        return cls(**{field.name: tuple(data[field.name]) if isinstance(data.get(field.name), list) else data.get(field.name, field.default) for field in fields(cls)})
