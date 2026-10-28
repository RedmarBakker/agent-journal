from enum import Enum

from journal.engine.nudge import Nudge
from tests.full_project import MAIN
from tests.in_process import got


class StepChecks:
    """The checks a scenario makes on what its last step brought: what the agent was told, by registry key and values, whether the hook let it through, whether the command passed, the stack and the rows, read through the API; a failing check says what was said instead and the stack."""

    def expect_agent_told(self, nudge: Nudge, **values) -> None:
        assert any(said.matches(nudge.key, values) for said in self.said), f"not told {nudge.key} {values}; {self.account()}"

    def expect_agent_not_told(self, nudge: Nudge) -> None:
        assert not any(said.key == nudge.key for said in self.said), f"told {nudge.key}; {self.account()}"

    def expect_agent_told_nothing(self) -> None:
        assert not self.said, f"told something; {self.account()}"

    def expect_refused(self, nudge: Nudge, **values) -> None:
        assert self.verdict is not None and self.verdict.refused(), f"let through; {self.account()}"
        self.expect_agent_told(nudge, **values)

    def expect_refused_if(self, condition: bool, nudge: Nudge, **values) -> None:
        if condition:
            self.expect_refused(nudge, **values)
        else:
            self.expect_allowed()

    def expect_allowed(self) -> None:
        assert self.verdict is not None and not self.verdict.refused(), f"refused; {self.account()}"

    def expect_command_passed(self) -> None:
        assert self.command is not None and self.command.code == 0, f"the command was refused: {self.command.error or self.command.text if self.command else ''}"

    def expect_command_refused(self) -> None:
        assert self.command is not None and self.command.code != 0, f"the command passed: {self.command.text if self.command else ''}"

    def expect_stack(self, *names: str) -> None:
        shown = self.stack()
        assert shown == list(names), f"the stack is {shown}; told {[said.key for said in self.said]}"

    def expect_task(self, n: int, **fields) -> None:
        self.expect_row("tasks", n, fields)

    def expect_worker(self, n: int, **fields) -> None:
        self.expect_row("workers", n, fields)

    def expect_plan(self, n: int, **fields) -> None:
        self.expect_row("plans", n, fields)

    def expect_row(self, table: str, n: int, fields: dict) -> None:
        row = self.api_row(table, n)
        wanted = {name: value.value if isinstance(value, Enum) else value for name, value in fields.items()}
        shown = {name: row.get(name) for name in wanted}
        assert shown == wanted, f"{table} {n} has {shown}, not {wanted}"

    def stack(self) -> list[str]:
        agents = got(self.app, "/journal/agents", MAIN)[1]["rows"]
        main = [row for row in agents if row.get("session") == "s1"]
        return [state["name"] for state in reversed(self.api_row("agents", main[0]["id"])["stack"])] if main else []

    def newest(self, table: str) -> int:
        return max(row["id"] for row in got(self.app, f"/journal/{table}", MAIN)[1]["rows"])

    def api_row(self, table: str, n: int) -> dict:
        rows = got(self.app, f"/journal/{table}?ids={n}", MAIN)[1]["rows"]
        assert rows, f"no {table} row {n} through the API"
        return rows[0]

    def account(self) -> str:
        return f"told {[(said.key, said.values) for said in self.said]}; stack {self.stack()}"
