from journal.support.caller import Caller
from tests.simulation.simulator import Simulator
from tests.simulation.world import World


class WorkerActor:
    """The simulated workers: each one out proves its point and clocks out once its time on the task has passed, and its work then waits to be merged."""

    def __init__(self, simulator: Simulator) -> None:
        self.simulator = simulator

    def finished(self, world: World) -> list[tuple[int, object]]:
        now = self.simulator.source.seconds()
        done = sorted(number for number, due in world.workers_out.items() if due <= now)
        seen = []
        for number in done:
            caller = Caller.worker("main", number, f"w{number}", "claude")
            self.simulator.run(["proof", "1", f"part_{number}.py:1"], caller)
            seen.append((number, self.simulator.run(["clock-out", "the part is written"], caller)))
            del world.workers_out[number]
            world.workers_done.append(number)
        return seen
