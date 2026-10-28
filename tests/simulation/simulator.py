from journal.engine.clock import Clock
from journal.features.git.listeners.commit_detection import CommitDetection
from journal.features.git.support.git_facts import GitFacts
from journal.features.workers.support.worker_branch import WorkerBranch
from journal.features.workers.support.worker_actions import WorkerActions
from journal.features.workers.support.worker_runner import WorkerRunner
from journal.features.workers.support.machine_load import MachineLoad
from journal.support.time_source import TimeSource
from tests.observation import Observation, Observer
from tests.replay import typing_capture, hook_as
from tests.simulation.commit_ledger import CommitLedger

START_SECONDS = 1_800_000_000.0
MERGED_LINES = 40


class Simulator:
    """One journal driven in-process by a simulation: no worker process starts, no line reaches a terminal, the jobs thread is stopped and the machine's load is fixed, git is a ledger of the commits the run made and a merge brings a fixed count of lines, the time is pinned and moves only when a step says so, the clock ticks when the run says a minute has passed, and every step closes with an observation once the worker thread has settled, the lines it said kept until the agent next acts."""

    def __init__(self, app, monkeypatch, provider: str = "claude") -> None:
        self.app, self.provider, self.typed, self.steps = app, provider, [], []
        monkeypatch.setattr(WorkerRunner, "start", lambda self, worker, actor: None)
        monkeypatch.setattr(WorkerActions, "resumable", lambda self, worker: None)
        monkeypatch.setattr(MachineLoad, "read", classmethod(lambda cls: cls((1.0, 1.0, 1.0), 8, 8000)))
        self.ledger = CommitLedger()
        monkeypatch.setattr(GitFacts, "run", staticmethod(lambda folder, *arguments: self.ledger.git(*arguments)))
        monkeypatch.setattr(CommitDetection, "head", lambda detection, folder: self.ledger.head())
        monkeypatch.setattr(WorkerBranch, "merged_lines", lambda branch, worker: MERGED_LINES)
        app.runtime().jobs.stop()
        typing_capture(app, monkeypatch, self.typed)
        self.source = app.container.get(TimeSource)
        self.source.pin(START_SECONDS)
        self.app.container.get(Clock).held_at = START_SECONDS
        self.observer = Observer(app, self.typed)
        self.said: list[tuple[str, str]] = []
        self.refusals: list[str] = []

    def hook(self, kind: str, session: str = "s1", **body) -> Observation:
        return self.heard(self.observer.observe(hook_as(self.app, self.provider, kind, session, **body)))

    def run(self, argv: list[str], caller) -> Observation:
        outcome = self.app.console().run(argv, caller)
        return self.heard(self.observer.observe((outcome.code, outcome.error or outcome.text)))

    def heard(self, seen: Observation) -> Observation:
        self.said.extend(zip(seen.nudges, seen.lines))
        if seen.is_refused():
            self.refusals.extend(seen.lines[-1:])
        return seen

    def lines_since(self) -> tuple[tuple[str, str], ...]:
        lines, self.said = tuple(self.said), []
        return lines

    def refusals_since(self) -> list[str]:
        lines, self.refusals = list(self.refusals), []
        return lines

    def advance(self, seconds: float) -> None:
        self.source.pin(self.source.seconds() + seconds)
        self.app.container.get(Clock).held_at = self.source.seconds()

    def tick(self) -> None:
        self.app.container.get(Clock).tick(self.source.seconds())
        self.app.runtime().deferred.drain()

    def observe(self) -> Observation:
        return self.heard(self.observer.observe())

    def step(self, name: str, answer=None) -> None:
        seen = self.observer.observe(answer)
        self.steps.append({"name": name, "answer": answer, "typed": list(seen.typed), "nudges": list(seen.nudges), "stack": list(seen.stack)})

    def record(self) -> list[dict]:
        return list(self.steps)
