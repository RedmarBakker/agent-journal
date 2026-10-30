# Runs workers as real processes (a shell in the worker's place, a sleeping process for a live session), so it is not in the default run: python3 -m pytest -q tests/worker_processes_run.py
"""What a worker's real run leaves behind: the marks of its dispatch, its end, a stop and a release, and the marks of each later moment."""
from worker_dispatch import started_run
from journal.repositories.workers import Workers
import time as timing
from pathlib import Path

import pytest

from journal.app import App
from journal.repositories.scope import Scope
from journal.support.actor import Actor
from journal.support.caller import Caller
from tests.test_features import AGENT, MAIN, USER, booted, dispatched, hook, kept_conversation, listening_session


@pytest.fixture(scope="module")
def boot():
    return booted


@pytest.fixture
def app(app: App):
    with app.container.get(Scope).environment(MAIN):
        yield app


def test_a_workers_dispatch_mark_stays_and_each_later_standing_is_a_new_mark(app: App):
    """A worker's dispatch is one mark that stays as it went out; its run ending, a stop and a release each add a mark at the bottom, and only a dispatch that could not start turns its own mark red."""
    from journal.features.workers.support.worker_runner import WorkerRunner
    from journal.repositories.messages import Messages as MessageRows
    from journal.repositories.workers import Workers
    hook(app, "SessionStart")
    console = app.console()
    for name in ("Lady Lovelace", "Dr. Einstein", "Mr. Babbage"):
        dispatched(console, [name, f"a job for {name}", "--changes", "the files of its task", "--tests", "Scoped tests", "--profile", "journal-medior", "--model", "sonnet"], AGENT)
    messages = app.container.get(MessageRows)
    card = lambda n: next(m for m in messages.scoped() if m.data.get("key") == f"worker:{n}")
    marks = lambda n: [m.text for m in messages.scoped() if str(m.data.get("key", "")).startswith(f"worker:{n}:")]
    assert card(1).text == "Lady Lovelace: started on claude sonnet" and card(1).data["detail"] == "a job for Lady Lovelace" and card(1).data["shows"] == "workers"
    runner, workers = app.container.get(WorkerRunner), app.container.get(Workers)
    started_run(runner, app.container.get(Workers), workers.find(1), ["sh", "-c", 'echo "the footer is fixed"; test -n "$JOURNAL_ACTOR_TOKEN" || exit 9; test "$JOURNAL_ROOT" = "$0" || exit 8', str(app.config.root)], Actor.agent("s1"))
    first_hash = workers.find(1).token_hash
    started_run(runner, app.container.get(Workers), workers.find(2), ["sh", "-c", "echo broken >&2; exit 3"], Actor.agent("s1"))
    started_run(runner, app.container.get(Workers), workers.find(3), ["sh", "-c", "true"], Actor.agent("s1"))
    assert first_hash == "" and workers.find(3).token_hash == "", "a run carries its token in its process, and the token is cleared when the run ends without clocking out"
    console.run(["worker", "stop", "3"], AGENT)
    assert card(1).text == "Lady Lovelace: started on claude sonnet", "the dispatch mark stays as it went out"
    assert marks(1) == ["Lady Lovelace: stopped before it finished"], "a run that ends without clocking out is a new mark"
    assert marks(2) == ["Dr. Einstein: stopped before it finished"] and marks(3)[-1] == "Mr. Babbage: stopped"
    console.run(["worker", "release", "1"], AGENT)
    assert marks(1)[-1] == "Lady Lovelace: released" and card(1).text.endswith("started on claude sonnet"), "and a release is one more"
    newest = [m for m in messages.scoped() if str(m.data.get("key", "")).startswith("worker:")][-1]
    assert newest.text == "Lady Lovelace: released", "each new mark lands at the bottom of the chat"


def test_each_worker_moment_after_its_dispatch_is_a_short_mark_of_its_own(app: App, tmp_path, monkeypatch):
    import subprocess
    from journal.models.message import Message
    from journal.repositories.messages import Messages
    from journal.repositories.workers import Workers
    home = tmp_path / "home"
    monkeypatch.setattr(Path, "home", staticmethod(lambda: home))
    monkeypatch.delenv("CLAUDE_CONFIG_DIR", raising=False)
    kept_conversation(app, monkeypatch)
    hook(app, "SessionStart")
    console, workers, messages = app.console(), app.container.get(Workers), app.container.get(Messages)
    marks = lambda: [(m.text, m.data.get("outcome", ""), m.data.get("detail")) for m in messages.scoped() if m.data.get("shows") == "worker_steps" and not m.data.get("key")]
    dispatched(console, ["Mr. Wedgwood", "the vase", "--changes", "the files of its task", "--tests", "Scoped tests", "--profile", "journal-medior", "--model", "sonnet"], AGENT)
    console.run(["worker", "report", "1", "the vase is fired"], Caller.agent("main", "w1", "claude"))
    workers.save(workers.find(1).with_(resume="w-1"), USER.actor)
    console.run(["worker", "send", "1", "the jug"], AGENT)
    process = subprocess.Popen(["sleep", "30"])
    try:
        workers.save(workers.find(1).running_as(process.pid, timing.time()), Actor.system())
        listening_session(home, process.pid, "w-1")
        console.run(["worker", "notify", "1", "a blue glaze"], AGENT)
    finally:
        process.kill()
        process.wait(5)
    console.run(["worker", "stop", "1"], AGENT)
    console.run(["worker", "send", "1", "the teapot"], AGENT)
    console.run(["worker", "report", "1", "the teapot pours"], Caller.agent("main", "w1", "claude"))
    console.run(["worker", "complete", "1"], AGENT)
    assert marks() == [
        ("Mr. Wedgwood: sent its next job", "", "the jug"),
        ("Mr. Wedgwood: started again in its last session", "", "the teapot"),
        ("Mr. Wedgwood: retired, its report acted on", "", ""),
    ]
    assert all(len(text) <= 80 for text, _, _ in marks())
    sent = [(m.text, m.session, m.data.get(Message.RECIPIENT_KEY)) for m in messages.scoped() if m.data.get("kind") == Message.PEER]
    assert sent == [("a blue glaze", "s1", "worker 1, Mr. Wedgwood")], "a notify is a message sent to the worker in the dispatcher's chat, its whole text, as a message to any other agent is, never a worker mark"
