import json
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class RecordedFault:
    """A fault as the fault log keeps it: when, where it happened, its type, its first words, its frames by file, function and line, and the journal's version."""

    time: float
    place: str
    fault_type: str
    text: str
    frames: tuple[dict, ...]
    version: str

    @classmethod
    def read(cls, line: str) -> "RecordedFault":
        fields = json.loads(line)
        return cls(fields["time"], fields["place"], fields["fault_type"], fields["text"], tuple(fields["frames"]), fields["version"])

    def line(self) -> str:
        return json.dumps({**asdict(self), "frames": list(self.frames)})
