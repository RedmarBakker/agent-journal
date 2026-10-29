"""Each agent's memories are its own: the main agent's and each worker's are kept, shown, weighed, removed and faded apart, every agent simulated in-process, and a subagent keeps none."""

import json

import pytest

from journal.app import App
from journal.engine.support.session_agents import SessionAgents
from journal.features.memory.memory_nudges import MemoryNudges
from journal.features.memory.states.weighing_memories import WeighingMemories
from journal.models.support.ref import Ref
from journal.models.task import Task
from journal.models.worker import Worker
from journal.providers.claude import Claude
from journal.repositories.environments import Environments
from journal.repositories.memories import Memories
from journal.repositories.scope import Scope
from journal.repositories.tasks import Tasks
from journal.repositories.workers import Workers
from journal.support.actor import Actor
from journal.support.agent_token import AgentToken
from journal.support.caller import Caller
from nudge_lines import nudge_reached
from tests.in_process import posted
from tests.test_features import booted, hook, made

AGENT = Caller.agent("main", "s1", "claude")
MAIN = 1
TOKEN = "tok"


@pytest.fixture(scope="module")
def boot():
    return booted


@pytest.fixture
def app(app: App):
    with app.container.get(Scope).environment(MAIN):
        hook(app, "SessionStart")
        app.console().run(["environment", "overview"], AGENT)
        yield app


def sent(app: App, name: str, session: str) -> tuple[Worker, Caller]:
    """A worker sent on a task of its own, its agent's row made by its first hook, and the caller its commands run as."""
    workers, tasks = app.container.get(Workers), app.container.get(Tasks)
    row = workers.save(Worker(environment_id=MAIN, name=name, brief="b", session=session, token_hash=AgentToken.hashed(TOKEN)), Actor.system())
    tasks.handover(tasks.save(Task(environment_id=MAIN, title=f"the job of {name}", brief="b"), Actor.system()), Ref.build(row), Actor.system())
    worker_hook(app, row, "SessionStart", source="startup")
    return row, Caller.worker("main", row.id, session, "claude")


def worker_hook(app: App, row: Worker, type_name: str, **body) -> tuple[int, dict]:
    return posted(app, "/hooks/claude", {"hook_event_name": type_name, "session_id": row.session, **body}, {"X-Journal-Env": "main", "X-Journal-Actor": f"worker:{row.id}", "X-Journal-Actor-Token": TOKEN})


def compacted(app: App, row: Worker) -> None:
    worker_hook(app, row, "PreCompact", trigger="auto")
    app.runtime().deferred.drain()
    worker_hook(app, row, "SessionStart", source="compact")


def context(app: App, session: str, percent: int) -> None:
    app.config.status_home.mkdir(parents=True, exist_ok=True)
    (app.config.status_home / f"{session}.json").write_text(json.dumps({"context_window": {"used_percentage": percent}}))


def told(body: dict) -> str:
    return body.get("hookSpecificOutput", {}).get("additionalContext", "")


def test_a_worker_sent_its_next_job_is_shown_its_own_memories_faded_by_its_compactions_and_never_the_main_agents(app: App, monkeypatch):
    conversation = app.config.root / "conversation.jsonl"
    conversation.write_text("{}\n")
    monkeypatch.setattr(Claude, "transcript", lambda self, project, session: conversation)
    console, memories, workers = app.console(), app.container.get(Memories), app.container.get(Workers)
    main_memory = made(console.run(["memory", "add", "the main agent keeps the release notes", "--weight", "5"], AGENT))
    lovelace, as_lovelace = sent(app, "Lady Lovelace", "w1")
    assert console.run(["clock-in"], as_lovelace).code == 0
    own = made(console.run(["memory", "add", "the parser reads tokens left to right", "--weight", "6"], as_lovelace))
    compacted(app, lovelace)
    workers.save(workers.find(lovelace.id).delivered(2.0), Actor.worker(lovelace.id))
    workers.save(workers.find(lovelace.id).with_(resume="w1"), Actor.system())
    assert console.run(["worker", "send", str(lovelace.id), "now the lexer"], AGENT).code == 0, "the worker that reported is sent its next job"
    assert console.run(["clock-in"], as_lovelace).code == 0
    shown = told(worker_hook(app, lovelace, "PostToolUse", tool_name="Bash", tool_input={"command": "journal clock-in"}, tool_response="")[1])
    assert nudge_reached(app, shown, MemoryNudges.WORKER_MEMORIES, memories=f"{own} (weight 5) the parser reads tokens left to right"), "once it has clocked in on the next job it is shown its memories, faded by its compaction"
    assert "release notes" not in shown, "and never the main agent's"
    babbage, as_babbage = sent(app, "Mr. Babbage", "w2")
    theirs = made(console.run(["memory", "add", "the engine turns in decimal"], as_babbage))
    assert console.run(["clock-in"], as_babbage).code == 0
    other_shown = told(worker_hook(app, babbage, "PostToolUse", tool_name="Bash", tool_input={"command": "journal clock-in"}, tool_response="")[1])
    assert nudge_reached(app, other_shown, MemoryNudges.WORKER_MEMORIES, memories=f"{theirs} (weight 5) the engine turns in decimal") and "the parser reads" not in other_shown and "release notes" not in other_shown, "another worker clocking in is shown its own memories and nobody else's"






