import re
import shlex
from collections.abc import Callable
from journal.engine.nudge import Nudge
from journal.providers.claude import Claude
from journal.providers.codex import Codex
from journal.repositories.command_outputs import CommandOutputs
from journal.repositories.environments import Environments
from journal.repositories.scope import Scope
from journal.support.caller import Caller
from journal.support.option import Option
from tests.full_project import MAIN
from tests.in_process import get_answer, posted
from tests.stories.builder.hook_verdict import HookVerdict
from urllib.request import Request as HttpRequest, urlopen


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

    def agent_looks_at_the_overview(self) -> None:
        self.agent_runs("environment overview")

    def agent_runs(self, line: str) -> None:
        arguments = shlex.split(line)
        flags = [word for word in arguments if word.startswith("--")]
        outcome = self.app.console().run(arguments, self.agent)
        self.record_command(f"agent runs {' '.join(arguments[:2] + flags)}{', refused' if outcome.code else ''}", outcome)

    def agent_reads(self, path: str = "a.py", count: int = 1) -> None:
        for _ in range(count):
            self.hooked("agent reads", "PreToolUse", tool_name=self.tools.read, tool_input={"file_path": path})

    def agent_writes(self, path: str) -> None:
        self.hooked("agent writes", "PreToolUse", tool_name=self.tools.write, tool_input={"file_path": path, "content": "x"})

    def agent_runs_in_the_shell(self, line: str) -> None:
        self.hooked(f"agent runs in the shell {line.split()[0]}", "PreToolUse", tool_name=self.tools.shell, tool_input={"command": line})

    def agent_stops(self) -> None:
        self.hooked("agent stops", "Stop")

    def agent_reads_message(self, message: int) -> None:
        self.agent_runs(f"message read {message}")

    def agent_reacts(self, message: int, emoji: str) -> None:
        self.record_command("agent reacts", self.app.console().run(["message", "react", str(message), emoji], self.agent))

    def agent_replies(self, message: int, text: str) -> None:
        self.record_command("agent replies", self.app.console().run(["message", "send", text, "--reply-to", str(message)], self.agent))

    def hooked(self, action: str, type_name: str, **body) -> None:
        status, answer = self.posted_hook(type_name, **body)
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

    def agent_writes_a_document(self, title: str, text: str) -> int:
        source = self.app.config.root / f"{title}.md"
        source.write_text(text)
        self.agent_runs(f"doc create '{title}' --file '{source}' --abstract '{title}'")
        return int(re.search(r"doc (\d+)", self.command.text)[1])

    def agent_asks(self, question: str, *options: str) -> int:
        self.agent_runs(f"question ask '{question}' --options " + " ".join(f"'{option}'" for option in options))
        return int(re.search(r"question (\d+)", self.command.text)[1])

    def agent_replies_with_number(self, message: int, text: str) -> int:
        self.agent_replies(message, text)
        return int(re.search(r"message (\d+)", self.command.text)[1])

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
        raw = f"JOURNAL_ENV=main\0\0{line}\n"
        request = HttpRequest(f"http://127.0.0.1:{self.app.server().port}/shell/run", data=raw.encode(), method="POST", headers={"Content-Type": "application/octet-stream", "X-Journal-Env": "main", "X-Journal-Cwd": str(self.app.config.root), "X-Journal-Shell": "sh"})
        urlopen(request, timeout=30).read()
        self.observed(f"agent runs a command {line.split()[0]}", None, None)
        with self.app.container.get(Scope).environment(1):
            outputs = self.app.container.get(CommandOutputs)
            return outputs.selected(outputs.query().order_descending("id").limit(1))[0].row_id

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

    def setting(self, option: Option) -> object:
        settings_tree = get_answer(self.app, "/journal/settings", MAIN)[1]
        for part in option.key.split("."):
            settings_tree = settings_tree.get(part, {}) if isinstance(settings_tree, dict) else {}
        return option.default if settings_tree == {} else settings_tree
