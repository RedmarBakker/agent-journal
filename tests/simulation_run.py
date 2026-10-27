"""The event simulator's runs: not in the default run (pytest collects only test_*.py); run with python3 -m pytest tests/simulation_run.py."""
import os
import time
from dataclasses import replace
from pathlib import Path

import pytest

from journal.config import Config
from journal.models.setting import Setting
from journal.repositories.scope import Scope
from journal.repositories.setting_rows import SettingRows
from journal.support.actor import Actor
from tests.main_journal import main_journal
from tests.replay import Frozen, differences
from tests.replays_run import a_queue_runs_to_merge
from tests.simulation.scenario import Scenario
from tests.simulation.scenario_run import POLICIES, ScenarioRun
from tests.simulation.scenarios import ALL, ENGINE_MOMENTS, HISTORY, QUIET_BUILDER
from tests.simulation.simulator import Simulator
from tests.test_features import MAIN


SEED = int(os.environ.get("SIM_SEED", "7"))
RUNS = int(os.environ.get("SIM_RUNS", "1"))
MINUTES = int(os.environ.get("SIM_MINUTES", "0"))
RUN_SECONDS = 120
HISTORY_RUN_SECONDS = 60


def fresh(folder: Path, monkeypatch) -> Simulator:
    """One fresh journal under the simulator, started, its skills off and lines delivered at once; it is stopped with the test."""
    monkeypatch.setattr(Config, "status_home", property(lambda self: self.root / "status"))
    app = main_journal(Config(folder, port=0))
    settings = app.container.get(SettingRows)
    for key, value in (("features.skills", False), ("delivery.batch_seconds", 0), ("workers.testing", "Hand the tests over")):
        settings.save(Setting(environment_id=0, key=key, value=value), Actor.system())
    app.runtime().start()
    return Simulator(app, monkeypatch)


@pytest.fixture
def simulated(tmp_path: Path, monkeypatch):
    simulator = fresh(tmp_path / "journal", monkeypatch)
    with simulator.app.container.get(Scope).environment(MAIN):
        yield simulator
    simulator.app.runtime().stop()


def played(folder: Path, monkeypatch, scenario: Scenario, seed: int, policy=None) -> list:
    simulator = fresh(folder, monkeypatch)
    try:
        with simulator.app.container.get(Scope).environment(MAIN):
            began = time.monotonic()
            trace = ScenarioRun(simulator, replace(scenario, minutes=MINUTES or scenario.minutes), seed, policy or POLICIES[scenario.policy]()).played()
            assert time.monotonic() - began < RUN_SECONDS, f"{scenario.name} ran past its time limit"
            return trace
    finally:
        simulator.app.runtime().stop()


def test_the_simulator_plays_a_queue_to_its_merge_as_the_replay_recorded_it(simulated):
    a_queue_runs_to_merge(simulated.app, simulated, "claude")
    assert differences(Frozen("a_queue_runs_to_merge_claude").record(), simulated.record(), True) == [], "the simulator sees what the frozen replay saw: the same lines typed and nudges said at each step"


def test_two_runs_of_a_scenario_from_one_seed_give_the_same_trace(tmp_path, monkeypatch):
    first = played(tmp_path / "first", monkeypatch, replace(QUIET_BUILDER, minutes=10), SEED)
    second = played(tmp_path / "second", monkeypatch, replace(QUIET_BUILDER, minutes=10), SEED)
    assert first and first == second, "a seed replays a run exactly"


@pytest.mark.parametrize("scenario", HISTORY, ids=lambda scenario: scenario.name)
def test_a_scenario_from_last_weeks_history_replays_from_its_seed(tmp_path, monkeypatch, scenario):
    first = played(tmp_path / "first", monkeypatch, replace(scenario, minutes=30), SEED)
    second = played(tmp_path / "second", monkeypatch, replace(scenario, minutes=30), SEED)
    assert first and first == second, "arrivals, job lengths, send-backs, clashes and the mode switch all replay from the seed"


@pytest.mark.parametrize("scenario", ALL, ids=lambda scenario: scenario.name)
def test_every_scenario_plays_within_its_time_limit(tmp_path, monkeypatch, scenario):
    for run in range(RUNS):
        began = time.monotonic()
        trace = played(tmp_path / f"run{run}", monkeypatch, scenario, SEED + run)
        assert any(entry.actor == "agent" for entry in trace), f"{scenario.name} played the agent"
        assert scenario not in HISTORY or time.monotonic() - began < HISTORY_RUN_SECONDS, f"{scenario.name} plays its {scenario.minutes} minutes in under {HISTORY_RUN_SECONDS} seconds"



def test_a_scripted_clash_sends_the_worker_back_and_a_third_in_a_row_is_named_to_the_agent(simulated):
    from tests.simulation.main_agent import AGENT
    from tests.simulation.worker_actor import WorkerActor
    from tests.simulation.world import World
    from journal.support.caller import Caller
    world, workers = World(), WorkerActor(simulated)
    simulated.hook("SessionStart")
    simulated.run(["environment", "overview"], AGENT)
    simulated.run(["task", "create", "part 1", "--brief", "1. part 1 is written"], Caller.user("main"))
    simulated.run(["worker", "dispatch", "Worker 1", "--task", "1", "--changes", "the files of its task", "--profile", "journal-medior", "--model", "fast", "--tests", "Scoped tests"], AGENT)
    simulated.run(["clock-in"], Caller.worker("main", 1, "w1", "claude"))
    named = []
    for _ in range(3):
        world.workers_out[1] = 0
        workers.finished(world)
        named.extend(workers.clashes(world, 1, "src/part_1.py").nudges)
        simulated.run(["clock-in"], Caller.worker("main", 1, "w1", "claude"))
    assert named.count("workers.branch_keeps_clashing") == 1, named
    assert simulated.observer.observe().skipped == 0, "no deferred work was skipped"


def test_a_policy_is_told_the_lines_its_previous_action_brought(tmp_path, monkeypatch):
    from tests.simulation.scenarios import CARELESS
    from tests.simulation.scripted_policy import ScriptedPolicy
    policy = ScriptedPolicy(["write", "write", "stop", "write", "read", "stop"])
    trace = played(tmp_path / "told", monkeypatch, replace(CARELESS, minutes=3), SEED, policy)
    agent_steps = [index for index, entry in enumerate(trace) if entry.actor == "agent"]
    between = [tuple(key for entry in trace[previous:index] for key in entry.nudges) for previous, index in zip(agent_steps, agent_steps[1:])]
    assert [tuple(key for key, _ in told) for told in policy.told[1:len(agent_steps)]] == between, "each action is told every line said since the one before, at its own step and the user's and the workers'"
    assert any(policy.told), "and it is told something in a run"


def test_the_clock_ticks_each_simulated_minute_so_an_idle_agents_load_is_measured(simulated):
    from journal.repositories.agents import Agents
    from tests.simulation.scenario_run import ScenarioRun
    from tests.simulation.scenarios import CARELESS
    from tests.simulation.scripted_policy import ScriptedPolicy
    from tests.simulation.simulator import START_SECONDS
    ScenarioRun(simulated, replace(CARELESS, minutes=20), SEED, ScriptedPolicy(["idle"] * 40)).played()
    measured = simulated.app.container.get(Agents).session_agent("s1").work_queue.measured_at
    assert measured >= START_SECONDS + 19 * 60, "an agent idle for twenty minutes still has its load measured in the last one, by the clock's tick"


@pytest.mark.parametrize("follow_rate", [1.0, 0.0])
def test_a_known_policy_follows_the_lines_it_is_told_at_its_rate(tmp_path, monkeypatch, follow_rate):
    from tests.simulation.builder_policy import BuilderPolicy
    from tests.simulation.known_policy import KnownPolicy
    from tests.simulation.nudge_response import NudgeResponse
    from tests.simulation.scenarios import BUILDER_SPREE
    policy = KnownPolicy(BuilderPolicy(), follow_rate, SEED)
    trace = played(tmp_path / "known", monkeypatch, replace(BUILDER_SPREE, minutes=30), SEED, policy)
    asked = [(entry.second, NudgeResponse.action(key)) for entry in trace for key in entry.nudges if NudgeResponse.action(key) and entry.second <= trace[-1].second - 240]
    assert asked, "the spree says lines that ask for an action"
    followed = [any(later.actor == "agent" and later.action == action and second < later.second <= second + 240 for later in trace) for second, action in asked]
    if follow_rate:
        missed = [(second, action, [(later.second, later.action) for later in trace if later.actor == "agent" and second <= later.second <= second + 300]) for (second, action), done in zip(asked, followed) if not done]
        assert not missed, f"at a follow rate of one every line asking for an action is followed by it within four simulated minutes: {missed[:2]}"
    else:
        assert not policy.due, "at a follow rate of nought none is taken up"


def test_a_run_announces_its_commits_and_its_merge_without_git(simulated):
    from journal.events.bus import Bus
    from journal.events.listener import Listener
    from journal.events.moments.git_committed import GitCommitted
    from journal.events.moments.worker_work_merged import WorkerWorkMerged
    from journal.repositories.agents import Agents
    from tests.simulation.main_agent import LINES_PER_WRITE, WRITES_PER_TASK
    from tests.simulation.scenario_run import ScenarioRun
    from tests.simulation.scenarios import CARELESS
    from tests.simulation.scripted_policy import ScriptedPolicy
    from tests.simulation.simulator import MERGED_LINES
    heard: list = []
    hearing = type("Hearing", (Listener,), {"handle": lambda self, event: heard.append(event)})()
    bus = simulated.app.container.get(Bus)
    bus.listen(GitCommitted, hearing)
    bus.listen(WorkerWorkMerged, hearing)
    script = ["dispatch", *["write"] * (2 * (WRITES_PER_TASK + 1)), "idle", "idle", "merge", "merge", "merge"]
    ScenarioRun(simulated, replace(CARELESS, minutes=12, user_messages_hourly=0), SEED, ScriptedPolicy(script)).played()
    shas = {event.sha for event in heard if isinstance(event, GitCommitted)}
    merges = [event for event in heard if isinstance(event, WorkerWorkMerged)]
    assert len(shas) == 2 and simulated.ledger.lines() == 2 * (WRITES_PER_TASK - 1) * LINES_PER_WRITE, "two tasks written are two commits, announced through the shell's recording with no git run"
    assert len(merges) == 1 and merges[0].lines == MERGED_LINES, "and the worker's merge announces its lines once"
    assert sum(count for _, count in simulated.app.container.get(Agents).session_agent("s1").merged_lines) == MERGED_LINES


def test_the_engines_own_moments_replay_from_their_seed(tmp_path, monkeypatch):
    first = played(tmp_path / "first", monkeypatch, replace(ENGINE_MOMENTS, minutes=15), SEED)
    second = played(tmp_path / "second", monkeypatch, replace(ENGINE_MOMENTS, minutes=15), SEED)
    assert any(entry.actor == "engine" for entry in first) and first == second, "compactions, pauses, questions, restarts and approvals replay exactly from one seed"



def test_each_invariant_fires_on_a_planted_bad_trace_and_not_on_a_clean_one():
    from tests.simulation.hold_lifts import HoldLifts
    from tests.simulation.no_contradiction import NoContradiction
    from tests.simulation.no_faults import NoFaults
    from tests.simulation.stack_bounded import StackBounded
    from tests.simulation.stop_releases import StopReleases
    from tests.simulation.trace_entry import TraceEntry
    from tests.simulation.wait_ends import WaitEnds
    from tests.simulation.worker_unlocks import WorkerUnlocks
    from tests.simulation.progress import Progress
    clean = [TraceEntry(30 * n, "agent", "write", False, (), ("idle", "working"), 200) for n in range(1, 40)]
    planted = {
        HoldLifts(): [TraceEntry(30 * n, "agent", "write", True, ("x.y",), ("idle",), 409) for n in range(1, 13)],
        StopReleases(): [TraceEntry(30 * n, "agent", "stop", True, (), ("idle",), 409) for n in range(1, 8)],
        StackBounded(): [TraceEntry(30, "agent", "write", False, (), tuple(f"layer {n}" for n in range(10)), 200)],
        WaitEnds(): [TraceEntry(60 * n, "agent", "read", False, (), ("idle", "external_wait"), 200) for n in range(1, 40)],
        NoContradiction(): [TraceEntry(30, "agent", "write", False, ("workers.orchestrator_hand_out",), ("idle",), 200), TraceEntry(30 + 8 * 60, "agent", "write", False, ("workers.orchestrator_clear_oldest",), ("idle",), 200)],
        NoFaults(): [TraceEntry(30, "agent", "write", False, (), ("idle",), 500)],
        WorkerUnlocks(): [TraceEntry(30, "agent", "read", False, (), ("idle",), 200, 0, ("1:dispatched:locked",))],
        Progress(): [TraceEntry(30 * n, "agent", ("write", "read", "stop")[n % 3], True, (), ("idle",), 409) for n in range(1, 45)],
    }
    for invariant, trace in planted.items():
        assert invariant.violated(trace), f"{type(invariant).__name__} fires on its planted trace"
        assert not invariant.violated(clean), f"{type(invariant).__name__} stays quiet on a clean one"
    apart = [TraceEntry(30, "agent", "write", False, ("workers.orchestrator_hand_out",), ("idle",), 200), TraceEntry(30 + 12 * 60, "agent", "write", False, ("workers.orchestrator_clear_oldest",), ("idle",), 200)]
    assert not NoContradiction().violated(apart), "two opposed lines twelve minutes apart are no contradiction"


@pytest.mark.parametrize("scenario", ALL, ids=lambda scenario: scenario.name)
def test_no_invariant_is_broken_by_a_scenario(tmp_path, monkeypatch, scenario):
    from tests.simulation.invariants import ALL as INVARIANTS
    trace = played(tmp_path / "journal", monkeypatch, scenario, SEED)
    broken = [found for invariant in INVARIANTS if (found := invariant.violated(trace))]
    assert broken == [], f"{scenario.name} from seed {SEED}: " + "; ".join(broken)


class PlantedFault:
    """A fault planted for the search to find: the agent merging right after it dispatched."""

    def violated(self, trace) -> str:
        actions = [entry.action for entry in trace if entry.actor == "agent"]
        return "a merge came right after a dispatch" if any(a == "dispatch" and b == "merge" for a, b in zip(actions, actions[1:])) else ""


def test_random_runs_find_a_planted_fault_shrink_it_and_replay_it_from_its_file(tmp_path, monkeypatch):
    import json
    from tests.simulation.scenarios import CARELESS
    from tests.simulation.scripted_policy import ScriptedPolicy
    from tests.simulation.shrinker import Shrinker
    from tests.simulation.trace_file import TraceFile
    short = replace(CARELESS, minutes=5)
    found = None
    for seed in range(SEED, SEED + 20):
        trace = played(tmp_path / f"search{seed}", monkeypatch, short, seed)
        if PlantedFault().violated(trace):
            found = seed, trace
            break
    assert found, "random runs find the planted fault"
    seed, trace = found
    actions = [entry.action for entry in trace if entry.actor == "agent"]
    replays = iter(range(1000))
    shrunk = Shrinker(lambda script: played(tmp_path / f"shrink{next(replays)}", monkeypatch, short, seed, ScriptedPolicy(script)), PlantedFault()).shrunk(actions)
    assert shrunk == ["dispatch", "merge"], shrunk
    path = TraceFile(tmp_path / "traces").written(short.name, seed, PlantedFault().violated(trace), trace, shrunk)
    stored = json.loads(path.read_text())
    replayed = played(tmp_path / "replayed", monkeypatch, short, stored["seed"], ScriptedPolicy(stored["actions"]))
    assert PlantedFault().violated(replayed), "the shrunk trace replays from its file and still breaks the invariant"


def test_the_lines_said_together_in_every_scenario_are_listed_for_the_contradiction_table(tmp_path, monkeypatch, capsys):
    from itertools import combinations
    pairs = {}
    for scenario in ALL:
        for entry in played(tmp_path / scenario.name.replace(" ", "_"), monkeypatch, replace(scenario, minutes=10), SEED):
            for pair in combinations(sorted(set(entry.nudges)), 2):
                pairs[pair] = pairs.get(pair, 0) + 1
    with capsys.disabled():
        print("\nlines said together in one step, for the contradiction table:")
        for (first, second), count in sorted(pairs.items(), key=lambda item: -item[1]):
            print(f"  {count:3}  {first} + {second}")
    assert isinstance(pairs, dict)


def recorded(folder: Path, monkeypatch, scenario: Scenario, seed: int = SEED) -> tuple[ScenarioRun, list]:
    simulator = fresh(folder / scenario.name.replace(" ", "_"), monkeypatch)
    try:
        with simulator.app.container.get(Scope).environment(MAIN):
            run = ScenarioRun(simulator, replace(scenario, minutes=MINUTES or scenario.minutes), seed, POLICIES[scenario.policy]())
            return run, run.played()
    finally:
        simulator.app.runtime().stop()


def test_the_lines_sent_in_the_long_runs_are_counted_per_key_and_frozen_with_their_class(tmp_path, monkeypatch):
    from collections import Counter
    from tests.nudge_frequency import FREQUENCY_FILE, NudgeFrequency
    runs = []
    for scenario in HISTORY:
        trace = played(tmp_path / scenario.name.replace(" ", "_"), monkeypatch, scenario, SEED)
        runs.append((len(trace), dict(Counter(key for entry in trace for key in entry.nudges))))
    from scripts.nudge_words import registered
    counted = NudgeFrequency.counted(runs, [nudge.key for nudge in registered()])
    if os.environ.get("NUDGE_FREQUENCY_FREEZE") == "1":
        counted.written()
    assert counted.counts == NudgeFrequency.frozen().counts, f"the long runs send lines at other rates than {FREQUENCY_FILE.name} holds: run again with NUDGE_FREQUENCY_FREEZE=1"
