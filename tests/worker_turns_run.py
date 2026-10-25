# Runs a worker's test turn through a real journal server and its shell shim as processes, so it is not in the default run: python3 -m pytest -q tests/worker_turns_run.py
"""A worker's shell sends journal tests turn to the server, which runs the project's test command in the worker's place within the budget and hands the result back."""
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

import pytest

from journal.app import App
from journal.config import Config
from journal.features.workers.workers_options import WorkersOptions
from journal.models.test_turn_state import TestTurnState
from journal.models.worker import Worker
from journal.repositories.scope import Scope
from journal.repositories.setting_rows import SettingRows
from journal.repositories.test_turns import TestTurns
from journal.repositories.workers import Workers
from journal.support.actor import Actor
from journal.support.agent_token import AgentToken
from tests.main_journal import main_journal

SHIM = Path(__file__).resolve().parent.parent / "src" / "journal.sh"


@pytest.fixture(scope="module")
def boot():
    def booted(root: Path, patch: pytest.MonkeyPatch) -> App:
        app = main_journal(Config(root, port=0))
        app.runtime().boot()
        app.server().start()
        return app
    return booted


def test_two_workers_turns_run_one_after_the_other_under_a_budget_of_one_and_each_is_handed_its_result(app: App):
    root, scope = app.config.root, app.container.get(Scope)
    (app.config.home / "port").write_text(str(app.server().port))
    (root / "tests").mkdir(exist_ok=True)
    (root / "tests" / "test_passing.py").write_text("import time\n\n\ndef test_passes():\n    time.sleep(2)\n")
    (root / "tests" / "test_failing.py").write_text("def test_fails():\n    assert 1 == 2\n")
    settings = app.container.get(SettingRows)
    settings.set(WorkersOptions.TEST_COMMAND.key, f"{sys.executable} -m pytest -q -p no:cacheprovider", Actor.user(1))
    settings.set(WorkersOptions.TEST_RUNS.key, 1, Actor.user(1))
    with scope.environment(1):
        workers = [app.container.get(Workers).save(Worker(environment_id=1, name=f"Worker {n}", brief="b", session=f"w{n}", token_hash=AgentToken.hashed("tok")), Actor.system()) for n in (1, 2)]
    results = {}

    def turn(worker: Worker, test: str) -> None:
        env = {**os.environ, "JOURNAL_ROOT": str(root), "JOURNAL_ACTOR": f"worker:{worker.id}", "JOURNAL_ACTOR_TOKEN": "tok"}
        results[worker.id] = subprocess.run(["sh", str(SHIM), "tests", "turn", test], capture_output=True, text=True, timeout=120, env=env, cwd=root)

    first = threading.Thread(target=turn, args=(workers[0], "tests/test_passing.py"))
    first.start()
    states = lambda: [row.state for row in app.container.get(TestTurns).rows()]
    end = time.time() + 20
    while TestTurnState.RUNNING not in states() and time.time() < end:
        time.sleep(0.1)
    second = threading.Thread(target=turn, args=(workers[1], "tests/test_failing.py"))
    second.start()
    waited = False
    while second.is_alive() and first.is_alive() and not waited:
        waited = TestTurnState.WAITING in states()
        time.sleep(0.1)
    first.join(120)
    second.join(120)
    assert waited, "the second turn waited for the first under a budget of 1"
    assert results[workers[0].id].returncode == 0 and "1 passed" in results[workers[0].id].stdout, results[workers[0].id].stdout + results[workers[0].id].stderr
    assert results[workers[1].id].returncode == 0 and "test_failing.py" in results[workers[1].id].stdout and "1 failed" in results[workers[1].id].stdout, results[workers[1].id].stdout + results[workers[1].id].stderr
    assert set(states()) == {TestTurnState.ENDED}, "both places are freed"
