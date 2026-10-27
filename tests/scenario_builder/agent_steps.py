import shlex

from tests.scenario_builder.hook_verdict import HookVerdict


class AgentSteps:
    """What the scenario's main agent does, each a sentence that plays the real hook or command for the scenario's provider."""

    def agent_starts_a_session(self) -> None:
        self.hooked("SessionStart", source="startup")

    def agent_looks_at_the_overview(self) -> None:
        self.agent_runs("environment overview")

    def agent_runs(self, line: str) -> None:
        self.ran(self.app.console().run(shlex.split(line), self.agent))

    def agent_reads(self, path: str) -> None:
        self.hooked("PreToolUse", tool_name=self.tools.read, tool_input={"file_path": path})

    def agent_writes(self, path: str) -> None:
        self.hooked("PreToolUse", tool_name=self.tools.write, tool_input={"file_path": path, "content": "x"})

    def agent_runs_in_the_shell(self, line: str) -> None:
        self.hooked("PreToolUse", tool_name=self.tools.shell, tool_input={"command": line})

    def agent_stops(self) -> None:
        self.hooked("Stop")

    def agent_replies(self, message: int, text: str) -> None:
        self.ran(self.app.console().run(["message", "send", text, "--reply-to", str(message)], self.agent))

    def hooked(self, type_name: str, **body) -> None:
        status, answer = self.posted_hook(type_name, **body)
        self.observed(HookVerdict(self.provider, status, answer if isinstance(answer, dict) else {}), None)
