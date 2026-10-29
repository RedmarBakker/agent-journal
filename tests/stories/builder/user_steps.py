import re
import shlex
import uuid
from dataclasses import replace

from journal.features.library.support.library_account import LibraryAccount
from journal.features.workers.workers_options import WorkersOptions
from journal.support.caller import Caller
from journal.support.option import Option
from sync_server.team_server import TeamServer
from journal.http.controllers.settings import FEATURES
from tests.full_project import MAIN
from tests.in_process import answered, get_answer, posted


class UserSteps:
    """What the user does in a story, each a sentence that posts to the route the viewer's client posts to, as the user's own request."""

    def user_sends_message(self, text: str) -> int:
        return self.user_posted("/journal/messages", {"text": text, "idempotency": uuid.uuid4().hex})["id"]

    def user_attaches_file(self, message: int, name: str, content: bytes) -> None:
        self.user_uploads(f"/journal/messages/{message}/files", name, content)
        assert self.viewer_status < 300, f"the viewer's upload was refused: {self.viewer_answer}"
        self.observed("user attaches a file", None, None)

    def user_starts_a_dump(self, brief: str) -> int:
        return self.user_posted("/journal/dumps", {"brief": brief}, "user starts a dump")["id"]

    def user_drops_a_file_in_the_dump(self, dump: int, name: str, content: bytes) -> None:
        self.user_uploads(f"/journal/dumps/{dump}/files", name, content)
        self.observed("user drops a file in the dump", None, None)

    def user_uploads(self, path: str, name: str, content: bytes) -> None:
        boundary = "story"
        raw = f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{name}\"\r\nContent-Type: application/octet-stream\r\n\r\n".encode() + content + f"\r\n--{boundary}--\r\n".encode()
        self.viewer_status, self.viewer_answer = answered(self.app, "POST", path, raw, {**MAIN, "Content-Type": f"multipart/form-data; boundary={boundary}"})

    def viewer_logs_a_console_error(self, message: str, stack: str) -> None:
        self.user_posted("/journal/client-errors", {"message": message, "stack": stack}, "the viewer logs a console error")

    def a_library_server_runs(self) -> str:
        folder = self.app.config.root / "library-server"
        folder.mkdir(exist_ok=True)
        library = TeamServer(folder)
        server = library.started("127.0.0.1", 0)
        self.library_team = library
        self.closers.append(lambda: library.close(server))
        self.observed("a library server runs", None, None)
        return f"http://127.0.0.1:{server.server_address[1]}"

    def user_connects_to_a_library(self) -> str:
        library = self.a_library_server_runs()
        self.user_types(f"library connect {library} --email ada@example.com --name Ada --password 'correct horse battery'")
        return library

    def user_is_a_library_member(self) -> None:
        self.user_connects_to_a_library()
        self.library_team.accounts.create("carl@example.com", "Carl", "correct horse battery", "member", 2.0)
        _, token = self.library_team.devices.login("carl@example.com", "correct horse battery", "laptop", "127.0.0.1", 2.0)
        account = LibraryAccount(self.app.config)
        account.write(replace(account.connection(), token=token, role="member"))
        self.observed("the user is a member of the library", None, None)

    def a_library_holds_a_sequence_imported_here(self, title: str, steps: str) -> int:
        library = self.a_library_server_runs()
        console, user = self.app.console(), Caller.user("main")
        lines = (["library", "connect", library, "--email", "ada@example.com", "--name", "Ada", "--password", "correct horse battery"], ["sequence", "create", title, "--steps", steps])
        outcomes = [console.run(line, user) for line in lines]
        sequence = int(re.search(r"sequence (\d+)", outcomes[-1].text)[1])
        outcomes += [console.run(line, user) for line in (["library", "publish", "sequence", str(sequence)], ["library", "import", "sequence", re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")])]
        refused = [outcome.error for outcome in outcomes if outcome.code]
        assert not refused, f"the library setup was refused: {refused}"
        self.observed("a library holds a sequence imported here", None, None)
        return sequence

    def library_server_stops(self) -> None:
        self.closers.pop()()
        self.observed("the library server stops", None, None)

    def user_types(self, line: str) -> None:
        arguments = shlex.split(line)
        self.record_command(f"user types {' '.join(arguments[:2])}", self.app.console().run(arguments, Caller.user("main")))

    def project_text(self, path: str) -> str:
        return (self.app.config.root / path).read_text()

    def user_edits_message(self, message: int, text: str) -> None:
        self.user_posted(f"/journal/messages/{message}", {"text": text}, "user edits a message")

    def user_writes_a_document(self, title: str, abstract: str, body: str) -> int:
        return self.user_posted("/journal/docs", {"title": title, "abstract": abstract, "body": body}, "user writes a document")["id"]

    def user_writes_a_report(self, title: str, abstract: str, body: str) -> int:
        return self.user_posted("/journal/reports", {"title": title, "abstract": abstract, "body": body}, "user writes a report")["id"]

    def user_deletes_message(self, message: int) -> None:
        self.user_posted(f"/journal/messages/{message}/delete", {}, "user deletes a message")

    def user_asks_about(self, rows: list[str], text: str) -> None:
        self.viewer_status, self.viewer_answer = posted(self.app, "/journal/messages", {"text": text, "refers": rows, "idempotency": uuid.uuid4().hex}, MAIN)
        self.observed("user asks about a row in the chat", None, None)

    def user_comments_on(self, table: str, row: int, text: str) -> int:
        return self.user_posted("/journal/messages", {"text": text, "on": f"{table}:{row}", "idempotency": uuid.uuid4().hex})["id"]

    def user_replies_in_the_column(self, table: str, row: int, comment: int, text: str) -> int:
        return self.user_posted("/journal/messages", {"text": text, "on": f"{table}:{row}", "reply_target": comment, "idempotency": uuid.uuid4().hex}, "user replies in the comment column")["id"]

    def user_replies_in_the_chat(self, message: int, text: str) -> int:
        return self.user_posted("/journal/messages", {"text": text, "reply_target": message, "idempotency": uuid.uuid4().hex}, "user replies in the chat")["id"]

    def user_answers(self, question: int, answer: str) -> None:
        self.user_posted(f"/journal/questions/{question}/answer", {"answer": answer})

    def user_reacts(self, message: int, emoji: str) -> None:
        self.user_posted(f"/journal/messages/{message}/react", {"emoji": emoji})

    def user_creates_plan_in(self, environment: str, title: str) -> int:
        status, answer = posted(self.app, "/journal/plans", {"title": title, "brief": title}, {"X-Journal-Env": environment})
        assert status < 300, f"the viewer's request to make a plan in {environment} was refused: {answer}"
        self.observed(f"user makes a plan in {environment}", None, None)
        return answer["id"]

    def user_creates_plan(self, title: str, brief: str) -> int:
        return self.user_posted("/journal/plans", {"title": title, "brief": brief})["id"]

    def user_adds_plan_task(self, plan: int, title: str) -> int:
        return self.user_posted(f"/journal/plans/{plan}/tasks", {"title": title, "brief": f"- {title} is done"})["id"]

    def user_sets_plan_testing(self, plan: int, title: str) -> None:
        self.user_posted(f"/journal/plans/{plan}/testing", {"title": title}, f"user sets the plan testing to {title}")

    def user_opens(self, route: str) -> None:
        self.viewer_status, self.viewer_answer = get_answer(self.app, route, MAIN)
        self.observed(f"user opens {route}", None, None)

    def user_opens_in(self, environment: str, route: str) -> None:
        self.viewer_status, self.viewer_answer = get_answer(self.app, route, {"X-Journal-Env": environment})
        self.observed(f"user opens {route} in {environment}", None, None)

    def user_presses(self, path: str, body: dict) -> None:
        self.viewer_status, self.viewer_answer = posted(self.app, path, body, MAIN)
        self.observed(f"user presses {re.sub(r'/\d+', '/{n}', path)}", None, None)

    def card_number(self, key: str) -> int:
        return next(row["id"] for row in get_answer(self.app, "/journal/messages", MAIN)[1]["rows"] if (row.get("data") or {}).get("key") == key)

    def user_docks(self, table: str, n: int) -> None:
        self.viewer_status, self.viewer_answer = posted(self.app, f"/journal/docks/{table}/{n}", {}, MAIN)
        self.observed(f"user docks a row of {table}", None, None)

    def docked_card(self) -> int:
        return self.viewer_answer["id"]

    def user_undocks(self, table: str, n: int) -> None:
        self.viewer_status, self.viewer_answer = posted(self.app, f"/journal/docks/{table}/{n}/undock", {}, MAIN)
        self.observed(f"user undocks a row of {table}", None, None)

    def user_closes_the_plan_card(self, plan: int) -> None:
        self.user_posted(f"/journal/plans/{plan}/dismiss", {}, "user closes the plan's card")

    def first_shown(self, key: str) -> int:
        return self.viewer_answer[key][0]["id"]

    def user_pauses_the_agent(self) -> None:
        self.user_posted(f"/journal/agents/{self.main_agent_id()}/pause", {}, "user pauses the agent")

    def user_resumes_the_agent(self) -> None:
        self.user_posted(f"/journal/agents/{self.main_agent_id()}/resume", {}, "user resumes the agent")

    def user_skips_the_step(self) -> None:
        self.user_posted(f"/journal/agents/{self.main_agent_id()}/skip-step", {}, "user skips the sequence step")

    def user_ends_the_sequence(self) -> None:
        self.user_posted(f"/journal/agents/{self.main_agent_id()}/end-sequence", {}, "user ends the sequence")

    def main_agent_id(self) -> int:
        return next(row["id"] for row in get_answer(self.app, "/journal/agents", MAIN)[1]["rows"] if row.get("session") == self.main_session())

    def user_approves_plan_with_a_comment(self, plan: int, text: str) -> int:
        key = uuid.uuid4().hex
        comment = self.user_posted("/journal/messages", {"text": text, "on": f"plans:{plan}", "idempotency": key}, "user comments on the plan")["id"]
        self.user_posted(f"/journal/plans/{plan}/approve", {"comment_key": key}, "user approves the plan with the comment")
        return comment

    def user_approves_plan(self, plan: int) -> None:
        self.user_posted(f"/journal/plans/{plan}/approve", {})

    def user_pauses_plan(self, plan: int) -> None:
        self.user_posted(f"/journal/plans/{plan}/pause", {})

    def user_edits_task(self, task: int, title: str) -> None:
        self.user_posted(f"/journal/tasks/{task}", {"title": title}, "user edits a task")

    def user_rewrites_the_brief(self, task: int, brief: str) -> None:
        self.user_posted(f"/journal/tasks/{task}", {"brief": brief}, "user rewrites a task's brief")

    def user_completes_task(self, task: int, outcome: str) -> None:
        self.user_posted(f"/journal/tasks/{task}/finish", dict(how=outcome), "user completes a task")

    def user_pauses_task(self, task: int, reason: str) -> None:
        self.user_posted(f"/journal/tasks/{task}/pause", dict(why=reason), "user pauses a task")

    def user_cancels_task(self, task: int, reason: str) -> None:
        self.user_posted(f"/journal/tasks/{task}/cancel", dict(why=reason), "user cancels a task")

    def user_cancels_plan(self, plan: int) -> None:
        self.user_posted(f"/journal/plans/{plan}/abandon", {}, "user cancels a plan")

    def user_switches_on(self, feature: type) -> None:
        switches = get_answer(self.app, "/journal/settings", MAIN)[1][FEATURES]
        self.user_posted("/journal/settings", {FEATURES: {**switches, feature.name: True}}, f"user switches on {feature.name}")

    def plays_in(self, mode: str) -> None:
        self.mode = mode
        if self.setting(WorkersOptions.MODE) != mode:
            self.user_sets(WorkersOptions.MODE, mode)

    def user_sets(self, option: Option, value: object) -> None:
        top, _, name = option.key.partition(".")
        position = self.reads.position()
        self.user_posted("/journal/settings", {top: {name: value}}, f"user sets {option.key} to {value}")
        stored = self.setting(option)
        assert stored == value, f"{option.key} was set to {value!r} in the viewer but the journal holds {stored!r}"
        self.set_positions[option.key] = position

    def user_sets_sequence_triggers(self, sequence: int, triggers: list[dict]) -> None:
        self.viewer_status, self.viewer_answer = posted(self.app, f"/journal/sequences/{sequence}/triggers", {"triggers": triggers}, MAIN)
        self.observed("user sets the sequence's triggers", None, None)

    def template_number(self, title: str) -> int:
        return next(row["id"] for row in get_answer(self.app, "/journal/templates", MAIN)[1]["rows"] if row["title"] == title)

    def sequence_number(self, title: str) -> int:
        return next(row["id"] for row in get_answer(self.app, "/journal/sequences", MAIN)[1]["rows"] if row["title"] == title)

    def user_posted(self, path: str, body: dict, action: str = "") -> dict:
        status, answer = posted(self.app, path, body, MAIN)
        assert status < 300, f"the viewer's request {path} was refused: {answer}"
        self.observed(action or f"user posts {re.sub(r'/\d+', '/{n}', path)}", None, None)
        return answer
