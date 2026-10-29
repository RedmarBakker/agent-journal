from dataclasses import dataclass


@dataclass(frozen=True)
class ContractProblem:
    """One thing wrong in a contract file, in plain words: the file it is in, the rule it breaks and what to change."""

    path: str
    rule: str
    message: str
    severity: str = "error"

    def is_error(self) -> bool:
        return self.severity == "error"
