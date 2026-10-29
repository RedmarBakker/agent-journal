import json
from enum import Enum

from journal.engine.nudge import Nudge
from journal.repositories.entries import Entries
from journal.repositories.scope import Scope
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

    def expect_one_entry_of_firing(self, firing: str) -> None:
        with self.app.container.get(Scope).environment(1):
            entries = self.app.container.get(Entries)
            count = entries.counted(entries.query().filter(idempotency=f"hook:{self.scoped_session()}:PreToolUse:{firing}"))
        assert count == 1, f"firing {firing} has {count} entries, not one"

    def expect_refused_by_anything(self) -> None:
        assert self.verdict is not None and self.verdict.refused(), f"let through; {self.account()}"

    def expect_refusal_text(self, part: str) -> None:
        said = str(self.verdict.body) if self.verdict else ""
        assert part in said, f"the refusal does not say {part!r}: {said}"

    def expect_refusal_without(self, part: str) -> None:
        said = str(self.verdict.body) if self.verdict else ""
        assert part not in said, f"the refusal says {part!r}: {said}"

    def expect_newest_message_text(self, text: str) -> None:
        newest = self.api_row("messages", self.newest("messages"))
        assert newest["text"] == text, f"the newest message reads {newest['text']!r}, not {text!r}"

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

    def expect_command_line_count(self, count: int) -> None:
        lines = self.command.text.strip().splitlines()
        assert len(lines) == count, f"the command printed {len(lines)} lines, not {count}: {self.command.text}"

    def expect_viewer_passed(self) -> None:
        assert self.viewer_status < 300, f"the viewer's request was refused: {self.viewer_answer}"

    def expect_viewer_refused(self, part: str) -> None:
        assert self.viewer_status >= 300 and part in json.dumps(self.viewer_answer), f"the viewer's request answered {self.viewer_status} {self.viewer_answer}, not a refusal saying {part!r}"

    def expect_chat_marks(self, shows: str, *texts: str) -> None:
        rows = [row for row in get_answer(self.app, "/journal/messages", MAIN)[1]["rows"] if (row.get("data") or {}).get("shows") == shows]
        marks = sorted(row["text"] for row in rows)
        assert marks == sorted(texts), f"the chat's {shows} marks are {marks}, not {sorted(texts)}: {rows}"

    def expect_viewer_shows(self, name: str, value: object) -> None:
        assert self.viewer_answer.get(name) == value, f"the viewer was given {name} {self.viewer_answer.get(name)!r}, not {value!r}"

    def expect_viewer_rows(self, key: str, field: str, values: list) -> None:
        shown = [row.get(field) for row in self.viewer_answer.get(key, [])]
        assert shown == values, f"the viewer was given {key} with {field} {shown}, not {values}"

    def expect_viewer_part(self, path: tuple, value: object) -> None:
        part = self.viewer_answer
        for key in path:
            part = part[key]
        assert part == value, f"the viewer was given {part!r} at {'/'.join(map(str, path))}, not {value!r}"

    def expect_viewer_count_at_most(self, key: str, count: int) -> None:
        shown = self.viewer_answer.get(key, [])
        assert len(shown) <= count, f"the viewer was given {len(shown)} {key}, more than {count}"

    def expect_viewer_rows_newer(self, key: str, n: int) -> None:
        older = [row["id"] for row in self.viewer_answer.get(key, []) if row["id"] <= n]
        assert not older, f"the viewer was given {key} {older}, not newer than {n}"

    def expect_viewer_rows_without(self, key: str, field: str) -> None:
        holding = [row["id"] for row in self.viewer_answer.get(key, []) if field in row]
        assert not holding, f"the viewer was given {key} {holding} with their {field}"

    def expect_viewer_first_hit(self, n: int, part: str) -> None:
        first = self.viewer_answer[0] if self.viewer_answer else {}
        assert first.get("id") == n and part in first.get("text", ""), f"the viewer's first hit is {first}, not {n} holding {part!r}"

    def expect_viewer_list_count(self, count: int) -> None:
        assert len(self.viewer_answer) == count, f"the viewer was given {len(self.viewer_answer)} rows, not {count}: {self.viewer_answer}"

    def expect_viewer_count(self, key: str, count: int) -> None:
        shown = self.viewer_answer.get(key, [])
        assert len(shown) == count, f"the viewer was given {len(shown)} {key}, not {count}"

    def expect_docked_cards(self, *texts: str) -> None:
        docked = sorted(row["text"] for row in get_answer(self.app, "/journal/messages", MAIN)[1]["rows"] if (row.get("data") or {}).get("docked"))
        assert docked == sorted(texts), f"the cards docked above the chat are {docked}, not {sorted(texts)}"

    def expect_plan_titles_in(self, environment: str, *titles: str) -> None:
        shown = sorted(row["title"] for row in get_answer(self.app, "/journal/plans", {"X-Journal-Env": environment})[1]["rows"])
        assert shown == sorted(titles), f"the plans of {environment} are {shown}, not {sorted(titles)}"

    def expect_dispatch_card(self, **data) -> None:
        cards = [row.get("data") or {} for row in get_answer(self.app, "/journal/messages", MAIN)[1]["rows"] if (row.get("data") or {}).get("dispatch")]
        fields = {name: cards[-1].get(name) for name in data} if cards else {}
        assert fields == data, f"the subagent's dispatch card holds {fields}, not {data}"

    def expect_card(self, n: int, **data) -> None:
        shown = self.api_row("messages", n).get("data") or {}
        fields = {name: shown.get(name) for name in data}
        assert fields == data, f"card {n} holds {fields}, not {data}"

    def expect_tool_input_changed(self, **fields) -> None:
        changed = (self.verdict.body.get("hookSpecificOutput") or {}).get("updatedInput") or {} if self.verdict else {}
        shown = {name: changed.get(name) for name in fields}
        assert shown == fields, f"the tool's input was changed to {changed}, not to hold {fields}"

    def expect_project_file(self, path: str, *parts: str) -> None:
        file = self.app.config.root / path
        text = file.read_text() if file.is_file() else ""
        missing = [part for part in parts if part not in text]
        assert file.is_file() and not missing, f"{path} does not hold {missing}: {text[:400]!r}"

    def expect_runtime_file(self, name: str, text: str) -> None:
        file = self.app.config.home / "runtime" / name
        shown = file.read_text() if file.is_file() else ""
        assert shown == text, f"runtime/{name} holds {shown!r}, not {text!r}"

    def expect_project_file_without(self, path: str, part: str) -> None:
        text = (self.app.config.root / path).read_text()
        assert part not in text, f"{path} still holds {part!r}"

    def expect_no_project_file(self, path: str) -> None:
        assert not (self.app.config.root / path).exists(), f"{path} is still in the project"

    def expect_project_file_is(self, path: str, text: str) -> None:
        assert (self.app.config.root / path).read_text() == text, f"{path} changed"

    def expect_typed_last(self, line: str) -> None:
        last = self.typed[-1] if self.typed else ""
        assert last == line, f"the last line typed into the agent's terminal is {last!r}, not {line!r}"

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

    def expect_card_data(self, n: int, **fields) -> None:
        data = self.api_row("messages", n).get("data") or {}
        card_fields = {name: data.get(name) for name in fields}
        assert card_fields == fields, f"the card of message {n} holds {card_fields}, not {fields}"

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

    def expect_seconds_waited_with_work_open(self, seconds: int) -> None:
        agents = [row["id"] for row in get_answer(self.app, "/journal/agents", MAIN)[1]["rows"] if row.get("session") == self.scoped_session()]
        counted = sum(round(waited) for _, waited in self.api_row("agents", max(agents))["open_work_waits"])
        assert counted == seconds, f"the agent waited {counted} seconds with work open, not {seconds}"

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
