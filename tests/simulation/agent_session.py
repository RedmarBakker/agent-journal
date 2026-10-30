import shlex

from journal.features.shell.support.shell_record import ShellRecord
from journal.support.command_classifier import CommandClassifier
from journal.support.command_part import CommandPart
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

    def commit(self, subject: str) -> Observation:
        line = f"git commit -m {shlex.quote(subject)}"
        call, use = {"command": line, "description": "Commit the task's part"}, self.next_tool_use_id()
        held = self.hook("PreToolUse", tool_name="Bash", tool_input=call, tool_use_id=use)
        if held.is_refused():
            return held
        root = self.simulator.app.config.root
        chain = f"sim-commit-{self.caller.agent_session}-{self.calls}"
        self.simulator.ledger.committed(subject, int(self.simulator.source.seconds()))
        record = self.simulator.app.container.get(ShellRecord)
        record.start(chain, line, root / ".journal" / "runs" / chain, self.caller, ran_in=str(root))
        record.finish_part(chain, CommandPart.plain(line, self.simulator.app.container.get(CommandClassifier)), 0, 0.1, "", [], self.caller)
        record.foreground_end(chain, 0, self.caller)
        return self.hook("PostToolUse", tool_name="Bash", tool_input=call, tool_response={"stdout": "", "stderr": "", "interrupted": False}, tool_use_id=use)

    def next_tool_use_id(self) -> str:
        self.calls += 1
        return f"sim-{self.calls}"
