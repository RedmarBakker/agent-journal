import re
import shlex
import random

from journal.features.shell.support.shell_record import ShellRecord
from journal.support.caller import Caller
from tests.observation import Observation
from tests.simulation.job_lengths import JobLengths
from tests.simulation.simulator import Simulator
from tests.simulation.world import World

AGENT = Caller.agent("main", "s1", "claude")
WRITES_PER_TASK = 4
LINES_PER_WRITE = 4


class MainAgent:
    """The simulated main agent: it plays the action its policy picks from the world and every line said since its previous action, at its own steps, the user's and the workers', through the same hooks a real agent sends, each journal command as a shell tool use that a hold can refuse, each task's part committed through the shell's recording as a real commit is, written with the editor or a shell heredoc, a clocked-out job sent back at the scenario's shares, and keeps the world up to date with what it did."""

    def __init__(self, simulator: Simulator, policy, chance: random.Random, jobs: JobLengths, send_backs: tuple[float, ...]) -> None:
        self.simulator, self.policy, self.chance, self.jobs, self.send_backs = simulator, policy, chance, jobs, send_backs
        self.returns: dict[int, int] = {}
        self.current_task, self.writes, self.calls = 0, 0, 0

    def act(self, world: World) -> tuple[str, Observation]:
        world.refusal_lines = self.simulator.refusals_since()
        action = self.policy.action(world, self.chance, self.simulator.lines_since())
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
        return self.written(world, self.editor_write)

    def shell_write_action(self, world: World) -> Observation:
        return self.written(world, self.shell_write)

    def written(self, world: World, writer) -> Observation:
        if not self.current_task:
            if not world.open_tasks:
                return self.read_action(world)
            self.current_task = world.open_tasks.pop(0)
            return self.command(["task", "start", str(self.current_task)])
        self.writes += 1
        if self.writes >= WRITES_PER_TASK:
            task, self.current_task, self.writes = self.current_task, 0, 0
            self.commit(task)
            return self.command(["task", "complete", str(task), "--how", "written"])
        path = f"src/part_{self.current_task}.py"
        self.simulator.ledger.wrote(path, LINES_PER_WRITE)
        return writer(path)

    def editor_write(self, path: str) -> Observation:
        return self.tool("Write", {"file_path": path, "content": f"PART = {self.writes}\n"}, {"type": "create"})

    def shell_write(self, path: str) -> Observation:
        line = f"cat > {path} <<'EOF'\nPART = {self.writes}\nEOF"
        return self.tool("Bash", {"command": line, "description": "Write the part"}, {"stdout": "", "stderr": "", "interrupted": False})

    def commit(self, task: int) -> Observation:
        line = f"git commit -m 'the part of task {task}'"
        self.simulator.ledger.committed(f"the part of task {task}", int(self.simulator.source.seconds()))
        self.calls += 1
        call, use = {"command": line, "description": "Commit the task's part"}, f"sim-{self.calls}"
        held = self.simulator.hook("PreToolUse", tool_name="Bash", tool_input=call, tool_use_id=use)
        if held.is_refused():
            return held
        record, chain, root = self.simulator.app.container.get(ShellRecord), f"sim-commit-{self.calls}", self.simulator.app.config.root
        record.start(chain, line, root / ".journal" / "runs" / chain, AGENT, ran_in=str(root))
        record.finish_part(chain, line, 0, 0.1, "", [], AGENT)
        record.foreground_end(chain, 0, AGENT)
        return self.simulator.hook("PostToolUse", tool_name="Bash", tool_input=call, tool_response={"stdout": "", "stderr": "", "interrupted": False}, tool_use_id=use)

    def remedy_action(self, world: World) -> Observation:
        return self.command(world.remedies.pop(0)) if world.remedies else self.read_action(world)

    def idle_action(self, world: World) -> Observation:
        return self.simulator.observe()

    def read_action(self, world: World) -> Observation:
        return self.tool("Read", {"file_path": "README.md"}, {"type": "text"})

    def dispatch_action(self, world: World) -> Observation:
        if not world.open_tasks:
            return self.read_action(world)
        if world.idle_workers:
            return self.queue_action(world)
        task = world.open_tasks.pop(0)
        seen = self.command(["worker", "dispatch", f"Worker {world.next_worker}", "--task", str(task), "--changes", "the files of its task", "--profile", "journal-medior", "--model", "fast", "--tests", "Scoped tests"])
        if seen.answer[0] == 0:
            world.next_worker += 1
            self.sent_out(world, int(re.search(r"worker (\d+)", str(seen.answer[1])).group(1)))
        else:
            world.open_tasks.insert(0, task)
        return seen

    def queue_action(self, world: World) -> Observation:
        number, task = world.idle_workers.pop(0), world.open_tasks.pop(0)
        seen = self.command(["worker", "queue", str(number), str(task)])
        if seen.answer[0] == 0:
            self.sent_out(world, number)
        else:
            world.open_tasks.insert(0, task)
            world.idle_workers.insert(0, number)
        return seen

    def sent_out(self, world: World, number: int) -> None:
        world.workers_out[number] = self.simulator.source.seconds() + self.jobs.seconds()
        self.simulator.run(["clock-in"], Caller.worker("main", number, f"w{number}", "claude"))

    def merge_action(self, world: World) -> Observation:
        if not world.workers_done:
            return self.read_action(world)
        if self.is_sent_back(world.workers_done[0]):
            return self.send_back(world, world.workers_done.pop(0))
        number = world.workers_done.pop(0)
        self.command(["worker", "check", str(number), "1"])
        merged = self.command(["worker", "merge", str(number)])
        if merged.answer[0] == 0:
            world.idle_workers.append(number)
        return merged

    def is_sent_back(self, number: int) -> bool:
        returned = self.returns.get(number, 0)
        if returned >= len(self.send_backs):
            return False
        share = self.send_backs[returned] / (self.send_backs[returned - 1] if returned else 1.0)
        return self.chance.random() < share

    def send_back(self, world: World, number: int) -> Observation:
        self.returns[number] = self.returns.get(number, 0) + 1
        seen = self.command(["worker", "check", str(number), "1", "--short", "name the case it misses"])
        world.workers_out[number] = self.simulator.source.seconds() + self.jobs.seconds()
        return seen

    def stop_action(self, world: World) -> Observation:
        return self.simulator.hook("Stop")

    def answer_action(self, world: World) -> Observation:
        unread = self.command(["message", "unread"])
        world.unread_messages = 0
        for number in re.findall(r"message (\d+) from the user", str(unread.answer[1])):
            unread = self.command(["message", "send", "on it", "--reply-to", number])
        return unread

    def message_action(self, world: World) -> Observation:
        return self.command(["message", "send", "a word on the work"])
