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


def worker_hook(app: App, row: Worker, kind: str, **body) -> tuple[int, dict]:
    return posted(app, "/hooks/claude", {"hook_event_name": kind, "session_id": row.session, **body}, {"X-Journal-Env": "main", "X-Journal-Actor": f"worker:{row.id}", "X-Journal-Actor-Token": TOKEN})


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
    assert "the parser reads" in console.run(["memory", "list"], as_lovelace).text and "release notes" not in console.run(["memory", "list"], as_lovelace).text, "a worker lists its own memories alone"
    assert "release notes" in console.run(["memory", "list"], AGENT).text and "the parser reads" not in console.run(["memory", "list"], AGENT).text, "and the main agent its own"
    compacted(app, lovelace)
    assert memories.find(own).weight == 5 and memories.find(main_memory).weight == 5, "the worker's compaction fades its own memory and leaves the main agent's"
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


def test_each_agent_lists_weighs_removes_and_fades_only_its_own_memories_and_a_subagent_keeps_none(app: App):
    console, memories = app.console(), app.container.get(Memories)
    main_memory = made(console.run(["memory", "add", "the main agent keeps the release notes"], AGENT))
    _, as_lovelace = sent(app, "Lady Lovelace", "w1")
    _, as_babbage = sent(app, "Mr. Babbage", "w2")
    lovelace_memory = made(console.run(["memory", "add", "the parser reads tokens"], as_lovelace))
    babbage_memory = made(console.run(["memory", "add", "the engine turns in decimal"], as_babbage))
    assert "the parser reads" not in console.run(["memory", "list"], as_babbage).text and "the engine turns" not in console.run(["memory", "list"], as_lovelace).text, "a worker never lists another worker's memories"
    for caller, number in ((as_lovelace, main_memory), (as_babbage, lovelace_memory), (AGENT, babbage_memory)):
        refused = console.run(["memory", "weigh", str(number), "3"], caller)
        assert refused.code == 1 and "that is yours" in refused.error, f"weighing memory {number} that another agent owns is refused"
        assert console.run(["memory", "remove", str(number)], caller).code == 1, f"and so is removing it: memory {number}"
    assert memories.find(main_memory).weight == memories.find(lovelace_memory).weight == memories.find(babbage_memory).weight == 5 and memories.find(lovelace_memory).removed_at is None
    assert console.run(["memory", "remove", str(lovelace_memory)], as_lovelace).code == 0 and memories.find(lovelace_memory).removed_at is not None, "its owner removes it"
    reviewer = console.run(["memory", "list"], Caller.reviewer("main", 9, "r1", "claude"))
    assert reviewer.code == 0 and "release notes" not in reviewer.text and "the engine turns" not in reviewer.text, "a reviewer lists its own, which are none"
    for subagent in (AGENT.subagent_caller(), as_babbage.subagent_caller()):
        assert console.run(["memory", "list"], subagent).code == 1 and console.run(["memory", "weigh", str(main_memory), "3"], subagent).code == 1, "a subagent's command names no row of its own, so it lists and weighs no memory at all, its agent's neither"
    hook(app, "PreCompact", trigger="auto")
    app.runtime().deferred.drain()
    assert memories.find(main_memory).weight == 4 and memories.find(babbage_memory).weight == 5, "the main agent's compaction fades its own memories alone"
    hook(app, "SessionStart", source="compact")
    overview = console.run(["environment", "overview"], AGENT).text
    assert "release notes" in overview and "the engine turns" not in overview, "the main agent's overview opens with its own memories alone"


def test_a_worker_weighs_its_own_memories_at_its_own_marks_and_the_main_agents_decision_leaves_it_weighing(app: App):
    console, sessions = app.console(), app.container.get(SessionAgents)
    made(console.run(["memory", "add", "the main agent keeps the release notes"], AGENT))
    lovelace, as_lovelace = sent(app, "Lady Lovelace", "w1")
    assert console.run(["clock-in"], as_lovelace).code == 0
    made(console.run(["memory", "add", "the parser reads tokens", "--weight", "7"], as_lovelace))
    made(console.run(["memory", "add", "the lexer is next", "--weight", "4"], as_lovelace))
    context(app, "w1", 55)
    status, body = worker_hook(app, lovelace, "PreToolUse", tool_name="Read", tool_input={"file_path": "a.py"})
    assert status == 200 and nudge_reached(app, told(body), MemoryNudges.CONTEXT_DECISION, percent=50, count=2), "at the mark of its own context window the worker is told to weigh its own two memories"
    assert type(sessions.top("w1")) is WeighingMemories and type(sessions.top("s1")) is not WeighingMemories, "the mark pushes WeighingMemories over the worker's work alone"
    assert worker_hook(app, lovelace, "PreToolUse", tool_name="Write", tool_input={"file_path": "a.py"})[0] == 409, "its writes wait"
    context(app, "s1", 55)
    hook(app, "PreToolUse", tool_name="Read", tool_input={})
    assert type(sessions.top("s1")) is WeighingMemories
    assert console.run(["memory", "skip", "nothing new"], AGENT).code == 0
    assert type(sessions.top("s1")) is not WeighingMemories and type(sessions.top("w1")) is WeighingMemories, "the main agent's decision pops its own weighing and leaves the worker's"
    assert console.run(["memory", "skip", "nothing to keep"], as_lovelace).code == 0
    assert type(sessions.top("w1")) is not WeighingMemories and worker_hook(app, lovelace, "PreToolUse", tool_name="Write", tool_input={"file_path": "a.py"})[0] == 200, "its own skip pops it and its work goes on"


def test_two_environments_memories_never_mix_and_a_subagents_compaction_fades_none(app: App):
    console, memories, scope = app.console(), app.container.get(Memories), app.container.get(Scope)
    other = Caller.user("other")
    main_memory = made(console.run(["memory", "add", "the main project ships on fridays"], AGENT))
    other_memory = made(console.run(["memory", "add", "the other project ships on mondays"], other))
    assert "mondays" not in console.run(["memory", "list"], AGENT).text and "fridays" not in console.run(["memory", "list"], other).text, "each environment lists its own memories alone"
    assert console.run(["memory", "weigh", str(other_memory), "3"], AGENT).code == 1, "and refuses a number from another environment"
    hook(app, "PreCompact", trigger="auto", agent_id="sub-1")
    app.runtime().deferred.drain()
    assert memories.find(main_memory).weight == 5, "a subagent's compaction fades no memory, its agent's neither"
    hook(app, "PreCompact", trigger="auto")
    app.runtime().deferred.drain()
    assert memories.find(main_memory).weight == 4, "the main agent's compaction fades its own"
    with scope.environment(app.container.get(Environments).lookup("other").id):
        assert memories.find(other_memory).weight == 5, "and leaves another environment's"
