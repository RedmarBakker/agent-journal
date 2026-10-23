import faulthandler
import sys
import threading
import time as timing
import traceback

from journal.engine.clock import Clock
from journal.engine.job import Job
from journal.events.bus import Bus
from journal.events.slow_tick import SlowTick

SLOW_TICK_SECONDS = 1.0
STALL_SECONDS = 5.0
IDLE_SECONDS = 60.0


class JobRunner:
    """The engine's one thread for work on a schedule: from each start, every registered job is ticked once its interval has passed and the thread sleeps until the next is due; a tick that raises is logged and the job ticked again at its next turn, and a tick that runs long is logged and told on the bus; one still running after five seconds has every thread's stack written to the log, so a stall names what holds it."""

    def __init__(self, clock: Clock, bus: Bus) -> None:
        self.clock, self.bus = clock, bus
        self.jobs: list[Job] = []
        self.due_at: dict[Job, float] = {}
        self._waking = threading.Event()
        self._stopping = threading.Event()
        self._thread: threading.Thread | None = None

    def register(self, job: Job) -> None:
        self.jobs.append(job)
        self._waking.set()

    def start(self) -> None:
        self._stopping.clear()
        self.due_at.clear()
        self._thread = threading.Thread(target=self._run, name="jobs", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stopping.set()
        self._waking.set()
        if self._thread:
            self._thread.join()
            self._thread = None

    def _run(self) -> None:
        while not self._stopping.is_set():
            self._waking.clear()
            self._waking.wait(self.run_due(self.clock.time()))

    def run_due(self, time: float) -> float:
        for job in list(self.jobs):
            if self.due_at.setdefault(job, time + job.interval_seconds) > time:
                continue
            self.ticked(job, time)
            self.due_at[job] = time + job.interval_seconds
        return max(0.0, min(self.due_at.values(), default=time + IDLE_SECONDS) - time)

    def ticked(self, job: Job, time: float) -> None:
        name, began = type(job).__name__, timing.monotonic()
        faulthandler.dump_traceback_later(STALL_SECONDS, file=sys.stderr)
        try:
            job.tick(time)
        except Exception:
            sys.stderr.write(f"job {name} failed:\n{traceback.format_exc()}")
        finally:
            faulthandler.cancel_dump_traceback_later()
        seconds = timing.monotonic() - began
        if seconds > SLOW_TICK_SECONDS:
            sys.stderr.write(f"job {name} took {seconds:.1f} seconds for one tick\n")
            self.bus.dispatch(SlowTick(job=name, seconds=round(seconds, 1)))
