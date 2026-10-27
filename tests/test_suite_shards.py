import importlib.util
from pathlib import Path

from tests.shard_deal import ShardDeal


def suite_script():
    spec = importlib.util.spec_from_file_location("suite", Path(__file__).resolve().parents[1] / "scripts" / "suite.py")
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
