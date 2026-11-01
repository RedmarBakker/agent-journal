from tests.stories.builder.story_agent import StoryAgent
import re
import shlex
import uuid
import json
from urllib.parse import urlencode, urlsplit
from dataclasses import replace

from journal.features.library.support.library_account import LIBRARIES_FOLDER, LibraryAccount
from journal.support.caller import Caller
from journal.support.option import Option
from sync_server.team_server import TeamServer
from journal.http.controllers.settings import FEATURES
from tests.full_project import MAIN
from tests.in_process import answered, file_answer, get_answer, posted, routed
from tests.stories.builder.step_result import StepResult
from tests.stories.builder.hosted_journal_origin import HostedJournalOrigin
from hosted_login import HostedLoginHandler, create_login_state
from functools import partial
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from threading import Thread


class UserSteps:
    """What the user does in a story, each a sentence that posts to the route the viewer's client posts to, as the user's own request."""

    def user_sends_message(self, text: str) -> int:
        return self.user_posted("/journal/messages", {"text": text, "idempotency": uuid.uuid4().hex})["id"]

    def user_attaches_file(self, message: int, name: str, content: bytes) -> StepResult:
        self.user_uploads(f"/journal/messages/{message}/files", name, content)
        assert self.viewer_status < 300, f"the viewer's upload was refused: {self.viewer_answer}"
        return self.observed("user attaches a file", None, None)

    def user_starts_a_dump(self, brief: str) -> int:
        return self.user_posted("/journal/dumps", {"brief": brief}, "user starts a dump")["id"]

    def user_drops_a_file_in_the_dump(self, dump: int, name: str, content: bytes) -> StepResult:
        self.user_uploads(f"/journal/dumps/{dump}/files", name, content)
        return self.observed("user drops a file in the dump", None, None)

    def user_uploads(self, path: str, name: str, content: bytes) -> None:
        boundary = "story"
        raw = f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{name}\"\r\nContent-Type: application/octet-stream\r\n\r\n".encode() + content + f"\r\n--{boundary}--\r\n".encode()
        self.viewer_status, self.viewer_answer = answered(self.app, "POST", path, raw, {**MAIN, "Content-Type": f"multipart/form-data; boundary={boundary}"})

    def viewer_logs_a_console_error(self, message: str, stack: str) -> StepResult:
        return self.user_did("/journal/client-errors", {"message": message, "stack": stack}, "the viewer logs a console error")

    def a_team_server_runs(self, name: str = "team") -> str:
        address = self.team_server_started(name, 0)
        self.observed("a team server runs", None, None)
        return f"{address}/setup?code={self.team_server.setup_code.current()}"

    def team_server_started(self, name: str, port: int) -> str:
        folder = self.app.config.root / f"{name}-server"
        folder.mkdir(exist_ok=True)
        team = TeamServer(folder)
        server = team.started("127.0.0.1", port)
        self.team_server = team
        self.closers.append(lambda: team.close(server))
        self.team_addresses[name] = f"http://127.0.0.1:{server.server_address[1]}"
        return self.team_addresses[name]

    def team_servers_restarted(self) -> None:
        for path in sorted((self.app.config.home / LIBRARIES_FOLDER).glob("*.json")):
            connection = json.loads(path.read_text())
            if (self.app.config.root / f"{connection['team']}-server").is_dir():
                self.team_server_started(connection["team"], urlsplit(connection["address"]).port)

    def user_adds_a_team(self, name: str) -> StepResult:
        body = {"url": self.a_team_server_runs(name), "email": "ada@example.com", "name": "Ada", "password": "correct horse battery", "team": name}
        return self.user_presses("/journal/team/connect", body)

    def user_connects_to_a_team(self) -> str:
        team = self.a_team_server_runs()
        self.user_types(f"team connect {team} --email ada@example.com --name Ada --password 'correct horse battery'")
        return team

    def user_is_a_team_member(self) -> StepResult:
        self.user_connects_to_a_team()
        self.team_server.accounts.create("carl@example.com", "Carl", "correct horse battery", "member", 2.0)
        _, token = self.team_server.devices.login("carl@example.com", "correct horse battery", "laptop", "127.0.0.1", 2.0)
        account = LibraryAccount(self.app.config)
        account.write(replace(account.connection(), token=token, role="member"))
        return self.observed("the user is a member of the team", None, None)

    def a_library_holds_a_sequence_imported_here(self, title: str, steps: str) -> int:
        library = self.a_team_server_runs()
        console, user = self.app.console(), Caller.user("main")
        lines = (["team", "connect", library, "--email", "ada@example.com", "--name", "Ada", "--password", "correct horse battery"], ["sequence", "create", title, "--steps", steps])
        outcomes = [console.run(line, user) for line in lines]
        sequence = int(re.search(r"sequence (\d+)", outcomes[-1].text)[1])
        outcomes += [console.run(line, user) for line in (["library", "publish", "sequence", str(sequence)], ["library", "import", "sequence", re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")])]
        refused = [outcome.error for outcome in outcomes if outcome.code]
        assert not refused, f"the library setup was refused: {refused}"
        self.observed("a library holds a sequence imported here", None, None)
        return sequence

    def library_server_stops(self) -> StepResult:
        self.closers.pop()()
        return self.observed("the library server stops", None, None)

    def user_types(self, line: str) -> StepResult:
        arguments = shlex.split(line)
        return self.record_command(f"user types {' '.join(arguments[:2])}", self.app.console().run(arguments, Caller.user("main")))

    def project_text(self, path: str) -> str:
        return (self.app.config.root / path).read_text()

    def user_edits_message(self, message: int, text: str) -> StepResult:
        return self.user_did(f"/journal/messages/{message}", {"text": text}, "user edits a message")

    def user_writes_a_document(self, title: str, abstract: str, body: str) -> int:
        return self.user_posted("/journal/docs", {"title": title, "abstract": abstract, "body": body}, "user writes a document")["id"]

    def user_writes_a_report(self, title: str, abstract: str, body: str) -> int:
        return self.user_posted("/journal/reports", {"title": title, "abstract": abstract, "body": body}, "user writes a report")["id"]

    def user_deletes_message(self, message: int) -> StepResult:
        return self.user_did(f"/journal/messages/{message}/delete", {}, "user deletes a message")

    def user_asks_about(self, rows: list[str], text: str) -> StepResult:
        self.viewer_status, self.viewer_answer = posted(self.app, "/journal/messages", {"text": text, "refers": rows, "idempotency": uuid.uuid4().hex}, MAIN)
        return self.observed("user asks about a row in the chat", None, None)

    def user_comments_on(self, table: str, row: int, text: str) -> int:
        return self.user_posted("/journal/messages", {"text": text, "on": f"{table}:{row}", "idempotency": uuid.uuid4().hex})["id"]

    def user_replies_in_the_column(self, table: str, row: int, comment: int, text: str) -> int:
        return self.user_posted("/journal/messages", {"text": text, "on": f"{table}:{row}", "reply_target": comment, "idempotency": uuid.uuid4().hex}, "user replies in the comment column")["id"]

    def user_replies_in_the_chat(self, message: int, text: str) -> int:
        return self.user_posted("/journal/messages", {"text": text, "reply_target": message, "idempotency": uuid.uuid4().hex}, "user replies in the chat")["id"]

    def user_answers(self, question: int, answer: str) -> StepResult:
        return self.user_did(f"/journal/questions/{question}/answer", {"answer": answer})

    def user_reacts(self, message: int, emoji: str) -> StepResult:
        return self.user_did(f"/journal/messages/{message}/react", {"emoji": emoji})

    def user_creates_plan_in(self, environment: str, title: str) -> int:
        status, answer = posted(self.app, "/journal/plans", {"title": title, "brief": title}, {"X-Journal-Env": environment})
        assert status < 300, f"the viewer's request to make a plan in {environment} was refused: {answer}"
        self.observed(f"user makes a plan in {environment}", None, None)
        return answer["id"]

    def user_creates_plan(self, title: str, brief: str) -> int:
        return self.user_posted("/journal/plans", {"title": title, "brief": brief})["id"]

    def user_adds_plan_task(self, plan: int, title: str, domain: str = "") -> int:
        body = {"title": title, "brief": f"- {title} is done"}
        if domain:
            body["domain"] = domain
        return self.user_posted(f"/journal/plans/{plan}/tasks", body)["id"]

    def user_sets_plan_testing(self, plan: int, title: str) -> StepResult:
        return self.user_did(f"/journal/plans/{plan}/testing", {"title": title}, f"user sets the plan testing to {title}")

    def user_opens(self, route: str) -> StepResult:
        self.viewer_status, self.viewer_answer = get_answer(self.app, route, MAIN)
        return self.observed(f"user opens {route}", None, None)

    def hosted_visitor_opens(self, route: str) -> StepResult:
        return self.hosted_visitor_requests("GET", route)

    def hosted_visitor_submits_password(
        self, password: str, next_path: str = "/journal/health"
    ) -> StepResult:
        body = urlencode({"password": password, "next": next_path}).encode()
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        return self.hosted_visitor_requests("POST", "/login", body, headers)

    def hosted_visitor_requests(
        self, method: str, route: str, body: bytes = b"", headers: dict | None = None
    ) -> StepResult:
        self.hosted_front_started()
        request_headers = dict(headers or {})
        if getattr(self, "hosted_login_cookie", ""):
            request_headers["Cookie"] = self.hosted_login_cookie
        connection = HTTPConnection(*self.hosted_front_address, timeout=5)
        connection.request(method, route, body=body, headers=request_headers)
        response = connection.getresponse()
        self.viewer_status = response.status
        response_headers = dict(response.getheaders())
        self.viewer_answer = {"headers": response_headers, "body": response.read().decode()}
        cookie = response_headers.get("Set-Cookie", "")
        if cookie.startswith("journal_hosted_session="):
            self.hosted_login_cookie = cookie.split(";", 1)[0]
        connection.close()
        return self.observed(f"a visitor makes a {method} request to {route}", None, None)

    def hosted_front_started(self) -> None:
        if getattr(self, "hosted_front_address", None):
            return
        origin = ThreadingHTTPServer(("127.0.0.1", 0), HostedJournalOrigin)
        origin_thread = Thread(target=origin.serve_forever, daemon=True)
        origin_thread.start()
        self.closers.append(lambda: self.close_hosted_front(origin, origin_thread))
        state = create_login_state("story hosted password 123")
        handler = partial(HostedLoginHandler, state, ("127.0.0.1", origin.server_address[1]))
        front = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        front_thread = Thread(target=front.serve_forever, daemon=True)
        front_thread.start()
        self.closers.append(lambda: self.close_hosted_front(front, front_thread))
        self.hosted_front_address = ("127.0.0.1", front.server_address[1])

    @staticmethod
    def close_hosted_front(server: ThreadingHTTPServer, thread: Thread) -> None:
        server.shutdown()
        server.server_close()
        thread.join()

    def user_opens_viewer_in(self, environment: str) -> StepResult:
        self.viewer_status, self.viewer_answer = answered(self.app, "GET", "/journal/viewer", b"", {"X-Journal-Env": environment, "X-Journal-Viewer": "1"})
        return self.observed(f"the viewer tab is open in {environment}", None, None)

    def user_downloads(self, route: str) -> StepResult:
        self.viewer_status, self.viewer_answer = file_answer(self.app, route, MAIN)
        return self.observed(f"user downloads {route}", None, None)

    def user_opens_in(self, environment: str, route: str) -> StepResult:
        self.viewer_status, self.viewer_answer = get_answer(self.app, route, {"X-Journal-Env": environment})
        return self.observed(f"user opens {route} in {environment}", None, None)

    def viewer_stream_receives_environment_switch(self, environment: str) -> StepResult:
        answer = routed(self.app, "GET", f"/journal/entries/stream?since=0&env={environment}", b"", {})
        blocks = answer.blocks
        next(blocks)
        self.viewer_status, self.viewer_answer = answer.status, next(blocks).decode()
        blocks.close()
        return self.observed(f"the viewer stream receives the launch environment for {environment}", None, None)

    def user_sends_message_in(self, environment: str, text: str) -> StepResult:
        self.viewer_status, self.viewer_answer = posted(self.app, "/journal/messages", {"text": text, "idempotency": uuid.uuid4().hex}, {**MAIN, "X-Journal-Env": environment})
        assert self.viewer_status < 300, f"the viewer's message to {environment} was refused: {self.viewer_answer}"
        return self.observed(f"the user sends a message in {environment}", None, None)

    def user_presses_in(self, environment: str, path: str, body: dict) -> StepResult:
        self.viewer_status, self.viewer_answer = posted(self.app, path, body, {"X-Journal-Env": environment})
        return self.observed(f"user presses {re.sub(r'/\d+', '/{n}', path)} in {environment}", None, None)

    def user_presses(self, path: str, body: dict) -> StepResult:
        self.viewer_status, self.viewer_answer = posted(self.app, path, body, MAIN)
        return self.observed(f"user presses {re.sub(r'/\d+', '/{n}', path)}", None, None)

    def card_number(self, key: str) -> int:
        return next(row["id"] for row in get_answer(self.app, "/journal/messages", MAIN)[1]["rows"] if (row.get("data") or {}).get("key") == key)

    def user_docks(self, table: str, n: int) -> StepResult:
        self.viewer_status, self.viewer_answer = posted(self.app, f"/journal/docks/{table}/{n}", {}, MAIN)
        return self.observed(f"user docks a row of {table}", None, None)

    def docked_card(self) -> int:
        return self.viewer_answer["id"]

    def user_undocks(self, table: str, n: int) -> StepResult:
        self.viewer_status, self.viewer_answer = posted(self.app, f"/journal/docks/{table}/{n}/undock", {}, MAIN)
        return self.observed(f"user undocks a row of {table}", None, None)

    def user_closes_the_plan_card(self, plan: int) -> StepResult:
        return self.user_did(f"/journal/plans/{plan}/dismiss", {}, "user closes the plan's card")

    def first_shown(self, key: str) -> int:
        return self.viewer_answer[key][0]["id"]

    def user_pauses_the_agent(self) -> StepResult:
        return self.user_did(f"/journal/agents/{self.main_agent_id()}/pause", {}, "user pauses the agent")

    def user_resumes_the_agent(self) -> StepResult:
        return self.user_did(f"/journal/agents/{self.main_agent_id()}/resume", {}, "user resumes the agent")

    def user_skips_the_step(self) -> StepResult:
        return self.user_did(f"/journal/agents/{self.main_agent_id()}/skip-step", {}, "user skips the sequence step")

    def user_ends_the_sequence(self) -> StepResult:
        return self.user_did(f"/journal/agents/{self.main_agent_id()}/end-sequence", {}, "user ends the sequence")

    def main_agent_id(self) -> int:
        return self.agent_id(self.agents.main)

    def agent_id(self, agent: StoryAgent) -> int:
        return next(row["id"] for row in get_answer(self.app, "/journal/agents", MAIN)[1]["rows"] if row.get("session") == self.session_of(agent))

    def user_approves_plan_with_a_comment(self, plan: int, text: str) -> int:
        key = uuid.uuid4().hex
        comment = self.user_posted("/journal/messages", {"text": text, "on": f"plans:{plan}", "idempotency": key}, "user comments on the plan")["id"]
        self.user_posted(f"/journal/plans/{plan}/approve", {"comment_key": key}, "user approves the plan with the comment")
        return comment

    def user_approves_plan(self, plan: int) -> StepResult:
        return self.user_did(f"/journal/plans/{plan}/approve", {})

    def user_starts_plan(self, plan: int) -> StepResult:
        return self.user_did(f"/journal/plans/{plan}/start", {})

    def user_pauses_plan(self, plan: int) -> StepResult:
        return self.user_did(f"/journal/plans/{plan}/pause", {})

    def user_edits_task(self, task: int, title: str) -> StepResult:
        return self.user_did(f"/journal/tasks/{task}", {"title": title}, "user edits a task")

    def user_rewrites_the_brief(self, task: int, brief: str) -> StepResult:
        return self.user_did(f"/journal/tasks/{task}", {"brief": brief}, "user rewrites a task's brief")

    def user_completes_task(self, task: int, outcome: str) -> StepResult:
        return self.user_did(f"/journal/tasks/{task}/finish", dict(how=outcome), "user completes a task")

    def user_blocks_task(self, task: int, reason: str) -> StepResult:
        return self.user_did(f"/journal/tasks/{task}/block", dict(why=reason), "user blocks a task")

    def user_cancels_task(self, task: int, reason: str) -> StepResult:
        return self.user_did(f"/journal/tasks/{task}/cancel", dict(why=reason), "user cancels a task")

    def user_cancels_plan(self, plan: int) -> StepResult:
        return self.user_did(f"/journal/plans/{plan}/abandon", {}, "user cancels a plan")

    def user_switches_on(self, feature: type) -> StepResult:
        switches = get_answer(self.app, "/journal/settings", MAIN)[1][FEATURES]
        return self.user_did("/journal/settings", {FEATURES: {**switches, feature.name: True}}, f"user switches on {feature.name}")

    def user_switches_off(self, feature: type) -> StepResult:
        switches = get_answer(self.app, "/journal/settings", MAIN)[1][FEATURES]
        return self.user_did("/journal/settings", {FEATURES: {**switches, feature.name: False}}, f"user switches off {feature.name}")

    def user_sets(self, option: Option, value: object) -> StepResult:
        top, _, name = option.key.partition(".")
        position = self.reads.position()
        result = self.user_did("/journal/settings", {top: {name: value}}, f"user sets {option.key} to {value}")
        stored = self.setting(option)
        assert stored == value, f"{option.key} was set to {value!r} in the viewer but the journal holds {stored!r}"
        self.set_positions[option.key] = position
        return result

    def user_creates_trigger(self, phrases: list[str], text: str, action: str) -> int:
        return self.user_posted("/journal/triggers", {"phrases": phrases, "text": text, "action": action}, "user creates a trigger")["id"]

    def user_sets_sequence_triggers(self, sequence: int, triggers: list[dict]) -> StepResult:
        self.viewer_status, self.viewer_answer = posted(self.app, f"/journal/sequences/{sequence}/triggers", {"triggers": triggers}, MAIN)
        return self.observed("user sets the sequence's triggers", None, None)

    def template_number(self, title: str) -> int:
        return next(row["id"] for row in get_answer(self.app, "/journal/templates", MAIN)[1]["rows"] if row["title"] == title)

    def sequence_number(self, title: str) -> int:
        return next(row["id"] for row in get_answer(self.app, "/journal/sequences", MAIN)[1]["rows"] if row["title"] == title)

    def user_did(self, path: str, body: dict, action: str = "") -> StepResult:
        self.user_posted(path, body, action)
        return self.last_step

    def user_posted(self, path: str, body: dict, action: str = "") -> dict:
        status, answer = posted(self.app, path, body, MAIN)
        assert status < 300, f"the viewer's request {path} was refused: {answer}"
        self.viewer_status, self.viewer_answer = status, answer
        self.observed(action or f"user posts {re.sub(r'/\d+', '/{n}', path)}", None, None)
        return answer
