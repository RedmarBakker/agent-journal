import shlex

from journal.support.caller import Caller
from tests.observation import Observation
from tests.simulation.simulator import Simulator


class AgentSession:
    """Send one simulated agent's hooks and journal commands through its own environment."""

    def __init__(self, simulator: Simulator, caller: Caller) -> None:
        self.simulator, self.caller, self.calls = simulator, caller, 0

    def session_start(self) -> Observation:
        return self.hook("SessionStart", source="startup")

    def hook(self, kind: str, **body) -> Observation:
        return self.simulator.hook(
            kind,
            session=self.caller.agent_session,
            environment=self.caller.environment,
            **body,
        )

    def tool(self, name: str, given: dict, answer: dict) -> Observation:
        use = self.next_tool_use_id()
        held = self.hook("PreToolUse", tool_name=name, tool_input=given, tool_use_id=use)
        return held if held.is_refused() else self.hook(
            "PostToolUse", tool_name=name, tool_input=given, tool_response=answer, tool_use_id=use
        )

    def command(self, argv: list[str]) -> Observation:
        call = {"command": "journal " + " ".join(shlex.quote(part) for part in argv), "description": "Run a journal command"}
        use = self.next_tool_use_id()
        held = self.hook("PreToolUse", tool_name="Bash", tool_input=call, tool_use_id=use)
        if held.is_refused():
            return held
        seen = self.simulator.run(argv, self.caller)
        self.hook("PostToolUse", tool_name="Bash", tool_input=call, tool_response={"stdout": "", "stderr": "", "interrupted": False}, tool_use_id=use)
        return seen

    def next_tool_use_id(self) -> str:
        self.calls += 1
        return f"sim-{self.calls}"
