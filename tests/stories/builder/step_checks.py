from journal.http.support.project_check import PROJECT_REFUSAL_PREFIX
import json
import re
from journal.engine.nudge import Nudge
from tests.stories.builder.story_agent import StoryAgent
from login_throttle import LoginThrottle

# a hook duration as the terminal line shows it to the user
HOOK_DURATION = re.compile(r"\b[A-Za-z]+: \d+ ms\b")


class StepChecks:
    """The checks made on what one step brought: the lines the journal gave, the hook's verdict, the command's outcome, the shell's text and the viewer's answer."""

    def expect_refused_as_another_projects(self) -> None:
        refusal = (self.verdict.body.get("error", "") if self.verdict else "") or (self.command.error if self.command else "")
        assert PROJECT_REFUSAL_PREFIX in refusal, f"not refused as another project's: {self.verdict or self.command}"

    def expect_agent_told_words(self, agent: StoryAgent, nudge: Nudge, part: str) -> None:
        session = self.story.session_of(agent)
        lines = [nudge.create(**line.values).rendered() for line in self.said if line.key == nudge.key and line.session == session]
        assert any(part in line for line in lines), f"{session} not told {part!r} in {nudge.key}: {lines}"

    def expect_command_lines_holding(self, part: str, count: int) -> None:
        holding = [line for line in self.command.text.splitlines() if part in line] if self.command else []
        assert len(holding) == count, f"{len(holding)} lines of the command hold {part!r}, not {count}: {holding}"

    def account(self, session: str = "") -> str:
        stack = self.story.session_stack(session) if session else self.story.stack()
        return f"told {[(lines.session, lines.key, lines.values) for lines in self.said]}; stack {stack}"

    def expect_agent_told(self, agent: StoryAgent, nudge: Nudge, **values) -> None:
        self.expect_told_to(self.story.session_of(agent), nudge, values)

    def expect_told_to(self, session: str, nudge: Nudge, values: dict) -> None:
        assert any(lines.matches(nudge.key, values) and lines.session == session for lines in self.said), f"{session} not told {nudge.key} {values}; {self.account(session)}"

    def expect_agent_not_told(self, agent: StoryAgent, nudge: Nudge, **values) -> None:
        self.expect_not_told_to(self.story.session_of(agent), nudge, values)

    def expect_not_told_to(self, session: str, nudge: Nudge, values: dict) -> None:
        assert not any(lines.matches(nudge.key, values) and lines.session == session for lines in self.said), f"{session} told {nudge.key} {values}; {self.account(session)}"

    def expect_agent_told_nothing(self, agent: StoryAgent) -> None:
        session = self.story.session_of(agent)
        told = [line for line in self.said if line.session == session]
        assert not told, f"told something; {self.account(session)}"

    def expect_refused(self, agent: StoryAgent, nudge: Nudge, **values) -> None:
        assert self.verdict is not None and self.verdict.refused(), f"let through; {self.account(self.story.session_of(agent))}"
        self.expect_agent_told(agent, nudge, **values)

    def expect_refused_by_anything(self) -> None:
        assert self.verdict is not None and self.verdict.refused(), f"let through; {self.account()}"

    def expect_refusal_text(self, part: str) -> None:
        said = str(self.verdict.body) if self.verdict else ""
        assert part in said, f"the refusal does not say {part!r}: {said}"

    def expect_refusal_without(self, part: str) -> None:
        said = str(self.verdict.body) if self.verdict else ""
        assert part not in said, f"the refusal says {part!r}: {said}"

    def expect_allowed(self, agent: StoryAgent | None = None) -> None:
        session = self.story.session_of(agent) if agent else ""
        assert self.verdict is not None and not self.verdict.refused(), f"refused; {self.account(session)}"

    def expect_shell_text(self, *parts: str) -> None:
        assert all(part in self.shell_text for part in parts), f"the command showed {self.shell_text!r}, not {parts}"

    def expect_shell_text_without(self, part: str) -> None:
        assert part not in self.shell_text, f"the command showed {part!r}: {self.shell_text!r}"

    def expect_shell_exit(self, code: int) -> None:
        assert self.shell_exit == code, f"the command ended {self.shell_exit}, not {code}"

    def expect_launcher_prompt(self, heading: str, *options: str, default: int) -> None:
        shown = getattr(self.story, "launcher_questions", [])
        assert shown and shown[-1] == (heading, options, default), f"the launcher's last question was {shown[-1] if shown else None}, not {(heading, options, default)}"

    def expect_launcher_started_in_worktree(self, environment: str) -> None:
        from journal.support.worktree import Worktree

        folder = Worktree(self.story.app.config.root, environment).path
        choice = getattr(self.story, "launcher_choice", None)
        assert self.story.launcher_refusal == "", f"the launcher refused to start: {self.story.launcher_refusal}"
        assert choice and choice.environment == environment and choice.worktree, f"the launcher chose {choice}, not a worktree for {environment}"
        assert self.story.launcher_front_folder == str(folder) and folder.is_dir(), f"the launcher uses {self.story.launcher_front_folder!r}, not {folder}"

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

    def expect_hosted_login_required(self) -> None:
        location = self.viewer_answer["headers"].get("Location", "")
        assert self.viewer_status == 303 and location.startswith("/login?next="), (
            f"the unauthenticated visitor got {self.viewer_status} {location!r}, not the hosted login"
        )
        assert self.viewer_answer["body"] == "", (
            f"the hosted journal returned content before login: {self.viewer_answer['body']!r}"
        )

    def expect_hosted_login_form(self) -> None:
        body = self.viewer_answer["body"]
        assert self.viewer_status == 200 and 'type="password"' in body, (
            f"the visitor did not get the hosted password form: {self.viewer_status} {body!r}"
        )

    def expect_hosted_login_rejected(self) -> None:
        body = self.viewer_answer["body"]
        assert self.viewer_status == 401 and "password was not accepted" in body.lower(), (
            f"the wrong hosted password was not refused: {self.viewer_status} {body!r}"
        )
        assert "Set-Cookie" not in self.viewer_answer["headers"], (
            f"the wrong hosted password received a session: {self.viewer_answer['headers']}"
        )

    def expect_hosted_login_retry_announced(self) -> None:
        retry_after = self.viewer_answer["headers"].get("Retry-After", "")
        assert self.viewer_status == 401 and retry_after.isdigit() and int(retry_after) > 0, (
            f"the wrong password did not announce its retry delay: {self.viewer_status} {self.viewer_answer}"
        )
        delays = getattr(self.story, "hosted_retry_delays", [])
        assert not delays or int(retry_after) > delays[-1], (
            f"the repeated source did not receive a longer retry delay: {delays} then {retry_after}"
        )
        self.story.hosted_retry_delays = [*delays, int(retry_after)]

    def expect_hosted_login_slowed(self) -> None:
        retry_after = self.viewer_answer["headers"].get("Retry-After", "")
        assert self.viewer_status == 429 and retry_after.isdigit() and int(retry_after) >= LoginThrottle().source_lockout, (
            f"the locked login source was not slowed: {self.viewer_status} {self.viewer_answer}"
        )

    def expect_hosted_session_removed(self) -> None:
        headers = self.viewer_answer["headers"]
        cookie = headers.get("Set-Cookie", "")
        assert self.viewer_status == 303 and headers.get("Location") == "/login", (
            f"logout did not return the visitor to login: {self.viewer_status} {headers}"
        )
        assert "journal_hosted_session=;" in cookie and "Max-Age=0" in cookie, (
            f"logout did not clear the hosted session cookie: {cookie!r}"
        )
        assert not self.story.hosted_login_state["sessions"], "logout left the hosted session active"

    def expect_gateway_listener_refused(self) -> None:
        answer = json.dumps(self.viewer_answer)
        assert self.viewer_status == 403 and "token-checked supervisor routes only" in answer, (
            f"the Gateway listener admitted an owner route without a service token: {self.viewer_status} {answer}"
        )

    def expect_gateway_service_token_required(self) -> None:
        answer = json.dumps(self.viewer_answer)
        assert self.viewer_status == 403 and "service credential is required" in answer, (
            f"the Gateway listener admitted a service route without its token: {self.viewer_status} {answer}"
        )

    def expect_hosted_session_created(self) -> None:
        headers = self.viewer_answer["headers"]
        cookie = headers.get("Set-Cookie", "")
        assert self.viewer_status == 303 and headers.get("Location") == "/journal/health", (
            f"the correct hosted password did not redirect to its requested journal page: {self.viewer_status} {headers}"
        )
        assert "HttpOnly" in cookie and "Secure" in cookie and "SameSite=Lax" in cookie, (
            f"the hosted session cookie is not private: {cookie!r}"
        )

    def expect_hosted_journal_reached(self) -> None:
        body = self.viewer_answer["body"]
        assert self.viewer_status == 200 and body == "Hosted journal content; cookie=", (
            "the authenticated visitor did not reach the journal origin without forwarding its hosted session: "
            f"{self.viewer_status} {self.viewer_answer!r}"
        )

    def expect_viewer_refused(self, part: str) -> None:
        assert self.viewer_status >= 300 and part in json.dumps(self.viewer_answer), f"the viewer's request answered {self.viewer_status} {self.viewer_answer}, not a refusal saying {part!r}"

    def expect_viewer_text(self, part: str) -> None:
        assert self.viewer_status < 300 and part in json.dumps(self.viewer_answer), f"the viewer's request answered {self.viewer_status} {self.viewer_answer}, not text holding {part!r}"

    def expect_viewer_not_found_without(self, part: str) -> None:
        assert self.viewer_status == 404 and part not in json.dumps(self.viewer_answer), f"the viewer's request answered {self.viewer_status} {self.viewer_answer}, leaking {part!r} or not hiding the row"

    def expect_viewer_downloads_json_equal(self, expected: dict) -> None:
        downloaded = json.loads(self.viewer_answer["body"])
        assert self.viewer_status < 300 and downloaded == expected, f"the exported history differs from the viewer's read: {downloaded}"
        assert self.viewer_answer["content_type"].startswith("application/json") and "attachment;" in self.viewer_answer["headers"].get("Content-Disposition", ""), f"the history was not returned as a JSON download: {self.viewer_answer}"

    def expect_viewer_shows(self, name: str, value: object) -> None:
        assert self.viewer_answer.get(name) == value, f"the viewer was given {name} {self.viewer_answer.get(name)!r}, not {value!r}"

    def expect_viewer_rows(self, key: str, field: str, values: list) -> None:
        shown = [row.get(field) for row in self.viewer_answer.get(key, [])]
        assert shown == values, f"the viewer was given {key} with {field} {shown}, not {values}"

    def expect_viewer_rows_count(self, count: int) -> None:
        assert len(self.viewer_answer) == count, f"the viewer was given {len(self.viewer_answer)} rows, not {count}: {self.viewer_answer}"

    def expect_viewer_list_field(self, field: str, values: list) -> None:
        shown = [row.get(field) for row in self.viewer_answer]
        assert shown == values, f"the viewer was given {field} {shown}, not {values}"

    def expect_viewer_rows_holding(self, key: str, field: str, value: object) -> None:
        shown = [row.get(field) for row in self.viewer_answer.get(key, [])]
        assert value in shown, f"the viewer was given {key} with {field} {shown}, none of them {value!r}"

    def expect_viewer_part(self, path: tuple, value: object) -> None:
        part = self.viewer_answer
        for key in path:
            part = part[key]
        assert part == value, f"the viewer was given {part!r} at {'/'.join(map(str, path))}, not {value!r}"

    def expect_viewer_part_is_truthy(self, path: tuple) -> None:
        part = self.viewer_answer
        for key in path:
            part = part[key]
        assert part, f"the viewer was given an empty value at {'/'.join(map(str, path))}"

    def expect_viewer_parts_differ(self, first: tuple, second: tuple) -> None:
        left, right = self.viewer_answer, self.viewer_answer
        for key in first:
            left = left[key]
        for key in second:
            right = right[key]
        assert left != right, f"the viewer was given the same value {left!r} at both paths"

    def expect_viewer_parts_equal(self, first: tuple, second: tuple) -> None:
        left, right = self.viewer_answer, self.viewer_answer
        for key in first:
            left = left[key]
        for key in second:
            right = right[key]
        assert left == right, f"the viewer was given different values {left!r} and {right!r} at the two paths"

    def expect_viewer_rows_have_fields(self, key: str, *fields: str) -> None:
        rows = self.viewer_answer.get(key, [])
        missing = [(index, field) for index, row in enumerate(rows) for field in fields if field not in row]
        assert not missing, f"the viewer's {key} rows lack fields {missing}"

    def expect_viewer_count_at_most(self, key: str, count: int) -> None:
        shown = self.viewer_answer.get(key, [])
        assert len(shown) <= count, f"the viewer was given {len(shown)} {key}, more than {count}"

    def expect_viewer_rows_newer(self, key: str, n: int) -> None:
        older = [row["id"] for row in self.viewer_answer.get(key, []) if row["id"] <= n]
        assert not older, f"the viewer was given {key} {older}, not newer than {n}"

    def expect_viewer_rows_without(self, key: str, field: str) -> None:
        holding = [row["id"] for row in self.viewer_answer.get(key, []) if field in row]
        assert not holding, f"the viewer was given {key} {holding} with their {field}"

    def expect_viewer_rows_not_holding(self, key: str, field: str, value: object) -> None:
        shown = [row.get(field) for row in self.viewer_answer.get(key, [])]
        assert value not in shown, f"the viewer was given {key} with {field} {value!r}"

    def expect_viewer_first_hit(self, n: int, part: str) -> None:
        first = self.viewer_answer[0] if self.viewer_answer else {}
        assert first.get("id") == n and part in first.get("text", ""), f"the viewer's first hit is {first}, not {n} holding {part!r}"

    def expect_viewer_list_count(self, count: int) -> None:
        assert len(self.viewer_answer) == count, f"the viewer was given {len(self.viewer_answer)} rows, not {count}: {self.viewer_answer}"

    def expect_viewer_count(self, key: str, count: int) -> None:
        shown = self.viewer_answer.get(key, [])
        assert len(shown) == count, f"the viewer was given {len(shown)} {key}, not {count}"

    def expect_tool_input_changed(self, **fields) -> None:
        changed = (self.verdict.body.get("hookSpecificOutput") or {}).get("updatedInput") or {} if self.verdict else {}
        shown = {name: changed.get(name) for name in fields}
        assert shown == fields, f"the tool's input was changed to {changed}, not to hold {fields}"

    def expect_command_refused(self) -> None:
        assert self.command is not None and self.command.code != 0, f"the command passed: {self.command.text if self.command else ''}"

    def expect_hook_duration_shown(self) -> None:
        line = self.user_line()
        assert HOOK_DURATION.search(line), f"the hook's answer shows the user no duration: {self.verdict.body if self.verdict else None}"
        assert not HOOK_DURATION.search(self.agent_text()), f"the hook's duration reached the agent: {self.agent_text()}"

    def user_line(self) -> str:
        body = self.verdict.body if self.verdict else {}
        answer = body.get("answer", body) if isinstance(body, dict) else {}
        return str(answer.get("systemMessage", ""))

    def agent_text(self) -> str:
        body = self.verdict.body if self.verdict else {}
        answer = body.get("answer", body) if isinstance(body, dict) else {}
        specific = answer.get("hookSpecificOutput", {})
        return " ".join(str(part) for part in (specific.get("additionalContext", ""), specific.get("permissionDecisionReason", ""), answer.get("reason", ""), body.get("error", "")))

    def expect_command_line(self, *parts: str) -> str:
        lines = [line for line in self.command.text.splitlines() if all(part in line for part in parts)]
        assert lines, f"no line of the command says {', '.join(parts)}: {self.command.text}"
        return lines[0]
