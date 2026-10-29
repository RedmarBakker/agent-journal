import importlib.util
import sys
from pathlib import Path

from tests.shard_deal import ShardDeal


def suite_script(name: str = "suite"):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).resolve().parents[1] / "scripts" / f"{name}.py")
    suite = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(suite)
    return suite


def test_shards_are_dealt_longest_first_so_they_end_together_and_go_round_without_times():
    seconds = {"long": 30.0, "mid": 20.0, "a": 10.0, "b": 10.0, "c": 5.0, "d": 5.0}
    shards = ShardDeal(seconds).shards(["a", "b", "c", "d", "long", "mid", "new"], 2)
    loads = [sum(seconds.get(name, 13.3) for name in shard) for shard in shards]
    assert sorted(name for shard in shards for name in shard) == ["a", "b", "c", "d", "long", "mid", "new"], "every test is in one shard"
    assert abs(loads[0] - loads[1]) <= 13.3, "no shard ends a whole long test after the other"
    assert "long" in shards[0] and "mid" in shards[1], "the longest test starts a shard of its own"
    assert ShardDeal({}).shards(["a", "b", "c"], 2) == [["a", "c"], ["b"]], "with no times the tests go round"


def test_a_run_of_the_simulators_files_runs_at_a_lower_priority_and_any_other_run_as_before():
    suite = suite_script()
    assert suite.scoped_command(["tests/simulation_run.py", "-k", "history"])[:3] == ["nice", "-n", "10"], "a sweep of the simulator runs under nice"
    assert suite.scoped_command(["tests/test_cli.py"])[0] != "nice", "any other run is unchanged"


def test_a_shards_count_never_drops_when_a_printed_line_lands_in_its_line_of_dots(tmp_path):
    suite = suite_script()
    output = tmp_path / "shard.out"
    output.write_text("collected 9 items\n....")
    assert suite.shard_progress(output) == (4, 9)
    output.write_text("collected 9 items\n....no supervisor hosts this journal, so these services are off: sync\n..F  [ 77%]\n")
    assert suite.shard_progress(output) == (7, 9), "the dots before a printed line still count"
    output.write_text("collected 9 items\n.........  [100%]\nE       assert False\nF\n")
    assert suite.shard_progress(output) == (9, 9), "an assertion line of a failure's report is no result"


def test_the_suite_waiting_on_the_commandments_judge_prints_the_judges_own_progress_for_its_card():
    suite = suite_script()
    line = suite.judge_progress("parsing 3/10\rparsing 10/10\nreading 40/120\n")
    assert line == "judging tests/: reading 40/120 [ 33%]", "the judge's latest stage is said with its count and its share"
    assert suite.PERCENT.search(line).group(1) == "33", "in the form the suite's card reads its bar from"
    assert suite.judge_progress("") == "", "a judge that has printed nothing yet adds no line"


def test_a_missing_commandments_plugin_does_not_hold_the_tests_or_change_their_result(tmp_path, monkeypatch, capsys):
    suite = suite_script()
    monkeypatch.setattr(suite, "JUDGE", tmp_path / "missing-commandments-plugin")
    monkeypatch.setattr(suite, "available_bytes", lambda: suite.SHARD_BYTES)
    monkeypatch.setattr(suite, "core_shards", lambda: 1)
    monkeypatch.setattr(suite, "shard_count", lambda _: 1)
    monkeypatch.setattr(suite, "sharded_run", lambda *args: False)

    assert suite.whole_suite() == 0
    output = capsys.readouterr().out
    assert "the test commandments were not run" in output, "the missing judge is stated plainly"
    assert "waiting for the test commandments" not in output, "the suite does not claim to wait on a judge that never started"


def test_the_whole_suite_stops_an_unresponsive_judge_and_finishes_with_a_clear_failure(tmp_path, monkeypatch, capsys):
    suite = suite_script()
    monkeypatch.setattr(suite, "JUDGE", Path(__file__))
    monkeypatch.setattr(suite, "TEST_COMMANDMENTS", [sys.executable, "-c", "import time; time.sleep(60)"])
    monkeypatch.setattr(suite, "JUDGE_TIMEOUT_SECONDS", 0.1)
    judging = suite.commandments_started(tmp_path)
    assert judging is not None, "the test judge started"
    process, _ = judging
    monkeypatch.setattr(suite, "commandments_started", lambda _: judging)
    monkeypatch.setattr(suite, "available_bytes", lambda: suite.SHARD_BYTES)
    monkeypatch.setattr(suite, "core_shards", lambda: 1)
    monkeypatch.setattr(suite, "shard_count", lambda _: 1)
    monkeypatch.setattr(suite, "sharded_run", lambda *args: False)
    try:
        assert suite.whole_suite() == 1, "the suite reports that its judge did not complete"
        assert process.poll() is not None, "the stuck judge process was stopped and reaped"
        assert "the test commandments were not judged" in capsys.readouterr().out
    finally:
        if process.poll() is None:
            suite.stop_judge(process)


def test_a_timed_out_judge_ends_the_suite_card_after_its_await_was_cleared(app, tmp_path, monkeypatch):
    from journal.engine.support.session_agents import SessionAgents
    from journal.features.shell.support.output_log import OutputLog
    from journal.features.shell.support.shell_record import ShellRecord
    from journal.repositories.command_outputs import CommandOutputs
    from journal.repositories.messages import Messages
    from journal.repositories.scope import Scope
    from journal.support.caller import Caller
    from tests.in_process import posted

    caller = Caller.agent("main", "s1", "claude")
    assert posted(app, "/hooks/claude", {"hook_event_name": "SessionStart", "session_id": "s1"}, {"X-Journal-Env": "main"})[0] == 200
    folder = tmp_path / "suite-run"
    folder.mkdir()
    (folder / "parts").write_text("R-\n")
    (folder / "0.part").write_text("pytest -q tests/")
    (folder / "0.out").write_text("")
    outputs = app.container.get(CommandOutputs)
    output = app.container.get(OutputLog).start("suite-run", "pytest -q tests/", folder, caller)
    outputs.save(output.backgrounded(), caller.actor)
    assert app.console().run(["output", "watch", str(output.id), "--reader", "pytest"], caller).code == 0
    assert app.console().run(["await", "the suite run", "--output", str(output.id)], caller).code == 0
    assert app.console().run(["await", "clear"], caller).code == 0
    assert app.container.get(SessionAgents).top("s1").name != "awaiting", "clearing the await leaves no open wait"

    with app.container.get(Scope).environment(1):
        [running] = app.container.get(Messages).with_key(f"watch:{output.id}")
        assert running.data["active"] and running.data["docked"], "the suite output stays docked as running while its judge is still going"

    suite = suite_script("suite_for_output_card")
    monkeypatch.setattr(suite, "JUDGE", Path(__file__))
    monkeypatch.setattr(suite, "TEST_COMMANDMENTS", [sys.executable, "-c", "import time; time.sleep(2)"])
    monkeypatch.setattr(suite, "JUDGE_TIMEOUT_SECONDS", 0.1)
    judging = suite.commandments_started(tmp_path)
    assert judging is not None, "the test judge started"
    process, _ = judging
    monkeypatch.setattr(suite, "commandments_started", lambda _: judging)
    monkeypatch.setattr(suite, "available_bytes", lambda: suite.SHARD_BYTES)
    monkeypatch.setattr(suite, "core_shards", lambda: 1)
    monkeypatch.setattr(suite, "shard_count", lambda _: 1)
    monkeypatch.setattr(suite, "sharded_run", lambda *args: False)
    try:
        assert suite.whole_suite() == 1, "the suite exits after reporting its judge timed out"
        assert process.poll() is not None, "the stuck judge is stopped before the suite output can end"
    finally:
        if process.poll() is None:
            suite.stop_judge(process)

    app.container.get(ShellRecord).ended("suite-run", 1, folder, "", caller)
    app.runtime().deferred.drain()
    with app.container.get(Scope).environment(1):
        [ended] = app.container.get(Messages).with_key(f"watch:{output.id}")
        assert not ended.data["active"], "the shell records the suite output as ended when the judge wait returns"
    assert app.console().run(["output", "undock", str(output.id)], caller).code == 0, "an ended suite card can be taken down"
    with app.container.get(Scope).environment(1):
        [undocked] = app.container.get(Messages).with_key(f"watch:{output.id}")
        assert not undocked.data.get("docked"), "the run card comes down"


def test_the_suite_takes_fewer_shards_when_little_memory_is_free_and_reads_free_memory_on_macos_and_linux():
    suite = suite_script()
    shard = suite.SHARD_BYTES
    assert suite.shard_count(100 * shard) == suite.core_shards(), "with memory to spare the cores decide"
    assert suite.shard_count(3 * shard) == min(3, suite.core_shards()) and suite.shard_count(shard // 2) == 1, "with little free, as many shards as fit, never none"
    vm_stat = "Mach Virtual Memory Statistics: (page size of 16384 bytes)\nPages free:      10.\nPages active:   99.\nPages inactive:  20.\nPages speculative: 2.\n"
    assert suite.vm_stat_available(vm_stat) == 16384 * 32, "macOS: the free, inactive and speculative pages"
    assert suite.meminfo_available("MemTotal:  1000 kB\nMemAvailable:   512 kB\n") == 512 * 1024, "Linux: MemAvailable"
    assert "only 600 MB of memory is free" in suite.memory_line(2, 600 * 2**20), "the run says why it took fewer"


def test_the_tests_a_change_touches_are_its_own_test_files_and_the_quickest_tests_that_ran_its_source_files():
    script = suite_script("affected_tests")
    covered = {"tests/test_a.py::test_slow": ["src/journal/a.py"], "tests/test_a.py::test_quick": ["src/journal/a.py", "src/journal/b.py"], "tests/test_b.py::test_other": ["src/journal/b.py"], "tests/test_c.py::test_c": ["src/journal/a.py"]}
    seconds = {"tests/test_a.py::test_slow": 9.0, "tests/test_a.py::test_quick": 0.1}
    assert script.affected(["src/journal/a.py", "tests/test_c.py"], covered, seconds) == ["tests/test_c.py", "tests/test_a.py::test_quick", "tests/test_a.py::test_slow"], "a changed test file runs whole; the tests that ran a changed source file follow, quickest first, without repeating the test file"
    many = {f"tests/test_a.py::test_{n}": ["src/journal/a.py"] for n in range(100)}
    assert len(script.affected(["src/journal/a.py"], many, {})) == script.MOST_TESTS, "a file every test runs never turns the clock-out into the whole suite"
