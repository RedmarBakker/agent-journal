from dataclasses import dataclass

from journal.support.operation import Operation


@dataclass(frozen=True)
class SkillLoad(Operation):
    operation_type = "skill load"
    skill: str

    def loaded_skill(self) -> str:
        return self.skill
