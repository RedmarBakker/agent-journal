from collections.abc import Collection
from dataclasses import dataclass


@dataclass(frozen=True)
class SupervisorNarrowingRule:
    """One command a supervisor must propose or may never run on a named row."""

    command: str
    effect: str
    row_id: int | None = None

    @classmethod
    def parsed(cls, value: object, commands: Collection[str]) -> "SupervisorNarrowingRule":
        rule = cls.stored(value)
        if rule.command not in commands:
            raise ValueError("a supervisor narrowing rule must name a catalogued verb")
        return rule

    @classmethod
    def stored(cls, value: object) -> "SupervisorNarrowingRule":
        if not isinstance(value, dict):
            raise ValueError("a supervisor narrowing rule can only restrict access")
        command = value.get("command")
        effect = value.get("effect")
        if not isinstance(command, str) or not command.strip():
            raise ValueError("a supervisor narrowing rule can only require a verb to be proposed or forbid it on a named row")
        if effect == "propose" and set(value) == {"command", "effect"}:
            return cls(command, effect)
        row_id = value.get("row_id")
        if (effect != "never" or set(value) != {"command", "effect", "row_id"}
                or type(row_id) is not int or row_id < 1):
            raise ValueError("a supervisor narrowing rule can only require a verb to be proposed or forbid it on a named row")
        return cls(command, effect, row_id)

    def data(self) -> dict:
        data = {"command": self.command, "effect": self.effect}
        if self.row_id is not None:
            data["row_id"] = self.row_id
        return data
