from dataclasses import dataclass


@dataclass(frozen=True)
class OpenTask:
    """A task to offer next named by its number and brief, with the plan it is next in when a plan holds it, and its state: started, blocked or open."""

    id: int
    title: str
    brief: str
    plan_id: int
    state: str = "open"

    def line(self) -> str:
        plan = f"plan {self.plan_id}: " if self.plan_id else ""
        brief = f". brief: {self.brief}" if self.brief else ""
        if self.state == "blocked":
            return f"{plan}task {self.id} is blocked: has what it waits on arrived? journal task show {self.id}"
        if self.state == "started":
            return f"{plan}task {self.id} is started next{brief}"
        return f"{plan}task {self.id} is next{brief}"
