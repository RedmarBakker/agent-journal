import hashlib
import json
from dataclasses import dataclass

from journal.features.organization.support.evidence_requirement import EvidenceRequirement


@dataclass(frozen=True)
class DefinitionOfDone:
    """A domain's readable completion criterion and the evidence that can satisfy it."""

    criterion: str
    evidence: EvidenceRequirement
    target: str

    @property
    def version(self) -> str:
        return hashlib.sha256(json.dumps(self.data(), sort_keys=True, separators=(",", ":")).encode()).hexdigest()[:16]

    def data(self) -> dict[str, str]:
        return {"criterion": self.criterion, "evidence": self.evidence.value, "target": self.target}

    @classmethod
    def from_data(cls, data: dict | None) -> "DefinitionOfDone | None":
        if data is None:
            return None
        return cls(str(data["criterion"]), EvidenceRequirement(data["evidence"]), str(data["target"]))
