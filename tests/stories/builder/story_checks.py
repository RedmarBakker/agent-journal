from enum import Enum

from journal.engine.nudge import Nudge
from tests.full_project import MAIN
from journal.support.researcher_session import ResearcherSession
from tests.in_process import get_answer
from tests.stories.builder.worker_steps import worker_session
from journal.features.workers.feature import Workers
from tests.stories.builder.mode_floor import ModeFloor


class StoryChecks:
    """The checks a story makes on what its last step brought: what the agent was told, by registry key and values, whether the hook let it through, whether the command passed, the stack and the rows, read through the API; a failing check says what was lines instead and the stack."""

    def expect_agent_told(self, nudge: Nudge, **values) -> None:
        self.expect_told_to(self.scoped_session(), nudge, values)

    def expect_main_told(self, nudge: Nudge, **values) -> None:
        self.expect_told_to(self.main_session(), nudge, values)

    def expect_told_to(self, session: str, nudge: Nudge, values: dict) -> None:
        assert any(lines.matches(nudge.key, values) and lines.session == session for lines in self.said), f"{session} not told {nudge.key} {values}; {self.account()}"

    def expect_worker_told(self, worker: int, nudge: Nudge, **values) -> None:
        self.expect_told_to(worker_session(worker), nudge, values)

    def expect_agent_not_told(self, nudge: Nudge, **values) -> None:
        self.expect_not_told_to(self.scoped_session(), nudge, values)

    def told_number(self, nudge: Nudge, name: str) -> int:
        return int(next(line.values[name] for line in reversed(self.said) if line.key == nudge.key))

    def expect_main_stack(self, *states: type) -> None:
        stack = self.session_stack(self.main_session())
        assert stack == [state.name for state in states], f"the main agent's stack is {stack}"

    def expect_main_not_told(self, nudge: Nudge) -> None:
        self.expect_not_told_to(self.main_session(), nudge, {})

    def expect_not_told_to(self, session: str, nudge: Nudge, values: dict) -> None:
        assert not any(lines.matches(nudge.key, values) and lines.session == session for lines in self.said), f"{session} told {nudge.key} {values}; {self.account()}"

    def expect_agent_told_nothing(self) -> None:
        assert not self.said, f"told something; {self.account()}"

    def expect_refused(self, nudge: Nudge, **values) -> None:
        assert self.verdict is not None and self.verdict.refused(), f"let through; {self.account()}"
        self.expect_agent_told(nudge, **values)

    def expect_main_refused(self, nudge: Nudge, **values) -> None:
        assert self.verdict is not None and self.verdict.refused(), f"let through; {self.account()}"
        self.expect_main_told(nudge, **values)

    def expect_allowed(self) -> None:
        assert self.verdict is not None and not self.verdict.refused(), f"refused; {self.account()}"

    def expect_shell_text(self, *parts: str) -> None:
        assert all(part in self.shell_text for part in parts), f"the command showed {self.shell_text!r}, not {parts}"

    def expect_shell_text_without(self, part: str) -> None:
        assert part not in self.shell_text, f"the command showed {part!r}: {self.shell_text!r}"

    def expect_shell_exit(self, code: int) -> None:
        assert self.shell_exit == code, f"the command ended {self.shell_exit}, not {code}"

    def expect_no_new_output(self) -> None:
        assert not self.shell_outputs, f"the command kept output {self.newest_output()}"

    def expect_new_output(self) -> None:
        assert self.shell_outputs, "the command kept no output"

    def expect_output_count(self, count: int) -> None:
        assert self.output_count() == count, f"{self.output_count()} outputs are kept, not {count}"

    def expect_command_passed(self) -> None:
        assert self.command is not None and self.command.code == 0, f"the command was refused: {self.command.error or self.command.text if self.command else ''}"

    def expect_command_text(self, part: str) -> None:
        printed = f"{self.command.text}{self.command.error}" if self.command else ""
        assert part in printed, f"the command printed {printed!r}, not {part!r}"

    def expect_command_text_without(self, part: str) -> None:
        printed = f"{self.command.text}{self.command.error}" if self.command else ""
        assert part not in printed, f"the command printed {part!r}: {printed!r}"

    def expect_command_lines_in_order(self, *parts: str) -> None:
        lines = self.command.text.splitlines()
        places = [next((k for k, line in enumerate(lines) if part in line), -1) for part in parts]
        assert -1 not in places and places == sorted(places), f"the command printed {', '.join(parts)} out of this order: {self.command.text}"

    def expect_command_refused(self) -> None:
        assert self.command is not None and self.command.code != 0, f"the command passed: {self.command.text if self.command else ''}"

    def expect_stack(self, *states: type) -> None:
        stack = self.stack()
        assert stack == [self.floor().name if state is ModeFloor else state.name for state in states], f"the stack is {stack}; told {[line.key for line in self.said]}"
        self.stack_checked_at = len(self.path)

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

    def expect_change_told_to_the_viewer(self, table: str, n: int) -> None:
        changes = get_answer(self.app, "/journal/entries?since=0", MAIN)[1]
        assert (table, n) in [(change["data"].get("table"), change["data"].get("id")) for change in changes], f"no change of {table} {n} told to the viewer"

    def expect_row_count(self, table: str, count: int) -> None:
        rows = get_answer(self.app, f"/journal/{table}", MAIN)[1]["rows"]
        assert len(rows) == count, f"{len(rows)} {table} through the API, not {count}"

    def expect_task(self, n: int, **fields) -> None:
        self.expect_row("tasks", n, fields)

    def expect_task_logged(self, n: int, part: str) -> None:
        shown = self.app.console().run(["task", "show", str(n)], self.agent).text
        assert part in shown, f"task {n} has no log line holding {part!r}: {shown}"

    def expect_worker(self, n: int, **fields) -> None:
        self.expect_row("workers", n, fields)

    def expect_plan(self, n: int, **fields) -> None:
        self.expect_row("plans", n, fields)

    def expect_row_absent(self, table: str, n: int) -> None:
        rows = get_answer(self.app, f"/journal/{table}?ids={n}", MAIN)[1]["rows"]
        assert not rows, f"{table} {n} is still listed through the API: {rows[0]}"

    def expect_row(self, table: str, n: int, fields: dict) -> None:
        row = self.api_row(table, n)
        expected_fields = {name: value.value if isinstance(value, Enum) else value for name, value in fields.items()}
        row_fields = {name: row.get(name) for name in expected_fields}
        assert row_fields == expected_fields, f"{table} {n} has {row_fields}, not {expected_fields}"

    def expect_worker_stack(self, worker: int, *states: type) -> None:
        stack = self.session_stack(worker_session(worker))
        assert stack == [state.name for state in states], f"worker {worker}'s stack is {stack}; told {[line.key for line in self.said]}"

    def expect_subagent_stack(self, subagent: str, *states: type) -> None:
        stack = self.session_stack(ResearcherSession.joined(self.main_session(), subagent))
        assert stack == [state.name for state in states], f"subagent {subagent}'s stack is {stack}; told {[line.key for line in self.said]}"

    def floor(self) -> type:
        return Workers.modes.states[self.mode]

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
