from enum import Enum

from journal.engine.nudge import Nudge
from tests.full_project import MAIN
from journal.support.researcher_session import ResearcherSession
from tests.in_process import get_answer
from tests.stories.builder.main_session import MAIN_SESSION
from tests.stories.builder.worker_steps import worker_session


class StoryChecks:
    """The checks a story makes on what its last step brought: what the agent was told, by registry key and values, whether the hook let it through, whether the command passed, the stack and the rows, read through the API; a failing check says what was lines instead and the stack."""

    def expect_agent_told(self, nudge: Nudge, **values) -> None:
        self.expect_told_to(self.scoped_session(), nudge, values)

    def expect_main_told(self, nudge: Nudge, **values) -> None:
        self.expect_told_to(MAIN_SESSION, nudge, values)

    def expect_told_to(self, session: str, nudge: Nudge, values: dict) -> None:
        assert any(lines.matches(nudge.key, values) and lines.session == session for lines in self.said), f"{session} not told {nudge.key} {values}; {self.account()}"

    def expect_worker_told(self, worker: int, nudge: Nudge, **values) -> None:
        self.expect_told_to(worker_session(worker), nudge, values)

    def expect_agent_not_told(self, nudge: Nudge) -> None:
        self.expect_not_told_to(self.scoped_session(), nudge)

    def expect_main_not_told(self, nudge: Nudge) -> None:
        self.expect_not_told_to(MAIN_SESSION, nudge)

    def expect_not_told_to(self, session: str, nudge: Nudge) -> None:
        assert not any(lines.key == nudge.key and lines.session == session for lines in self.said), f"{session} told {nudge.key}; {self.account()}"

    def expect_agent_told_nothing(self) -> None:
        assert not self.said, f"told something; {self.account()}"

    def expect_refused(self, nudge: Nudge, **values) -> None:
        assert self.verdict is not None and self.verdict.refused(), f"let through; {self.account()}"
        self.expect_agent_told(nudge, **values)

    def expect_allowed(self) -> None:
        assert self.verdict is not None and not self.verdict.refused(), f"refused; {self.account()}"

    def expect_command_passed(self) -> None:
        assert self.command is not None and self.command.code == 0, f"the command was refused: {self.command.error or self.command.text if self.command else ''}"

    def expect_command_refused(self) -> None:
        assert self.command is not None and self.command.code != 0, f"the command passed: {self.command.text if self.command else ''}"

    def expect_stack(self, *states: type) -> None:
        stack = self.stack()
        assert stack == [state.name for state in states], f"the stack is {stack}; told {[line.key for line in self.said]}"

    def expect_end(self, *states: type) -> None:
        self.end_stack = list(states)

    def expect_task_in(self, environment: str, n: int, state: str) -> None:
        states = self.task_states_in(environment)
        assert states.get(n) == state, f"task {n} in {environment} is {states.get(n)}, not {state}"

    def expect_task_not_in(self, environment: str, n: int) -> None:
        assert n not in self.task_numbers_in(environment), f"task {n} is still in {environment}"

    def expect_message(self, n: int, **fields) -> None:
        self.expect_row("messages", n, fields)

    def expect_newest_agent_message(self, text: str) -> None:
        agent_rows = [row for row in get_answer(self.app, "/journal/messages", MAIN)[1]["rows"] if row.get("author") == "agent"]
        newest = max(agent_rows, key=lambda row: row["id"]) if agent_rows else {}
        assert newest.get("text") == text, f"the agent's newest message is {newest.get('text')!r}, not {text!r}"

    def expect_agent_messages(self, count: int) -> None:
        agent_messages = [row for row in get_answer(self.app, "/journal/messages", MAIN)[1]["rows"] if row.get("author") == "agent"]
        assert len(agent_messages) == count, f"the chat holds {len(agent_messages)} messages of the agent, not {count}"

    def expect_setting(self, option, value: object) -> None:
        stored = self.setting(option)
        assert stored == value, f"{option.key} is {stored!r}, not {value!r}"

    def expect_task_count(self, count: int) -> None:
        self.expect_row_count("tasks", count)

    def expect_plan_count(self, count: int) -> None:
        self.expect_row_count("plans", count)

    def expect_question_count(self, count: int) -> None:
        self.expect_row_count("questions", count)

    def expect_row_count(self, table: str, count: int) -> None:
        rows = get_answer(self.app, f"/journal/{table}", MAIN)[1]["rows"]
        assert len(rows) == count, f"{len(rows)} {table} through the API, not {count}"

    def expect_task(self, n: int, **fields) -> None:
        self.expect_row("tasks", n, fields)

    def expect_worker(self, n: int, **fields) -> None:
        self.expect_row("workers", n, fields)

    def expect_plan(self, n: int, **fields) -> None:
        self.expect_row("plans", n, fields)

    def expect_row(self, table: str, n: int, fields: dict) -> None:
        row = self.api_row(table, n)
        expected_fields = {name: value.value if isinstance(value, Enum) else value for name, value in fields.items()}
        row_fields = {name: row.get(name) for name in expected_fields}
        assert row_fields == expected_fields, f"{table} {n} has {row_fields}, not {expected_fields}"

    def expect_worker_stack(self, worker: int, *states: type) -> None:
        stack = self.session_stack(worker_session(worker))
        assert stack == [state.name for state in states], f"worker {worker}'s stack is {stack}; told {[line.key for line in self.said]}"

    def expect_subagent_stack(self, subagent: str, *states: type) -> None:
        stack = self.session_stack(ResearcherSession.joined(MAIN_SESSION, subagent))
        assert stack == [state.name for state in states], f"subagent {subagent}'s stack is {stack}; told {[line.key for line in self.said]}"

    def stack(self) -> list[str]:
        return self.session_stack(self.scoped_session())

    def session_stack(self, session: str) -> list[str]:
        agents = [row["id"] for row in get_answer(self.app, "/journal/agents", MAIN)[1]["rows"] if row.get("session") == session]
        return [state["name"] for state in reversed(self.api_row("agents", max(agents))["stack"])] if agents else []

    def newest(self, table: str) -> int:
        return max(row["id"] for row in get_answer(self.app, f"/journal/{table}", MAIN)[1]["rows"])

    def api_row(self, table: str, n: int) -> dict:
        rows = get_answer(self.app, f"/journal/{table}?ids={n}", MAIN)[1]["rows"]
        assert rows, f"no {table} row {n} through the API"
        return rows[0]

    def account(self) -> str:
        return f"told {[(lines.session, lines.key, lines.values) for lines in self.said]}; stack {self.stack()}"

    def expect_command_line(self, *parts: str) -> str:
        lines = [line for line in self.command.text.splitlines() if all(part in line for part in parts)]
        assert lines, f"no line of the command says {', '.join(parts)}: {self.command.text}"
        return lines[0]
