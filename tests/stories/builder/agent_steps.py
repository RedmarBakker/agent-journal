import re
import shlex
import subprocess
import threading
import time
from collections.abc import Callable
from journal.engine.nudge import Nudge
from journal.providers.claude import Claude
from journal.providers.codex import Codex
from journal.repositories.command_outputs import CommandOutputs
from journal.repositories.environments import Environments
from journal.repositories.scope import Scope
from journal.support.caller import Caller
from journal.support.option import Option
from journal.features.skills.support.skill_files import HOMES, SKILL_FILE
from journal.features.shell.support.shell_runner import EXIT
from journal.engine.clock import Clock
from journal.http.controllers.hooks import SILENCE_HEADER
from tests.full_project import MAIN
from tests.in_process import get_answer, posted
from tests.replay import pass_time
from tests.stories.builder.hook_verdict import HookVerdict
from urllib.request import Request as HttpRequest, urlopen

# the longest a story waits on a background run, and how often it looks
RUN_END_TIMEOUT_SECONDS, RUN_END_POLL_SECONDS = 15, 0.1
# the longest a story waits on one git command of its own setup
GIT_TIMEOUT_SECONDS = 30
# the thread the shell runner runs a chain on, whose end is the run's last word
RUNNER_THREAD = "shell-chain"

SUBAGENT_MODEL = "haiku"
# how much later a new turn starts than the step before it
TURN_GAP_SECONDS = 1


class AgentSteps:
    """What the story's main agent does, each a sentence that plays the real hook or command for the story's provider: its tool uses and stops, its journal commands that make rows, its shell runs, its sessions, in this environment or another, as many tool uses as a setting allows, and a setting read as the viewer reads it; another environment of the project is made as its launcher makes one."""

    def agent_starts_a_session(self) -> None:
        self.hooked("agent starts a session", "SessionStart", source="startup")

    def agent_resumes_the_session(self) -> None:
        self.hooked("agent resumes its session", "SessionStart", source="resume")

    def agent_ends_the_session(self) -> None:
        self.hooked("agent ends its session", "SessionEnd", reason="exit")

    def agent_closes_its_turn(self, text: str) -> None:
        self.hooked("agent closes its turn", "MessageDisplay", delta=text, message_id=f"turn-{len(self.path)}", index=0, final=True)

    def agent_is_prompted(self, text: str) -> None:
        self.hooked("the user prompts the agent", "UserPromptSubmit", prompt=text)

    def agent_is_prompted_in_a_new_turn(self, text: str) -> None:
        pass_time(self.app, TURN_GAP_SECONDS)
        self.agent_is_prompted(text)

    def agent_looks_at_the_overview(self) -> None:
        self.agent_runs("environment overview")

    def agent_runs(self, line: str) -> None:
        arguments = shlex.split(line)
        flags = [word for word in arguments if word.startswith("--")]
        outcome = self.app.console().run(arguments, self.scoped_caller())
        self.record_command(f"agent runs {' '.join(arguments[:2] + flags)}{', refused' if outcome.code else ''}", outcome)

    def agent_reads(self, path: str = "a.py", count: int = 1) -> None:
        for _ in range(count):
            self.hooked("agent reads", "PreToolUse", tool_name=self.tools.read, tool_input={"file_path": path})

    def agent_reads_after_the_journal_was_down(self, seconds: float) -> None:
        silence_start = self.app.container.get(Clock).held_at - seconds
        headers = {**self.scoped_headers(), SILENCE_HEADER: str(silence_start)}
        call = dict(tool_name=self.tools.read, tool_input={"file_path": "a.py"})
        self.hook_observed("agent reads after the journal was down", *self.session_posted_hook(self.scoped_session(), headers, "PreToolUse", call))

    def agent_has_run_in_the_shell(self, line: str) -> None:
        self.hooked(f"agent has run in the shell {line.split()[0]}", "PostToolUse", tool_name=self.tools.shell, tool_input={"command": line}, tool_response={"stdout": self.shell_text, "stderr": ""})

    def agent_has_read(self, path: str = "a.py") -> None:
        self.hooked("agent has read", "PostToolUse", tool_name=self.tools.read, tool_input={"file_path": path}, tool_response={})

    def agent_reads_part(self, path: str, limit: int) -> None:
        self.hooked("agent reads part of a file", "PreToolUse", tool_name=self.tools.read, tool_input={"file_path": path, "limit": limit})

    def agent_reads_a_skill(self, folder: str) -> None:
        call = dict(tool_name=self.tools.read, tool_input={"file_path": str(self.app.config.root / HOMES[0] / folder / SKILL_FILE)})
        self.hooked("agent reads a skill", "PreToolUse", **call)
        self.hooked("agent has read the skill", "PostToolUse", **call, tool_response={})

    def agent_writes(self, path: str) -> None:
        self.hooked("agent writes", "PreToolUse", tool_name=self.tools.write, tool_input={"file_path": path, "content": "x"})

    def agent_has_edited(self, path: str) -> None:
        patch = [{"oldStart": 7, "newStart": 7, "lines": [" before", "-x", "+y", " after"]}]
        self.hooked("agent has edited", "PostToolUse", tool_name=self.tools.write, tool_input={"file_path": str(self.app.config.root / path), "content": "y"}, tool_response={"structuredPatch": patch})

    def agent_runs_in_its_own_background(self, line: str) -> None:
        self.hooked(f"agent runs in its own background {line.split()[0]}", "PreToolUse", tool_name=self.tools.shell, tool_input={"command": line, "run_in_background": True})

    def agent_runs_in_the_shell(self, line: str) -> None:
        self.hooked(f"agent runs in the shell {line.split()[0]}", "PreToolUse", tool_name=self.tools.shell, tool_input={"command": line})

    def agent_sends_subagent(self, role: str, job: str) -> None:
        self.hooked("agent sends a subagent", "PreToolUse", tool_name=self.tools.subagent, tool_input={"subagent_type": role, "description": job, "task_name": job, "prompt": job, "model": SUBAGENT_MODEL})

    def subagent_starts(self, subagent: str, role: str) -> None:
        self.hooked("a subagent starts", "SubagentStart", agent_id=subagent, agent_type=role)

    def subagent_writes(self, subagent: str, path: str) -> None:
        self.hooked("a subagent writes", "PreToolUse", agent_id=subagent, tool_name=self.tools.write, tool_input={"file_path": path, "content": "x"})

    def subagent_ends(self, subagent: str) -> None:
        self.hooked("a subagent ends", "SubagentStop", agent_id=subagent)

    def agent_stops(self) -> None:
        self.hooked("agent stops", "Stop")

    def agent_stops_again(self) -> None:
        self.hooked("agent stops again after a held stop", "Stop", stop_hook_active=True)

    def agent_reads_message(self, message: int) -> None:
        self.agent_runs(f"message read {message}")

    def agent_reacts(self, message: int, emoji: str) -> None:
        self.record_command("agent reacts", self.app.console().run(["message", "react", str(message), emoji], self.agent))

    def agent_replies(self, message: int, text: str) -> None:
        self.record_command("agent replies", self.app.console().run(["message", "send", text, "--reply-to", str(message)], self.agent))

    def hooked(self, action: str, type_name: str, **body) -> None:
        self.hook_observed(action, *self.posted_hook(type_name, **body))

    def main_hooked(self, action: str, type_name: str, **body) -> None:
        self.hook_observed(action, *self.main_posted_hook(type_name, **body))

    def main_agent_runs(self, line: str) -> None:
        arguments = shlex.split(line)
        self.record_command(f"main agent runs {' '.join(arguments[:2])}", self.app.console().run(arguments, self.agent))

    def main_agent_reads(self, path: str = "a.py") -> None:
        self.main_hooked("main agent reads", "PreToolUse", tool_name=self.tools.read, tool_input={"file_path": path})

    def main_agent_writes(self, path: str) -> None:
        self.main_hooked("main agent writes", "PreToolUse", tool_name=self.tools.write, tool_input={"file_path": path, "content": "x"})

    def main_agent_ends_the_session(self) -> None:
        self.main_hooked("main agent ends its session", "SessionEnd", reason="exit")

    def main_agent_stops(self) -> None:
        self.main_hooked("main agent stops", "Stop")

    def hook_observed(self, action: str, status: int, answer: object) -> None:
        verdict = HookVerdict(self.provider, status, answer if isinstance(answer, dict) else {})
        self.observed(f"{action}, {'refused' if verdict.refused() else 'let through'}", verdict, None)

    def agent_creates_task(self, title: str) -> int:
        self.agent_runs(f"task create '{title}'")
        return self.task_number()

    def agent_creates_briefed_task(self, title: str, brief: str) -> int:
        self.agent_runs(f"task create '{title}' --brief '{brief}'")
        return self.task_number()

    def agent_takes_a_task(self, title: str) -> int:
        self.agent_runs(f"task create '{title}' --start")
        return self.task_number()

    def agent_writes_a_document(self, title: str, abstract: str, text: str) -> int:
        source = self.app.config.root / f"{title}.md"
        source.write_text(text)
        self.agent_runs(f"doc create '{title}' --file '{source}' --abstract '{abstract}'")
        return int(re.search(r"doc (\d+)", self.command.text)[1])

    def agent_rewrites_the_document(self, document: int, text: str) -> None:
        source = self.app.config.root / f"document {document} rewritten.md"
        source.write_text(text)
        self.agent_runs(f"doc update {document} --file '{source}'")

    def agent_asks(self, question: str, *options: str) -> int:
        self.agent_runs(f"question ask '{question}' --options " + " ".join(f"'{option}'" for option in options))
        return int(re.search(r"question (\d+)", self.command.text)[1])

    def agent_replies_with_number(self, message: int, text: str) -> int:
        self.agent_replies(message, text)
        return int(re.search(r"message (\d+)", self.command.text)[1])

    def agent_creates_plan(self, title: str, brief: str) -> int:
        self.agent_runs(f"plan create '{title}' --brief '{brief}'")
        return self.created_number("plan")

    def agent_adds_plan_task(self, plan: int, title: str) -> int:
        self.agent_runs(f"plan add {plan} '{title}' --brief '- {title} is done'")
        return self.created_number("task")

    def agent_creates_sequence(self, title: str, steps: str) -> int:
        self.agent_runs(f"sequence create '{title}' --steps '{steps}'")
        return self.created_number("sequence")

    def created_number(self, noun: str) -> int:
        return int(re.search(rf"{noun} (\d+)", self.command.text)[1])

    def agent_adds_memory(self, text: str, weight: int) -> int:
        self.agent_runs(f"memory add '{text}' --weight {weight}")
        return int(re.search(r"memory (\d+)", self.command.text)[1])

    def agent_answers(self, message: int, text: str) -> None:
        self.agent_runs(f"message read {message}")
        self.agent_replies(message, text)

    def task_number(self) -> int:
        return int(re.search(r"task (\d+)", self.command.text)[1])

    def agent_runs_a_command(self, line: str) -> int:
        raw = "".join(f"{name}={value}\0" for name, value in self.scoped_shell_variables().items()) + f"\0{line}\n"
        request = HttpRequest(f"http://127.0.0.1:{self.app.server().port}/shell/run", data=raw.encode(), method="POST", headers={"Content-Type": "application/octet-stream", "X-Journal-Env": "main", "X-Journal-Cwd": str(self.app.config.root), "X-Journal-Shell": "sh"})
        newest, runners = self.newest_output(), self.running_runners()
        text, _, code = urlopen(request, timeout=30).read().decode().rpartition(EXIT)
        self.runner_threads = [*self.runner_threads, *(self.running_runners() - runners)]
        self.shell_text, self.shell_exit = text, int(code.split()[0])
        self.shell_outputs = self.newest_output() - newest
        self.observed(f"agent runs a command {line.split()[0]}, {'failing' if self.shell_exit else 'passing'}", None, None)
        return self.newest_output()

    @staticmethod
    def running_runners() -> set[threading.Thread]:
        return {thread for thread in threading.enumerate() if thread.name == RUNNER_THREAD}

    def newest_output(self) -> int:
        with self.app.container.get(Scope).environment(1):
            outputs = self.app.container.get(CommandOutputs)
            rows = outputs.selected(outputs.query().order_descending("id").limit(1))
        return rows[0].row_id if rows else 0

    def background_run_ends(self, output: int) -> None:
        deadline = time.monotonic() + RUN_END_TIMEOUT_SECONDS
        while not self.is_output_ended(output):
            assert time.monotonic() < deadline, f"output {output} still runs after {RUN_END_TIMEOUT_SECONDS} seconds"
            time.sleep(RUN_END_POLL_SECONDS)
        for runner in self.runner_threads:
            runner.join(RUN_END_TIMEOUT_SECONDS)
        self.observed("the background run ends", None, None)

    def is_output_ended(self, output: int) -> bool:
        with self.app.container.get(Scope).environment(1):
            return bool(self.app.container.get(CommandOutputs).find(output).ended)

    def output_count(self) -> int:
        with self.app.container.get(Scope).environment(1):
            outputs = self.app.container.get(CommandOutputs)
            return outputs.counted(outputs.query())

    def another_environment(self, name: str) -> str:
        self.app.container.get(Environments).lookup(name)
        self.observed(f"the project has another environment, {name}", None, None)
        return name

    def task_numbers_in(self, environment: str) -> set[int]:
        return set(self.task_states_in(environment))

    def task_states_in(self, environment: str) -> dict[int, str]:
        return {row["id"]: row["state"] for row in get_answer(self.app, "/journal/tasks", {"X-Journal-Env": environment})[1]["rows"]}

    def agent_in_starts_task(self, environment: str, session: str, title: str) -> int:
        self.session_starts_in(environment, session)
        outcome = self.app.console().run(["task", "create", title, "--start"], Caller.agent(environment, session, self.provider))
        assert outcome.code == 0, outcome.error
        return max(self.task_numbers_in(environment))

    def session_starts_in(self, environment: str, session: str) -> None:
        status, answer = posted(self.app, f"/hooks/{self.provider}", {"hook_event_name": "SessionStart", "session_id": session, "source": "startup"}, {"X-Journal-Env": environment})
        self.observed(f"a session starts in {environment}", HookVerdict(self.provider, status, answer if isinstance(answer, dict) else {}), None)

    def expect_told_in(self, environment: str, nudge: Nudge, **values) -> None:
        lines = self.log.environment_lines(environment)
        assert any(line.matches(nudge.key, values) for line in lines), f"the agent in {environment} was not told {nudge.key} {values}: told {[(line.key, line.values) for line in lines]}"

    def second_session_starts(self, session: str = "s2") -> None:
        self.session_starts_with(self.provider, session)

    def other_provider_session_starts(self, session: str = "s3") -> None:
        self.session_starts_with(next(program.name for program in (Claude, Codex) if program.name != self.provider), session)

    def session_starts_with(self, provider: str, session: str) -> None:
        status, answer = posted(self.app, f"/hooks/{provider}", {"hook_event_name": "SessionStart", "session_id": session, "source": "startup"}, MAIN)
        self.replace_main_session(session, provider)
        self.observed(f"a {'second' if provider == self.provider else 'another provider'}'s session starts", HookVerdict(provider, status, answer if isinstance(answer, dict) else {}), None)

    def expect_agent_session(self, session: str) -> None:
        sessions = [row.get("session") for row in get_answer(self.app, "/journal/agents", MAIN)[1]["rows"] if row.get("role") in (None, "main")]
        assert sessions == [session], f"the environment's agents hold the sessions {sessions}, not only {session}"

    def repeat(self, count: int, step: Callable[[], None]) -> None:
        for _ in range(count):
            step()

    def agent_consumes(self, option: Option) -> None:
        for _ in range(int(self.setting(option))):
            self.agent_reads()
            self.expect_allowed()

    def setting_seconds(self, option: Option) -> float:
        return float(self.setting(option)) * 60

    def setting(self, option: Option) -> object:
        top, _, name = option.key.partition(".")
        group = get_answer(self.app, "/journal/settings", MAIN)[1].get(top, {})
        return group.get(name, option.default)

    def project_root(self) -> str:
        return str(self.app.config.root)

    def project_file_holding(self, name: str, text: str) -> None:
        path = self.app.config.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        self.observed(f"the project holds {name}", None, None)

    def project_file(self, name: str, line_count: int) -> str:
        path = self.app.config.root / name
        path.write_text("".join(f"line {number}\n" for number in range(line_count)))
        return str(path)

    def project_is_a_git_repository(self) -> None:
        for arguments in (["init", "-q", "-b", "main"], ["-c", "user.email=story@example.com", "-c", "user.name=Story", "commit", "-q", "--allow-empty", "-m", "start"]):
            subprocess.run(["git", *arguments], cwd=self.app.config.root, capture_output=True, timeout=GIT_TIMEOUT_SECONDS, check=True)
        self.observed("the project is a git repository", None, None)
