from journal.features.workers.support.clash_return import ClashReturn
from journal.repositories.workers import Workers
from journal.support.actor import Actor
from journal.support.caller import Caller
from tests.simulation.simulator import Simulator
from tests.simulation.world import World


class WorkerActor:
    """The simulated workers: each one out proves its point and clocks out once its time on the task has passed, and its work then waits to be merged; a script may also end one unfinished, as a process that died, or have its branch clash, as when a merge landed under it."""

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

    def ends_unfinished(self, world: World, number: int) -> None:
        workers = self.simulator.app.container.get(Workers)
        workers.save(workers.find(number).unfinished(self.simulator.source.seconds(), "the process ended"), Actor.system())
        world.workers_out.pop(number, None)

    def clashes(self, world: World, number: int, clashing: str) -> object:
        workers = self.simulator.app.container.get(Workers)
        self.simulator.app.container.get(ClashReturn).send(workers.find(number), clashing)
        world.workers_done.remove(number)
        world.workers_out[number] = self.simulator.source.seconds() + 60
        return self.simulator.observer.observe()
