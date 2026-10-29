from dataclasses import dataclass


@dataclass(frozen=True)
class ProcessUsage:
    """What an agent's processes take of the machine: their processor share in percent of one processor and their resident memory in bytes; several groups add up."""

    cpu_percent: float
    resident_bytes: int

    @classmethod
    def parsed(cls, data: dict) -> "ProcessUsage":
        return cls(float(data["cpu_percent"]), int(data["resident_bytes"]))

    @classmethod
    def total(cls, samples: list["ProcessUsage"]) -> "ProcessUsage":
        return cls(sum(sample.cpu_percent for sample in samples), sum(sample.resident_bytes for sample in samples))
