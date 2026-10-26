import random

from journal.support.caller import Caller
from tests.observation import Observation
from tests.simulation.simulator import Simulator
from tests.simulation.world import World

AGENT = Caller.agent("main", "s1", "claude")
WRITES_PER_TASK = 4


class MainAgent:
    """The simulated main agent: it plays the action its policy picks, through the same hooks and commands a real agent sends, and keeps the world up to date with what it did."""

    def __init__(self, simulator: Simulator, policy, chance: random.Random, worker_seconds: int) -> None:
        self.simulator, self.policy, self.chance, self.worker_seconds = simulator, policy, chance, worker_seconds
        self.current_task, self.writes = 0, 0

    def act(self, world: World) -> tuple[str, Observation]:
        action = self.policy.action(world, self.chance)
        return action, getattr(self, f"{action}_action")(world)

    def write_action(self, world: World) -> Observation:
        if not self.current_task:
            if not world.open_tasks:
                return self.read_action(world)
            self.current_task = world.open_tasks.pop(0)
            return self.simulator.run(["task", "start", str(self.current_task)], AGENT)
        self.writes += 1
        if self.writes >= WRITES_PER_TASK:
            task, self.current_task, self.writes = self.current_task, 0, 0
            return self.simulator.run(["task", "complete", str(task), "--how", "written"], AGENT)
        edit = {"file_path": f"src/part_{self.current_task}.py", "content": f"PART = {self.writes}\n"}
        self.simulator.hook("PreToolUse", tool_name="Write", tool_input=edit)
        return self.simulator.hook("PostToolUse", tool_name="Write", tool_input=edit, tool_response={"type": "create"})

    def read_action(self, world: World) -> Observation:
        sight = {"file_path": "README.md"}
        self.simulator.hook("PreToolUse", tool_name="Read", tool_input=sight)
        return self.simulator.hook("PostToolUse", tool_name="Read", tool_input=sight, tool_response={"type": "text"})

    def dispatch_action(self, world: World) -> Observation:
        if not world.open_tasks:
            return self.read_action(world)
        task, number = world.open_tasks.pop(0), world.next_worker
        seen = self.simulator.run(["worker", "dispatch", f"Worker {number}", "--task", str(task), "--changes", "the files of its task", "--profile", "journal-medior", "--model", "fast", "--tests", "Scoped tests"], AGENT)
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
        self.simulator.run(["worker", "check", str(number), "1"], AGENT)
        return self.simulator.run(["worker", "merge", str(number)], AGENT)

    def stop_action(self, world: World) -> Observation:
        return self.simulator.hook("Stop")

    def message_action(self, world: World) -> Observation:
        return self.simulator.run(["message", "send", "a word on the work"], AGENT)
