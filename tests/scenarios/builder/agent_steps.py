import shlex

from tests.scenarios.builder.hook_verdict import HookVerdict


class AgentSteps:
    """What the scenario's main agent does, each a sentence that plays the real hook or command for the scenario's provider and names its action in the story's path."""

    def agent_starts_a_session(self) -> None:
        self.hooked("agent starts a session", "SessionStart", source="startup")

    def agent_looks_at_the_overview(self) -> None:
        self.agent_runs("environment overview")

    def agent_runs(self, line: str) -> None:
        words = shlex.split(line)
        flags = [word for word in words if word.startswith("--")]
        self.ran(f"agent runs {' '.join(words[:2] + flags)}", self.app.console().run(words, self.agent))

    def agent_reads(self, path: str = "a.py", times: int = 1) -> None:
        for _ in range(times):
            self.hooked("agent reads", "PreToolUse", tool_name=self.tools.read, tool_input={"file_path": path})

    def agent_writes(self, path: str) -> None:
        self.hooked("agent writes", "PreToolUse", tool_name=self.tools.write, tool_input={"file_path": path, "content": "x"})

    def agent_runs_in_the_shell(self, line: str) -> None:
        self.hooked(f"agent runs in the shell {line.split()[0]}", "PreToolUse", tool_name=self.tools.shell, tool_input={"command": line})

    def agent_stops(self) -> None:
        self.hooked("agent stops", "Stop")

    def agent_replies(self, message: int, text: str) -> None:
        self.ran("agent replies", self.app.console().run(["message", "send", text, "--reply-to", str(message)], self.agent))

    def hooked(self, action: str, type_name: str, **body) -> None:
        status, answer = self.posted_hook(type_name, **body)
        verdict = HookVerdict(self.provider, status, answer if isinstance(answer, dict) else {})
        self.observed(f"{action}, {'refused' if verdict.refused() else 'let through'}", verdict, None)
