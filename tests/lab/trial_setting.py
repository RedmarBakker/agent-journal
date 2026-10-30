from collections.abc import Mapping
from dataclasses import dataclass

from journal.support.option import USER, Option
from tests.lab.design import Design


@dataclass(frozen=True)
class TrialSetting:
    """A user-owned switch used to compare a candidate with its off-by-default path."""

    option: Option
    owner: str

    def __post_init__(self) -> None:
        if not isinstance(self.option, Option) or not isinstance(self.option.key, str) or not all(part.strip() for part in self.option.key.split(".", 1)):
            raise ValueError("a trial setting needs a declared feature option")
        if self.option.setter != USER:
            raise ValueError("a trial setting must be user-controlled")
        if self.option.option_type != "switch" or type(self.option.default) is not bool or self.option.default:
            raise ValueError("a trial setting must be a switch whose default is off")
        if not isinstance(self.owner, str) or not self.owner.strip() or "\n" in self.owner or "\r" in self.owner:
            raise ValueError("a trial setting needs its owner's name")

    def designs(self, baseline_name: str, candidate_name: str, common_settings: Mapping[str, object]) -> tuple[Design, Design]:
        if not isinstance(baseline_name, str) or not baseline_name.strip() or not isinstance(candidate_name, str) or not candidate_name.strip() or baseline_name == candidate_name:
            raise ValueError("a trial needs distinct names for designs A and B")
        if not isinstance(common_settings, Mapping):
            raise ValueError("common trial settings must be a mapping")
        if self.option.key in common_settings:
            raise ValueError("the trial setting must be absent from common settings")
        baseline = dict(common_settings)
        candidate = dict(common_settings)
        baseline[self.option.key], candidate[self.option.key] = False, True
        return Design.from_mapping(baseline_name, baseline), Design.from_mapping(candidate_name, candidate)

    def manifest(self) -> dict[str, object]:
        return {"key": self.option.key, "owner": self.owner, "default": False, "candidate": True}
