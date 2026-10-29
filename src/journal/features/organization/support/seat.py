from dataclasses import dataclass


@dataclass(frozen=True)
class Seat:
    """One member of an organization plan's rig: the organization id it stands for, plan, domain:<id> or role:<domain>/<id>, its pod and member id there, the Role it works as (empty for the Plan and a Domain agent), its provider, model and reasoning effort, the guidance it boots with, its skills, the tools its Role allows and whether it writes."""

    qualified: str
    pod: str
    member: str
    role: str
    provider: str
    model: str
    effort: str
    guidance: str
    skills: tuple[str, ...]
    tools: tuple[str, ...]
    writes: bool
    provider: str
    effort: str

    def logical_id(self) -> str:
        return f"{self.pod}.{self.member}"

    def agent(self) -> str:
        return f"{self.pod}-{self.member}"
