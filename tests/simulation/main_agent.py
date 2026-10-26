import shlex
import random

from journal.support.caller import Caller
from tests.observation import Observation
from tests.simulation.simulator import Simulator
from tests.simulation.world import World

AGENT = Caller.agent("main", "s1", "claude")
WRITES_PER_TASK = 4


class MainAgent:
    """The simulated main agent: it plays the action its policy picks, through the same hooks a real agent sends, each journal command as a shell tool use that a hold can refuse, and keeps the world up to date with what it did."""

    def __init__(self, simulator: Simulator, policy, chance: random.Random, worker_seconds: int) -> None:
        self.simulator, self.policy, self.chance, self.worker_seconds = simulator, policy, chance, worker_seconds
        self.current_task, self.writes, self.calls = 0, 0, 0

    def act(self, world: World) -> tuple[str, Observation]:
        action = self.policy.action(world, self.chance)
        return action, getattr(self, f"{action}_action")(world)

    def tool(self, name: str, given: dict, answer: dict) -> Observation:
        self.calls += 1
        call = f"sim-{self.calls}"
        held = self.simulator.hook("PreToolUse", tool_name=name, tool_input=given, tool_use_id=call)
        return held if held.is_refused() else self.simulator.hook("PostToolUse", tool_name=name, tool_input=given, tool_response=answer, tool_use_id=call)

    def command(self, argv: list[str]) -> Observation:
        call = {"command": "journal " + " ".join(shlex.quote(part) for part in argv), "description": "Run a journal command"}
        self.calls += 1
        held = self.simulator.hook("PreToolUse", tool_name="Bash", tool_input=call, tool_use_id=f"sim-{self.calls}")
        if held.is_refused():
            return held
        seen = self.simulator.run(argv, AGENT)
        self.simulator.hook("PostToolUse", tool_name="Bash", tool_input=call, tool_response={"stdout": "", "stderr": "", "interrupted": False}, tool_use_id=f"sim-{self.calls}")
        return seen

    def write_action(self, world: World) -> Observation:
        if not self.current_task:
            if not world.open_tasks:
                return self.read_action(world)
            self.current_task = world.open_tasks.pop(0)
            return self.command(["task", "start", str(self.current_task)])
        self.writes += 1
        if self.writes >= WRITES_PER_TASK:
            task, self.current_task, self.writes = self.current_task, 0, 0
            return self.command(["task", "complete", str(task), "--how", "written"])
        edit = {"file_path": f"src/part_{self.current_task}.py", "content": f"PART = {self.writes}\n"}
        return self.tool("Write", edit, {"type": "create"})

    def read_action(self, world: World) -> Observation:
        return self.tool("Read", {"file_path": "README.md"}, {"type": "text"})

    def dispatch_action(self, world: World) -> Observation:
        if not world.open_tasks:
            return self.read_action(world)
        task, number = world.open_tasks.pop(0), world.next_worker
        seen = self.command(["worker", "dispatch", f"Worker {number}", "--task", str(task), "--changes", "the files of its task", "--profile", "journal-medior", "--model", "fast", "--tests", "Scoped tests"])
        if seen.answer[0] == 0:
            world.next_worker += 1
            world.workers_out[number] = self.simulator.source.seconds() + self.worker_seconds
            self.simulator.run(["clock-in"], Caller.worker("main", number, f"w{number}", "claude"))
        else:
            world.open_tasks.insert(0, task)
        return seen

    def merge_action(self, world: World) -> Observation:
        if not world.workers_done:
            return self.read_action(world)
        number = world.workers_done.pop(0)
        self.command(["worker", "check", str(number), "1"])
        return self.command(["worker", "merge", str(number)])

    def stop_action(self, world: World) -> Observation:
        return self.simulator.hook("Stop")

    def message_action(self, world: World) -> Observation:
        return self.command(["message", "send", "a word on the work"])
