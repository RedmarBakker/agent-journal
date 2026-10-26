from journal.engine.clock import Clock
from journal.features.workers.support.worker_actions import WorkerActions
from journal.features.workers.support.worker_runner import WorkerRunner
from journal.support.time_source import TimeSource
from tests.observation import Observation, Observer
from tests.replay import catch_typed, hook_as

START_SECONDS = 1_800_000_000.0


class Simulator:
    """One journal driven in-process by a simulation: no worker process starts, no line reaches a terminal, the time is pinned and moves only when a step says so, and every step closes with an observation once the worker thread has settled."""

    def __init__(self, app, monkeypatch, provider: str = "claude") -> None:
        self.app, self.provider, self.typed, self.steps = app, provider, [], []
        monkeypatch.setattr(WorkerRunner, "start", lambda self, worker, actor: None)
        monkeypatch.setattr(WorkerActions, "resumable", lambda self, worker: None)
        catch_typed(app, monkeypatch, self.typed)
        self.source = app.container.get(TimeSource)
        self.source.pin(START_SECONDS)
        self.app.container.get(Clock).held_at = START_SECONDS
        self.observer = Observer(app, self.typed)

    def hook(self, kind: str, session: str = "s1", **body) -> Observation:
        return self.observer.observe(hook_as(self.app, self.provider, kind, session, **body))

    def run(self, argv: list[str], caller) -> Observation:
        outcome = self.app.console().run(argv, caller)
        return self.observer.observe((outcome.code, outcome.error or outcome.text))

    def advance(self, seconds: float) -> None:
        self.source.pin(self.source.seconds() + seconds)
        self.app.container.get(Clock).held_at = self.source.seconds()

    def step(self, name: str, answer=None) -> None:
        seen = self.observer.observe(answer)
        self.steps.append({"name": name, "answer": answer, "typed": list(seen.typed), "nudges": list(seen.nudges), "stack": list(seen.stack)})

    def record(self) -> list[dict]:
        return list(self.steps)
